"""
Optimization Problem Templates
Pre-built templates for common optimization problems
"""

import cvxpy as cp
import numpy as np
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from .engine import ConvexSolver, ObjectiveType, OptimizationResult


@dataclass
class TemplateResult(OptimizationResult):
    """Extended result with template-specific interpretations"""
    interpretation: Optional[Dict[str, Any]] = None


# =============================================================================
# PORTFOLIO OPTIMIZATION (Quadratic Programming)
# =============================================================================

def portfolio_optimization(
    expected_returns: List[float],
    covariance_matrix: List[List[float]],
    risk_aversion: float = 1.0,
    min_weight: float = 0.0,
    max_weight: float = 1.0,
    target_return: Optional[float] = None
) -> TemplateResult:
    """
    Markowitz Mean-Variance Portfolio Optimization

    Solves: minimize w'Σw - λ * μ'w
            subject to: sum(w) = 1
                       min_weight <= w <= max_weight
                       (optional) μ'w >= target_return

    Args:
        expected_returns: Expected return for each asset
        covariance_matrix: Covariance matrix of returns
        risk_aversion: Trade-off parameter (higher = more risk averse)
        min_weight: Minimum weight per asset (default 0, no short selling)
        max_weight: Maximum weight per asset
        target_return: Optional minimum target return

    Returns:
        TemplateResult with optimal portfolio weights
    """
    n_assets = len(expected_returns)
    mu = np.array(expected_returns)
    Sigma = np.array(covariance_matrix)

    # Variables
    w = cp.Variable(n_assets, name="weights")

    # Objective: minimize risk - λ * return
    # (equivalent to maximize return - (1/λ) * risk)
    risk = cp.quad_form(w, Sigma)
    ret = mu @ w
    objective = cp.Minimize(risk - risk_aversion * ret)

    # Constraints
    constraints = [
        cp.sum(w) == 1,  # Fully invested
        w >= min_weight,  # Min weight
        w <= max_weight   # Max weight
    ]

    if target_return is not None:
        constraints.append(ret >= target_return)

    # Solve
    problem = cp.Problem(objective, constraints)
    problem.solve()

    # Prepare result
    weights = w.value.tolist() if w.value is not None else None
    portfolio_return = float(mu @ w.value) if w.value is not None else None
    portfolio_risk = float(np.sqrt(w.value @ Sigma @ w.value)) if w.value is not None else None

    interpretation = {
        "portfolio_weights": dict(zip([f"asset_{i}" for i in range(n_assets)], weights)) if weights else None,
        "expected_return": portfolio_return,
        "portfolio_risk": portfolio_risk,
        "sharpe_ratio": portfolio_return / portfolio_risk if portfolio_risk and portfolio_risk > 0 else None
    }

    return TemplateResult(
        status=problem.status,
        optimal_value=problem.value,
        variables={"weights": weights},
        solver_stats={"solver_name": problem.solver_stats.solver_name if problem.solver_stats else "unknown"},
        problem_type="quadratic",
        is_convex=True,
        interpretation=interpretation,
        message="Portfolio optimized successfully" if problem.status == "optimal" else problem.status
    )


# =============================================================================
# DIET PROBLEM (Linear Programming)
# =============================================================================

def diet_problem(
    food_costs: List[float],
    food_names: List[str],
    nutrients: List[str],
    nutrient_content: List[List[float]],
    min_nutrients: List[float],
    max_nutrients: Optional[List[float]] = None,
    max_servings: Optional[List[float]] = None
) -> TemplateResult:
    """
    Classic Diet Problem - Minimize cost while meeting nutritional requirements

    Solves: minimize c'x
            subject to: Ax >= b_min (minimum nutrient requirements)
                       Ax <= b_max (maximum nutrient limits, optional)
                       x >= 0 (non-negative servings)
                       x <= max_servings (optional serving limits)

    Args:
        food_costs: Cost per serving of each food
        food_names: Names of foods
        nutrients: Names of nutrients
        nutrient_content: Matrix [food][nutrient] of nutrient content per serving
        min_nutrients: Minimum required amount of each nutrient
        max_nutrients: Maximum allowed amount of each nutrient (optional)
        max_servings: Maximum servings of each food (optional)

    Returns:
        TemplateResult with optimal food servings
    """
    n_foods = len(food_costs)
    n_nutrients = len(nutrients)

    c = np.array(food_costs)
    A = np.array(nutrient_content)
    b_min = np.array(min_nutrients)

    # Variables
    x = cp.Variable(n_foods, name="servings", nonneg=True)

    # Objective: minimize cost
    objective = cp.Minimize(c @ x)

    # Constraints
    constraints = [A @ x >= b_min]  # Minimum nutrients

    if max_nutrients is not None:
        b_max = np.array(max_nutrients)
        constraints.append(A @ x <= b_max)

    if max_servings is not None:
        constraints.append(x <= np.array(max_servings))

    # Solve
    problem = cp.Problem(objective, constraints)
    problem.solve()

    # Prepare result
    servings = x.value.tolist() if x.value is not None else None
    total_cost = float(c @ x.value) if x.value is not None else None

    # Calculate nutrients obtained
    nutrients_obtained = {}
    if x.value is not None:
        nutrient_amounts = A @ x.value
        for i, nutrient in enumerate(nutrients):
            nutrients_obtained[nutrient] = float(nutrient_amounts[i])

    interpretation = {
        "food_servings": dict(zip(food_names, servings)) if servings else None,
        "total_cost": total_cost,
        "nutrients_obtained": nutrients_obtained,
        "non_zero_foods": [food_names[i] for i, s in enumerate(servings) if s and s > 0.01] if servings else []
    }

    return TemplateResult(
        status=problem.status,
        optimal_value=problem.value,
        variables={"servings": servings},
        solver_stats={"solver_name": problem.solver_stats.solver_name if problem.solver_stats else "unknown"},
        problem_type="linear",
        is_convex=True,
        interpretation=interpretation,
        message="Diet optimized successfully" if problem.status == "optimal" else problem.status
    )


# =============================================================================
# TRANSPORTATION PROBLEM (Linear Programming)
# =============================================================================

def transportation_problem(
    supply: List[float],
    demand: List[float],
    costs: List[List[float]],
    source_names: Optional[List[str]] = None,
    dest_names: Optional[List[str]] = None
) -> TemplateResult:
    """
    Transportation Problem - Minimize shipping costs from sources to destinations

    Solves: minimize sum(c_ij * x_ij)
            subject to: sum_j(x_ij) <= supply_i  (supply constraints)
                       sum_i(x_ij) >= demand_j   (demand constraints)
                       x_ij >= 0

    Args:
        supply: Supply available at each source
        demand: Demand required at each destination
        costs: Cost matrix [source][destination] for shipping
        source_names: Optional names for sources
        dest_names: Optional names for destinations

    Returns:
        TemplateResult with optimal shipping plan
    """
    n_sources = len(supply)
    n_dests = len(demand)

    if source_names is None:
        source_names = [f"Source_{i+1}" for i in range(n_sources)]
    if dest_names is None:
        dest_names = [f"Dest_{j+1}" for j in range(n_dests)]

    C = np.array(costs)
    s = np.array(supply)
    d = np.array(demand)

    # Variables: x[i,j] = amount shipped from source i to dest j
    X = cp.Variable((n_sources, n_dests), name="shipments", nonneg=True)

    # Objective: minimize total shipping cost
    objective = cp.Minimize(cp.sum(cp.multiply(C, X)))

    # Constraints
    constraints = [
        cp.sum(X, axis=1) <= s,  # Supply constraints
        cp.sum(X, axis=0) >= d   # Demand constraints
    ]

    # Solve
    problem = cp.Problem(objective, constraints)
    problem.solve()

    # Prepare result
    shipments = X.value.tolist() if X.value is not None else None
    total_cost = problem.value

    # Build shipping plan interpretation
    shipping_plan = []
    if X.value is not None:
        for i in range(n_sources):
            for j in range(n_dests):
                if X.value[i, j] > 0.01:
                    shipping_plan.append({
                        "from": source_names[i],
                        "to": dest_names[j],
                        "amount": float(X.value[i, j]),
                        "cost": float(C[i, j] * X.value[i, j])
                    })

    interpretation = {
        "shipping_plan": shipping_plan,
        "total_cost": total_cost,
        "supply_used": [float(sum(X.value[i, :])) for i in range(n_sources)] if X.value is not None else None,
        "demand_met": [float(sum(X.value[:, j])) for j in range(n_dests)] if X.value is not None else None
    }

    return TemplateResult(
        status=problem.status,
        optimal_value=problem.value,
        variables={"shipments": shipments},
        solver_stats={"solver_name": problem.solver_stats.solver_name if problem.solver_stats else "unknown"},
        problem_type="linear",
        is_convex=True,
        interpretation=interpretation,
        message="Transportation optimized" if problem.status == "optimal" else problem.status
    )


# =============================================================================
# RESOURCE ALLOCATION (Linear Programming)
# =============================================================================

def resource_allocation(
    profits: List[float],
    resource_usage: List[List[float]],
    resource_limits: List[float],
    product_names: Optional[List[str]] = None,
    resource_names: Optional[List[str]] = None,
    min_production: Optional[List[float]] = None,
    max_production: Optional[List[float]] = None
) -> TemplateResult:
    """
    Resource Allocation Problem - Maximize profit given limited resources

    Solves: maximize p'x
            subject to: Ax <= b (resource constraints)
                       x >= min_production
                       x <= max_production
                       x >= 0

    Args:
        profits: Profit per unit of each product
        resource_usage: Matrix [resource][product] of resource usage per unit
        resource_limits: Available amount of each resource
        product_names: Optional names for products
        resource_names: Optional names for resources
        min_production: Minimum production for each product
        max_production: Maximum production for each product

    Returns:
        TemplateResult with optimal production plan
    """
    n_products = len(profits)
    n_resources = len(resource_limits)

    if product_names is None:
        product_names = [f"Product_{i+1}" for i in range(n_products)]
    if resource_names is None:
        resource_names = [f"Resource_{i+1}" for i in range(n_resources)]

    p = np.array(profits)
    A = np.array(resource_usage)
    b = np.array(resource_limits)

    # Variables
    x = cp.Variable(n_products, name="production", nonneg=True)

    # Objective: maximize profit
    objective = cp.Maximize(p @ x)

    # Constraints
    constraints = [A @ x <= b]  # Resource limits

    if min_production is not None:
        constraints.append(x >= np.array(min_production))
    if max_production is not None:
        constraints.append(x <= np.array(max_production))

    # Solve
    problem = cp.Problem(objective, constraints)
    problem.solve()

    # Prepare result
    production = x.value.tolist() if x.value is not None else None
    total_profit = problem.value

    # Resource utilization
    resource_util = {}
    if x.value is not None:
        usage = A @ x.value
        for i, resource in enumerate(resource_names):
            resource_util[resource] = {
                "used": float(usage[i]),
                "available": float(b[i]),
                "utilization": float(usage[i] / b[i] * 100) if b[i] > 0 else 0
            }

    interpretation = {
        "production_plan": dict(zip(product_names, production)) if production else None,
        "total_profit": total_profit,
        "resource_utilization": resource_util,
        "binding_constraints": [resource_names[i] for i, u in enumerate(A @ x.value)
                               if x.value is not None and abs(u - b[i]) < 0.01] if x.value is not None else []
    }

    return TemplateResult(
        status=problem.status,
        optimal_value=problem.value,
        variables={"production": production},
        solver_stats={"solver_name": problem.solver_stats.solver_name if problem.solver_stats else "unknown"},
        problem_type="linear",
        is_convex=True,
        interpretation=interpretation,
        message="Resources allocated optimally" if problem.status == "optimal" else problem.status
    )


# =============================================================================
# REGRESSION WITH REGULARIZATION (Quadratic/SOCP)
# =============================================================================

def regularized_regression(
    X: List[List[float]],
    y: List[float],
    regularization: str = "ridge",
    lambda_param: float = 1.0,
    fit_intercept: bool = True
) -> TemplateResult:
    """
    Regularized Linear Regression

    Ridge (L2): minimize ||Xw - y||^2 + λ||w||^2
    LASSO (L1): minimize ||Xw - y||^2 + λ||w||_1
    Elastic Net: minimize ||Xw - y||^2 + λ1||w||_1 + λ2||w||^2

    Args:
        X: Feature matrix [n_samples, n_features]
        y: Target vector
        regularization: "ridge", "lasso", or "elastic_net"
        lambda_param: Regularization strength
        fit_intercept: Whether to fit intercept

    Returns:
        TemplateResult with optimal weights
    """
    X_arr = np.array(X)
    y_arr = np.array(y)

    n_samples, n_features = X_arr.shape

    # Add intercept column if needed
    if fit_intercept:
        X_arr = np.hstack([np.ones((n_samples, 1)), X_arr])
        n_features += 1

    # Variables
    w = cp.Variable(n_features, name="weights")

    # Loss: sum of squared errors
    loss = cp.sum_squares(X_arr @ w - y_arr)

    # Regularization
    if regularization == "ridge":
        if fit_intercept:
            reg = lambda_param * cp.sum_squares(w[1:])  # Don't regularize intercept
        else:
            reg = lambda_param * cp.sum_squares(w)
        problem_type = "quadratic"
    elif regularization == "lasso":
        if fit_intercept:
            reg = lambda_param * cp.norm(w[1:], 1)
        else:
            reg = lambda_param * cp.norm(w, 1)
        problem_type = "socp"
    elif regularization == "elastic_net":
        if fit_intercept:
            reg = 0.5 * lambda_param * cp.sum_squares(w[1:]) + 0.5 * lambda_param * cp.norm(w[1:], 1)
        else:
            reg = 0.5 * lambda_param * cp.sum_squares(w) + 0.5 * lambda_param * cp.norm(w, 1)
        problem_type = "socp"
    else:
        reg = 0
        problem_type = "quadratic"

    # Objective
    objective = cp.Minimize(loss + reg)

    # Solve
    problem = cp.Problem(objective, [])
    problem.solve()

    # Prepare result
    weights = w.value.tolist() if w.value is not None else None

    # Calculate predictions and metrics
    if w.value is not None:
        y_pred = X_arr @ w.value
        mse = float(np.mean((y_arr - y_pred) ** 2))
        r2 = float(1 - np.sum((y_arr - y_pred) ** 2) / np.sum((y_arr - np.mean(y_arr)) ** 2))
    else:
        mse = None
        r2 = None

    interpretation = {
        "weights": weights,
        "intercept": weights[0] if weights and fit_intercept else None,
        "coefficients": weights[1:] if weights and fit_intercept else weights,
        "mse": mse,
        "r_squared": r2,
        "regularization_type": regularization,
        "lambda": lambda_param,
        "non_zero_features": sum(1 for w in (weights[1:] if fit_intercept else weights) if abs(w) > 1e-6) if weights else None
    }

    return TemplateResult(
        status=problem.status,
        optimal_value=problem.value,
        variables={"weights": weights},
        solver_stats={"solver_name": problem.solver_stats.solver_name if problem.solver_stats else "unknown"},
        problem_type=problem_type,
        is_convex=True,
        interpretation=interpretation,
        message="Regression fitted successfully" if problem.status == "optimal" else problem.status
    )


# =============================================================================
# KNAPSACK PROBLEM (Mixed Integer LP)
# =============================================================================

def knapsack_problem(
    values: List[float],
    weights: List[float],
    capacity: float,
    item_names: Optional[List[str]] = None,
    max_quantity: Optional[List[int]] = None
) -> TemplateResult:
    """
    0-1 Knapsack Problem (or bounded knapsack with max_quantity)

    Solves: maximize v'x
            subject to: w'x <= capacity
                       x in {0, 1} (or x in {0, 1, ..., max_quantity})

    Args:
        values: Value of each item
        weights: Weight of each item
        capacity: Maximum weight capacity
        item_names: Optional names for items
        max_quantity: Maximum quantity per item (None = 0-1 knapsack)

    Returns:
        TemplateResult with optimal item selection
    """
    n_items = len(values)

    if item_names is None:
        item_names = [f"Item_{i+1}" for i in range(n_items)]

    v = np.array(values)
    w = np.array(weights)

    # Variables (binary or integer)
    if max_quantity is None:
        x = cp.Variable(n_items, name="selection", boolean=True)
    else:
        x = cp.Variable(n_items, name="selection", integer=True)

    # Objective: maximize value
    objective = cp.Maximize(v @ x)

    # Constraints
    constraints = [
        w @ x <= capacity,
        x >= 0
    ]

    if max_quantity is not None:
        constraints.append(x <= np.array(max_quantity))
    else:
        constraints.append(x <= 1)

    # Solve
    problem = cp.Problem(objective, constraints)
    problem.solve(solver=cp.SCIPY if max_quantity is None else None)

    # Prepare result
    selection = x.value.tolist() if x.value is not None else None

    # Build selection interpretation
    selected_items = []
    total_weight = 0
    if x.value is not None:
        for i in range(n_items):
            qty = int(round(x.value[i]))
            if qty > 0:
                selected_items.append({
                    "item": item_names[i],
                    "quantity": qty,
                    "value": float(v[i] * qty),
                    "weight": float(w[i] * qty)
                })
                total_weight += w[i] * qty

    interpretation = {
        "selected_items": selected_items,
        "total_value": problem.value,
        "total_weight": total_weight,
        "capacity_used": float(total_weight / capacity * 100) if capacity > 0 else 0,
        "items_selected": len(selected_items)
    }

    return TemplateResult(
        status=problem.status,
        optimal_value=problem.value,
        variables={"selection": selection},
        solver_stats={"solver_name": problem.solver_stats.solver_name if problem.solver_stats else "unknown"},
        problem_type="mixed_integer",
        is_convex=False,  # Integer constraints make it non-convex
        interpretation=interpretation,
        message="Knapsack optimized" if problem.status == "optimal" else problem.status
    )


# =============================================================================
# SIMPLE 2D LINEAR PROGRAM (for visualization)
# =============================================================================

def simple_lp_2d(
    c: List[float],
    A: List[List[float]],
    b: List[float],
    objective_type: str = "maximize",
    bounds: Optional[List[tuple]] = None
) -> TemplateResult:
    """
    Simple 2D Linear Program (good for visualization)

    Solves: maximize/minimize c'x
            subject to: Ax <= b
                       bounds

    Args:
        c: Objective coefficients [c1, c2]
        A: Constraint matrix
        b: Constraint RHS
        objective_type: "maximize" or "minimize"
        bounds: Optional bounds [(x1_min, x1_max), (x2_min, x2_max)]

    Returns:
        TemplateResult with solution and visualization data
    """
    c_arr = np.array(c)
    A_arr = np.array(A)
    b_arr = np.array(b)

    # Variables
    x = cp.Variable(2, name="x")

    # Objective
    if objective_type == "maximize":
        objective = cp.Maximize(c_arr @ x)
    else:
        objective = cp.Minimize(c_arr @ x)

    # Constraints
    constraints = [A_arr @ x <= b_arr]

    if bounds:
        if bounds[0][0] is not None:
            constraints.append(x[0] >= bounds[0][0])
        if bounds[0][1] is not None:
            constraints.append(x[0] <= bounds[0][1])
        if bounds[1][0] is not None:
            constraints.append(x[1] >= bounds[1][0])
        if bounds[1][1] is not None:
            constraints.append(x[1] <= bounds[1][1])
    else:
        constraints.append(x >= 0)

    # Solve
    problem = cp.Problem(objective, constraints)
    problem.solve()

    # Prepare result
    solution = x.value.tolist() if x.value is not None else None

    interpretation = {
        "x1": solution[0] if solution else None,
        "x2": solution[1] if solution else None,
        "optimal_value": problem.value,
        "objective_type": objective_type,
        "num_constraints": len(A)
    }

    return TemplateResult(
        status=problem.status,
        optimal_value=problem.value,
        variables={"x": solution},
        solver_stats={"solver_name": problem.solver_stats.solver_name if problem.solver_stats else "unknown"},
        problem_type="linear",
        is_convex=True,
        interpretation=interpretation,
        message="LP solved successfully" if problem.status == "optimal" else problem.status
    )


# =============================================================================
# MINIMUM COST FLOW (Network LP)
# =============================================================================

def min_cost_flow(
    sources: Dict[str, float],
    sinks: Dict[str, float],
    arcs: List[Dict[str, Any]]
) -> TemplateResult:
    """
    Minimum Cost Flow Problem

    Args:
        sources: Dict of source nodes with supply amounts
        sinks: Dict of sink nodes with demand amounts
        arcs: List of arcs, each with 'from', 'to', 'cost', 'capacity' (optional)

    Returns:
        TemplateResult with optimal flow
    """
    # Build node and arc lists
    nodes = list(set(sources.keys()) | set(sinks.keys()) |
                 set(a['from'] for a in arcs) | set(a['to'] for a in arcs))
    node_idx = {n: i for i, n in enumerate(nodes)}
    n_nodes = len(nodes)
    n_arcs = len(arcs)

    # Build cost vector and capacity constraints
    costs = np.array([a['cost'] for a in arcs])
    capacities = np.array([a.get('capacity', np.inf) for a in arcs])

    # Build node-arc incidence matrix
    A = np.zeros((n_nodes, n_arcs))
    for j, arc in enumerate(arcs):
        A[node_idx[arc['from']], j] = -1  # Outflow
        A[node_idx[arc['to']], j] = 1     # Inflow

    # Build supply/demand vector
    b = np.zeros(n_nodes)
    for node, supply in sources.items():
        b[node_idx[node]] = -supply  # Supply is negative (outflow)
    for node, demand in sinks.items():
        b[node_idx[node]] = demand   # Demand is positive (inflow)

    # Variables: flow on each arc
    f = cp.Variable(n_arcs, name="flow", nonneg=True)

    # Objective: minimize cost
    objective = cp.Minimize(costs @ f)

    # Constraints
    constraints = [
        A @ f == b,  # Flow conservation
    ]
    # Add capacity constraints only for finite capacities
    for j, cap in enumerate(capacities):
        if cap < np.inf:
            constraints.append(f[j] <= cap)

    # Solve
    problem = cp.Problem(objective, constraints)
    problem.solve()

    # Prepare result
    flows = f.value.tolist() if f.value is not None else None

    # Build flow interpretation
    flow_details = []
    if f.value is not None:
        for j, arc in enumerate(arcs):
            if f.value[j] > 0.01:
                flow_details.append({
                    "from": arc['from'],
                    "to": arc['to'],
                    "flow": float(f.value[j]),
                    "cost": float(costs[j] * f.value[j]),
                    "capacity_used": float(f.value[j] / capacities[j] * 100) if capacities[j] < np.inf else None
                })

    interpretation = {
        "flow_details": flow_details,
        "total_cost": problem.value,
        "total_flow": sum(f.value) if f.value is not None else None
    }

    return TemplateResult(
        status=problem.status,
        optimal_value=problem.value,
        variables={"flows": flows},
        solver_stats={"solver_name": problem.solver_stats.solver_name if problem.solver_stats else "unknown"},
        problem_type="linear",
        is_convex=True,
        interpretation=interpretation,
        message="Min cost flow solved" if problem.status == "optimal" else problem.status
    )
