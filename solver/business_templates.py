"""
Business Optimization Templates
Real-world business optimization problems for shops, restaurants, etc.
"""

import cvxpy as cp
import numpy as np
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from .templates import TemplateResult


# =============================================================================
# PIZZA SHOP OPTIMIZATION
# =============================================================================

def pizza_shop_menu_optimization(
    products: List[Dict[str, Any]],
    ingredient_costs: Dict[str, float],
    ingredient_inventory: Dict[str, float],
    labor_cost_per_item: List[float],
    max_daily_production: Optional[List[int]] = None,
    min_variety: int = 0
) -> TemplateResult:
    """
    Pizza Shop Menu/Production Optimization

    Determines optimal production quantities to maximize profit.

    Args:
        products: List of products with:
            - name: Product name
            - price: Selling price
            - ingredients: Dict of {ingredient: amount_needed}
            - demand_estimate: Expected daily demand
        ingredient_costs: Cost per unit of each ingredient
        ingredient_inventory: Available inventory of each ingredient
        labor_cost_per_item: Labor cost to produce each product
        max_daily_production: Maximum units that can be produced per product
        min_variety: Minimum number of different products to offer

    Returns:
        TemplateResult with optimal production quantities
    """
    n_products = len(products)
    product_names = [p['name'] for p in products]

    # Calculate revenue and costs per product
    revenues = np.array([p['price'] for p in products])
    labor_costs = np.array(labor_cost_per_item)

    # Build ingredient usage matrix
    all_ingredients = list(ingredient_costs.keys())
    n_ingredients = len(all_ingredients)

    ingredient_matrix = np.zeros((n_ingredients, n_products))
    for j, product in enumerate(products):
        for i, ing in enumerate(all_ingredients):
            ingredient_matrix[i, j] = product.get('ingredients', {}).get(ing, 0)

    ingredient_cost_vec = np.array([ingredient_costs[ing] for ing in all_ingredients])
    inventory_limits = np.array([ingredient_inventory.get(ing, float('inf')) for ing in all_ingredients])
    demand_estimates = np.array([p.get('demand_estimate', 100) for p in products])

    # Variables: quantity of each product to make
    x = cp.Variable(n_products, name="production", nonneg=True, integer=True)

    # Revenue minus costs
    # Ingredient cost per product
    ingredient_cost_per_product = ingredient_cost_vec @ ingredient_matrix

    profit_per_item = revenues - ingredient_cost_per_product - labor_costs
    total_profit = profit_per_item @ x

    # Objective: maximize profit
    objective = cp.Maximize(total_profit)

    # Constraints
    constraints = [
        ingredient_matrix @ x <= inventory_limits,  # Ingredient limits
        x <= demand_estimates * 1.2  # Don't overproduce beyond demand
    ]

    if max_daily_production is not None:
        constraints.append(x <= np.array(max_daily_production))

    # Solve
    problem = cp.Problem(objective, constraints)
    problem.solve(solver=cp.SCIPY)

    # Prepare results
    production = x.value.tolist() if x.value is not None else None

    if x.value is not None:
        production_int = [int(round(p)) for p in x.value]
        total_revenue = float(revenues @ x.value)
        total_ingredient_cost = float((ingredient_cost_vec @ ingredient_matrix) @ x.value)
        total_labor_cost = float(labor_costs @ x.value)
        net_profit = float(profit_per_item @ x.value)

        # Ingredient usage
        ingredient_usage = {}
        used = ingredient_matrix @ x.value
        for i, ing in enumerate(all_ingredients):
            ingredient_usage[ing] = {
                "used": float(used[i]),
                "available": float(inventory_limits[i]),
                "remaining": float(inventory_limits[i] - used[i])
            }

        # Per-product breakdown
        product_breakdown = []
        for j, name in enumerate(product_names):
            qty = production_int[j]
            if qty > 0:
                product_breakdown.append({
                    "product": name,
                    "quantity": qty,
                    "revenue": float(revenues[j] * qty),
                    "ingredient_cost": float(ingredient_cost_per_product[j] * qty),
                    "labor_cost": float(labor_costs[j] * qty),
                    "profit": float(profit_per_item[j] * qty)
                })
    else:
        total_revenue = None
        total_ingredient_cost = None
        total_labor_cost = None
        net_profit = None
        ingredient_usage = None
        product_breakdown = None

    interpretation = {
        "production_plan": dict(zip(product_names, production_int)) if production else None,
        "total_revenue": total_revenue,
        "total_ingredient_cost": total_ingredient_cost,
        "total_labor_cost": total_labor_cost,
        "net_profit": net_profit,
        "profit_margin": (net_profit / total_revenue * 100) if total_revenue and total_revenue > 0 else None,
        "ingredient_usage": ingredient_usage,
        "product_breakdown": product_breakdown
    }

    return TemplateResult(
        status=problem.status,
        optimal_value=problem.value,
        variables={"production": production},
        solver_stats={"solver_name": problem.solver_stats.solver_name if problem.solver_stats else "unknown"},
        problem_type="mixed_integer",
        is_convex=False,
        interpretation=interpretation,
        message="Production plan optimized!" if problem.status == "optimal" else problem.status
    )


def staff_scheduling(
    shifts: List[Dict[str, Any]],
    staff: List[Dict[str, Any]],
    min_staff_per_shift: List[int],
    max_hours_per_week: float = 40,
    overtime_multiplier: float = 1.5
) -> TemplateResult:
    """
    Staff Scheduling Optimization

    Minimizes labor cost while ensuring adequate coverage.

    Args:
        shifts: List of shifts with:
            - name: Shift name (e.g., "Monday Morning")
            - hours: Duration in hours
            - min_skill_level: Minimum skill required (optional)
        staff: List of staff members with:
            - name: Staff name
            - hourly_rate: Base hourly wage
            - availability: List of shift indices they can work
            - skill_level: Skill level (optional)
        min_staff_per_shift: Minimum staff required for each shift
        max_hours_per_week: Maximum regular hours per week
        overtime_multiplier: Overtime pay multiplier

    Returns:
        TemplateResult with optimal schedule
    """
    n_shifts = len(shifts)
    n_staff = len(staff)

    shift_hours = np.array([s['hours'] for s in shifts])
    hourly_rates = np.array([s['hourly_rate'] for s in staff])
    min_coverage = np.array(min_staff_per_shift)

    # Build availability matrix
    availability = np.zeros((n_staff, n_shifts))
    for i, person in enumerate(staff):
        for shift_idx in person.get('availability', range(n_shifts)):
            availability[i, shift_idx] = 1

    # Variables: binary assignment matrix
    X = cp.Variable((n_staff, n_shifts), name="schedule", boolean=True)

    # Total hours per staff member
    hours_worked = X @ shift_hours

    # Cost calculation (simplified - regular hours only for convex formulation)
    # Note: For true overtime handling, this would need MILP
    total_cost = cp.sum(cp.multiply(hourly_rates.reshape(-1, 1), X) @ shift_hours.reshape(-1, 1))

    # Objective: minimize cost
    objective = cp.Minimize(total_cost)

    # Constraints
    constraints = [
        cp.multiply(X, availability) == X,  # Respect availability
        cp.sum(X, axis=0) >= min_coverage,  # Minimum coverage
        hours_worked <= max_hours_per_week   # Max hours
    ]

    # Solve
    problem = cp.Problem(objective, constraints)
    problem.solve(solver=cp.SCIPY)

    # Prepare results
    schedule = X.value.tolist() if X.value is not None else None

    if X.value is not None:
        schedule_rounded = np.round(X.value).astype(int)

        # Build schedule interpretation
        staff_schedules = {}
        for i, person in enumerate(staff):
            assigned_shifts = [shifts[j]['name'] for j in range(n_shifts) if schedule_rounded[i, j] > 0]
            total_hours = sum(shifts[j]['hours'] for j in range(n_shifts) if schedule_rounded[i, j] > 0)
            staff_schedules[person['name']] = {
                "shifts": assigned_shifts,
                "total_hours": total_hours,
                "cost": total_hours * person['hourly_rate']
            }

        # Shift coverage
        coverage = {}
        for j, shift in enumerate(shifts):
            assigned = [staff[i]['name'] for i in range(n_staff) if schedule_rounded[i, j] > 0]
            coverage[shift['name']] = {
                "assigned_staff": assigned,
                "count": len(assigned),
                "required": min_coverage[j]
            }

        total_labor_cost = sum(s['cost'] for s in staff_schedules.values())
    else:
        staff_schedules = None
        coverage = None
        total_labor_cost = None

    interpretation = {
        "staff_schedules": staff_schedules,
        "shift_coverage": coverage,
        "total_labor_cost": total_labor_cost,
        "total_staff_used": sum(1 for s in (staff_schedules or {}).values() if s['shifts']) if staff_schedules else None
    }

    return TemplateResult(
        status=problem.status,
        optimal_value=problem.value,
        variables={"schedule": schedule},
        solver_stats={"solver_name": problem.solver_stats.solver_name if problem.solver_stats else "unknown"},
        problem_type="mixed_integer",
        is_convex=False,
        interpretation=interpretation,
        message="Schedule optimized!" if problem.status == "optimal" else problem.status
    )


def inventory_ordering(
    items: List[Dict[str, Any]],
    demand_forecast: List[float],
    current_inventory: List[float],
    storage_capacity: float,
    budget: float,
    min_safety_stock: Optional[List[float]] = None
) -> TemplateResult:
    """
    Inventory Ordering Optimization

    Determines optimal order quantities to minimize costs while meeting demand.

    Args:
        items: List of items with:
            - name: Item name
            - unit_cost: Cost per unit
            - holding_cost: Cost to hold one unit per period
            - order_cost: Fixed cost to place an order (optional)
            - shelf_life: Days until expiration (optional)
            - min_order: Minimum order quantity (optional)
        demand_forecast: Expected demand for each item
        current_inventory: Current stock of each item
        storage_capacity: Total storage capacity
        budget: Maximum budget for ordering
        min_safety_stock: Minimum safety stock for each item

    Returns:
        TemplateResult with optimal order quantities
    """
    n_items = len(items)
    item_names = [item['name'] for item in items]

    unit_costs = np.array([item['unit_cost'] for item in items])
    holding_costs = np.array([item.get('holding_cost', 0.1 * item['unit_cost']) for item in items])
    current_inv = np.array(current_inventory)
    demand = np.array(demand_forecast)

    safety_stock = np.array(min_safety_stock) if min_safety_stock else np.zeros(n_items)

    # Variables: order quantity for each item
    order = cp.Variable(n_items, name="order_quantity", nonneg=True)

    # New inventory = current + ordered
    new_inventory = current_inv + order

    # Costs
    ordering_cost = unit_costs @ order
    expected_holding = holding_costs @ cp.pos(new_inventory - demand)  # Expected leftover

    total_cost = ordering_cost + expected_holding

    # Objective: minimize cost
    objective = cp.Minimize(total_cost)

    # Constraints
    constraints = [
        new_inventory >= demand + safety_stock,  # Meet demand + safety stock
        cp.sum(new_inventory) <= storage_capacity,  # Storage limit
        ordering_cost <= budget  # Budget constraint
    ]

    # Solve
    problem = cp.Problem(objective, constraints)
    problem.solve()

    # Prepare results
    orders = order.value.tolist() if order.value is not None else None

    if order.value is not None:
        order_plan = {}
        total_order_cost = 0
        for i, name in enumerate(item_names):
            qty = float(order.value[i])
            cost = qty * unit_costs[i]
            order_plan[name] = {
                "order_quantity": round(qty, 1),
                "cost": round(cost, 2),
                "new_inventory": round(current_inv[i] + qty, 1),
                "expected_demand": demand[i],
                "safety_buffer": round(current_inv[i] + qty - demand[i], 1)
            }
            total_order_cost += cost

        budget_usage = total_order_cost / budget * 100 if budget > 0 else 0
    else:
        order_plan = None
        total_order_cost = None
        budget_usage = None

    interpretation = {
        "order_plan": order_plan,
        "total_order_cost": total_order_cost,
        "budget_usage_percent": budget_usage,
        "budget_remaining": budget - total_order_cost if total_order_cost else None
    }

    return TemplateResult(
        status=problem.status,
        optimal_value=problem.value,
        variables={"orders": orders},
        solver_stats={"solver_name": problem.solver_stats.solver_name if problem.solver_stats else "unknown"},
        problem_type="linear",
        is_convex=True,
        interpretation=interpretation,
        message="Order plan optimized!" if problem.status == "optimal" else problem.status
    )


def pricing_optimization(
    products: List[Dict[str, Any]],
    price_range: List[tuple],
    base_demand: List[float],
    price_elasticity: List[float],
    costs: List[float],
    capacity: Optional[float] = None
) -> TemplateResult:
    """
    Pricing Optimization

    Finds optimal prices to maximize profit considering demand elasticity.

    Demand model: Q = base_demand * (1 - elasticity * (price - base_price) / base_price)

    Note: This is a simplified model. For convexity, we use a quadratic approximation.

    Args:
        products: List of products with:
            - name: Product name
            - base_price: Current/reference price
        price_range: (min_price, max_price) for each product
        base_demand: Base demand at base price
        price_elasticity: Price elasticity of demand (positive number)
        costs: Variable cost per unit
        capacity: Optional total capacity constraint

    Returns:
        TemplateResult with optimal prices
    """
    n_products = len(products)
    product_names = [p['name'] for p in products]

    base_prices = np.array([p['base_price'] for p in products])
    base_dem = np.array(base_demand)
    elasticity = np.array(price_elasticity)
    var_costs = np.array(costs)

    min_prices = np.array([pr[0] for pr in price_range])
    max_prices = np.array([pr[1] for pr in price_range])

    # Variables: price for each product
    p = cp.Variable(n_products, name="prices")

    # Demand model (linearized for tractability)
    # Q(p) ≈ base_demand - elasticity * base_demand / base_price * (p - base_price)
    # Q(p) = base_demand * (1 - elasticity * (p - base_price) / base_price)
    # Q(p) = base_demand + base_demand * elasticity - elasticity * base_demand / base_price * p

    # For convex profit maximization, we need: profit = p * Q(p) - cost * Q(p)
    # This gives a quadratic in p (concave for maximization if elasticity > 0)

    sensitivity = elasticity * base_dem / base_prices
    # Q = base_dem + base_dem * elasticity - sensitivity * p
    # But this gives demand increasing with elasticity, let's fix:
    # Q = base_dem * (1 + elasticity - elasticity * p / base_price)
    # At p = base_price: Q = base_dem
    # At p > base_price: Q < base_dem (if elasticity > 0)

    # Simplified: Q = base_dem - sensitivity * (p - base_prices)
    # = base_dem + sensitivity * base_prices - sensitivity * p

    intercept = base_dem + sensitivity * base_prices
    Q = intercept - cp.multiply(sensitivity, p)

    # Profit = (price - cost) * quantity
    # For each product: (p_i - c_i) * Q_i
    # = (p_i - c_i) * (intercept_i - sensitivity_i * p_i)
    # = intercept_i * p_i - sensitivity_i * p_i^2 - c_i * intercept_i + c_i * sensitivity_i * p_i
    # = -sensitivity_i * p_i^2 + (intercept_i + c_i * sensitivity_i) * p_i - c_i * intercept_i

    # This is a concave quadratic in p, so we can maximize it

    profit = cp.sum(cp.multiply(p - var_costs, Q))

    # Objective: maximize profit
    objective = cp.Maximize(profit)

    # Constraints
    constraints = [
        p >= min_prices,
        p <= max_prices,
        Q >= 0  # Demand must be non-negative
    ]

    if capacity is not None:
        constraints.append(cp.sum(Q) <= capacity)

    # Solve
    problem = cp.Problem(objective, constraints)
    problem.solve()

    # Prepare results
    prices = p.value.tolist() if p.value is not None else None

    if p.value is not None:
        optimal_prices = p.value
        demands = (intercept - sensitivity * optimal_prices)

        pricing_plan = {}
        total_revenue = 0
        total_cost = 0
        total_quantity = 0

        for i, name in enumerate(product_names):
            price_val = float(optimal_prices[i])
            demand_val = max(0, float(demands[i]))
            revenue = price_val * demand_val
            cost = var_costs[i] * demand_val
            profit_i = revenue - cost

            pricing_plan[name] = {
                "optimal_price": round(price_val, 2),
                "base_price": base_prices[i],
                "price_change_percent": round((price_val - base_prices[i]) / base_prices[i] * 100, 1),
                "expected_demand": round(demand_val, 0),
                "base_demand": base_dem[i],
                "revenue": round(revenue, 2),
                "profit": round(profit_i, 2)
            }

            total_revenue += revenue
            total_cost += cost
            total_quantity += demand_val

        total_profit = total_revenue - total_cost
    else:
        pricing_plan = None
        total_revenue = None
        total_cost = None
        total_profit = None
        total_quantity = None

    interpretation = {
        "pricing_plan": pricing_plan,
        "total_revenue": total_revenue,
        "total_cost": total_cost,
        "total_profit": total_profit,
        "total_quantity": total_quantity,
        "profit_margin_percent": (total_profit / total_revenue * 100) if total_revenue and total_revenue > 0 else None
    }

    return TemplateResult(
        status=problem.status,
        optimal_value=problem.value,
        variables={"prices": prices},
        solver_stats={"solver_name": problem.solver_stats.solver_name if problem.solver_stats else "unknown"},
        problem_type="quadratic",
        is_convex=True,  # Concave objective (maximization)
        interpretation=interpretation,
        message="Prices optimized!" if problem.status == "optimal" else problem.status
    )


def break_even_analysis(
    fixed_costs: float,
    variable_cost_per_unit: float,
    selling_price: float,
    max_capacity: Optional[float] = None
) -> Dict[str, Any]:
    """
    Break-Even Analysis (not optimization, but useful business tool)

    Args:
        fixed_costs: Total fixed costs per period
        variable_cost_per_unit: Variable cost per unit
        selling_price: Selling price per unit
        max_capacity: Maximum production capacity

    Returns:
        Break-even analysis results
    """
    if selling_price <= variable_cost_per_unit:
        return {
            "error": "Selling price must be greater than variable cost",
            "contribution_margin": selling_price - variable_cost_per_unit
        }

    contribution_margin = selling_price - variable_cost_per_unit
    break_even_units = fixed_costs / contribution_margin
    break_even_revenue = break_even_units * selling_price

    results = {
        "break_even_units": round(break_even_units, 2),
        "break_even_revenue": round(break_even_revenue, 2),
        "contribution_margin": round(contribution_margin, 2),
        "contribution_margin_ratio": round(contribution_margin / selling_price * 100, 2)
    }

    if max_capacity:
        results["capacity_utilization_at_break_even"] = round(break_even_units / max_capacity * 100, 2)
        max_profit = (max_capacity * selling_price) - (fixed_costs + max_capacity * variable_cost_per_unit)
        results["max_profit_at_capacity"] = round(max_profit, 2)
        results["safety_margin_units"] = round(max_capacity - break_even_units, 2)

    return results


# =============================================================================
# BUSINESS SCENARIO ANALYZER
# =============================================================================

def analyze_pizza_shop(
    menu: List[Dict[str, Any]],
    monthly_fixed_costs: float,
    ingredients: Dict[str, Dict[str, float]],
    daily_capacity: int,
    days_per_month: int = 26
) -> Dict[str, Any]:
    """
    Comprehensive Pizza Shop Analysis

    Analyzes a pizza shop and provides optimization recommendations.

    Args:
        menu: List of menu items with:
            - name: Item name
            - price: Selling price
            - ingredients: Dict of {ingredient: amount_needed}
            - prep_time_minutes: Time to prepare
            - daily_sales_estimate: Estimated daily sales
        monthly_fixed_costs: Fixed costs (rent, utilities, salaries, etc.)
        ingredients: Dict of ingredients with:
            - cost_per_unit: Cost per unit
            - storage_days: Shelf life
        daily_capacity: Maximum items per day
        days_per_month: Operating days per month

    Returns:
        Comprehensive analysis with recommendations
    """
    n_items = len(menu)

    # Calculate costs and profits per item
    item_analysis = []
    for item in menu:
        ingredient_cost = 0
        for ing_name, amount in item.get('ingredients', {}).items():
            if ing_name in ingredients:
                ingredient_cost += amount * ingredients[ing_name]['cost_per_unit']

        profit = item['price'] - ingredient_cost
        margin = profit / item['price'] * 100 if item['price'] > 0 else 0

        item_analysis.append({
            "name": item['name'],
            "price": item['price'],
            "ingredient_cost": round(ingredient_cost, 2),
            "profit_per_unit": round(profit, 2),
            "margin_percent": round(margin, 1),
            "daily_sales": item.get('daily_sales_estimate', 0),
            "daily_revenue": item['price'] * item.get('daily_sales_estimate', 0),
            "daily_profit": profit * item.get('daily_sales_estimate', 0)
        })

    # Sort by profitability
    item_analysis.sort(key=lambda x: x['profit_per_unit'], reverse=True)

    # Calculate totals
    total_daily_revenue = sum(i['daily_revenue'] for i in item_analysis)
    total_daily_profit = sum(i['daily_profit'] for i in item_analysis)
    total_daily_items = sum(i['daily_sales'] for i in item_analysis)

    monthly_revenue = total_daily_revenue * days_per_month
    monthly_variable_profit = total_daily_profit * days_per_month
    monthly_net_profit = monthly_variable_profit - monthly_fixed_costs

    # Break-even analysis
    avg_margin = total_daily_profit / total_daily_items if total_daily_items > 0 else 0
    break_even_items = monthly_fixed_costs / avg_margin if avg_margin > 0 else float('inf')
    break_even_days = break_even_items / (total_daily_items if total_daily_items > 0 else 1)

    # Recommendations
    recommendations = []

    # High margin items
    high_margin_items = [i for i in item_analysis if i['margin_percent'] > 50]
    low_margin_items = [i for i in item_analysis if i['margin_percent'] < 30]

    if high_margin_items:
        recommendations.append({
            "type": "promote",
            "message": f"Promote high-margin items: {', '.join(i['name'] for i in high_margin_items[:3])}",
            "impact": "Could increase profits by 10-20%"
        })

    if low_margin_items:
        recommendations.append({
            "type": "review",
            "message": f"Review low-margin items: {', '.join(i['name'] for i in low_margin_items[:3])}",
            "impact": "Consider raising prices or reducing costs"
        })

    # Capacity utilization
    capacity_util = total_daily_items / daily_capacity * 100 if daily_capacity > 0 else 0
    if capacity_util < 60:
        recommendations.append({
            "type": "marketing",
            "message": f"Capacity utilization is only {capacity_util:.0f}%. Consider marketing to increase volume.",
            "impact": f"Potential to serve {int(daily_capacity - total_daily_items)} more items daily"
        })
    elif capacity_util > 90:
        recommendations.append({
            "type": "capacity",
            "message": f"Near capacity ({capacity_util:.0f}%). Consider expanding or optimizing operations.",
            "impact": "May be missing sales opportunities"
        })

    # Profitability check
    if monthly_net_profit < 0:
        deficit = abs(monthly_net_profit)
        recommendations.append({
            "type": "urgent",
            "message": f"Currently operating at a loss of ${deficit:.2f}/month",
            "impact": f"Need to increase revenue by ${deficit:.2f} or cut costs"
        })

    return {
        "item_analysis": item_analysis,
        "summary": {
            "total_daily_revenue": round(total_daily_revenue, 2),
            "total_daily_profit": round(total_daily_profit, 2),
            "monthly_revenue": round(monthly_revenue, 2),
            "monthly_fixed_costs": monthly_fixed_costs,
            "monthly_net_profit": round(monthly_net_profit, 2),
            "profit_margin_percent": round(monthly_net_profit / monthly_revenue * 100, 1) if monthly_revenue > 0 else 0,
            "capacity_utilization_percent": round(capacity_util, 1),
            "break_even_items_monthly": round(break_even_items, 0),
            "break_even_days": round(break_even_days, 1)
        },
        "recommendations": recommendations,
        "most_profitable_items": [i['name'] for i in item_analysis[:3]],
        "least_profitable_items": [i['name'] for i in item_analysis[-3:]]
    }
