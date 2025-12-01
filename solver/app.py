"""
Optimization Solver API
Flask-based REST API for the convex optimization solver
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import traceback
from typing import Dict, Any

from .engine import ConvexSolver, ObjectiveType, solve_from_dict
from . import templates
from . import business_templates
from .validator import analyze_problem, validate_solution

app = Flask(__name__, static_folder='../static', static_url_path='/static')
CORS(app)  # Enable CORS for frontend requests


# =============================================================================
# STATIC FILE SERVING
# =============================================================================

@app.route('/')
def index():
    """Serve the main modern app page"""
    return send_from_directory('..', 'app.html')


@app.route('/retro')
def retro_index():
    """Serve the retro optimizer page"""
    return send_from_directory('..', 'optimizer.html')


@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('..', filename)


# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "message": "Optimization Solver API is running",
        "version": "1.0.0"
    })


@app.route('/api/solve', methods=['POST'])
def solve_problem():
    """
    Solve a custom optimization problem

    Request body:
    {
        "objective_type": "minimize" | "maximize",
        "objective": { expression definition },
        "variables": [ variable definitions ],
        "constraints": [ constraint definitions ]
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        result = solve_from_dict(data)

        return jsonify({
            "status": result.status,
            "optimal_value": result.optimal_value,
            "variables": result.variables,
            "solver_stats": result.solver_stats,
            "problem_type": result.problem_type,
            "is_convex": result.is_convex,
            "dual_values": result.dual_values,
            "message": result.message
        })

    except Exception as e:
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


# =============================================================================
# TEMPLATE ENDPOINTS
# =============================================================================

@app.route('/api/templates', methods=['GET'])
def list_templates():
    """List available problem templates"""
    return jsonify({
        "templates": [
            # Classic OR Templates
            {
                "id": "portfolio",
                "name": "Portfolio Optimization",
                "description": "Markowitz mean-variance portfolio optimization",
                "problem_type": "quadratic",
                "category": "finance",
                "icon": "trending_up"
            },
            {
                "id": "diet",
                "name": "Diet Problem",
                "description": "Minimize cost while meeting nutritional requirements",
                "problem_type": "linear",
                "category": "planning",
                "icon": "restaurant"
            },
            {
                "id": "transportation",
                "name": "Transportation Problem",
                "description": "Minimize shipping costs from sources to destinations",
                "problem_type": "linear",
                "category": "logistics",
                "icon": "local_shipping"
            },
            {
                "id": "resource_allocation",
                "name": "Resource Allocation",
                "description": "Maximize profit given limited resources",
                "problem_type": "linear",
                "category": "planning",
                "icon": "inventory_2"
            },
            {
                "id": "regression",
                "name": "Regularized Regression",
                "description": "Ridge, LASSO, or Elastic Net regression",
                "problem_type": "quadratic",
                "category": "ml",
                "icon": "show_chart"
            },
            {
                "id": "knapsack",
                "name": "Knapsack Problem",
                "description": "Select items to maximize value within weight limit",
                "problem_type": "mixed_integer",
                "category": "planning",
                "icon": "shopping_bag"
            },
            {
                "id": "simple_lp",
                "name": "Simple 2D LP",
                "description": "Two-variable linear program for visualization",
                "problem_type": "linear",
                "category": "education",
                "icon": "school"
            },
            {
                "id": "min_cost_flow",
                "name": "Minimum Cost Flow",
                "description": "Network flow optimization",
                "problem_type": "linear",
                "category": "logistics",
                "icon": "account_tree"
            },
            {
                "id": "assignment",
                "name": "Assignment Problem",
                "description": "Optimally assign workers to tasks (H&L Ch.9)",
                "problem_type": "linear",
                "category": "planning",
                "icon": "assignment_ind"
            },
            # Business Templates
            {
                "id": "pizza_shop",
                "name": "Pizza Shop Optimizer",
                "description": "Optimize menu production, pricing, and ingredients",
                "problem_type": "mixed_integer",
                "category": "business",
                "icon": "local_pizza"
            },
            {
                "id": "staff_scheduling",
                "name": "Staff Scheduling",
                "description": "Minimize labor costs with adequate shift coverage",
                "problem_type": "mixed_integer",
                "category": "business",
                "icon": "groups"
            },
            {
                "id": "inventory_ordering",
                "name": "Inventory Ordering",
                "description": "Optimize order quantities to minimize costs",
                "problem_type": "linear",
                "category": "business",
                "icon": "inventory"
            },
            {
                "id": "pricing",
                "name": "Pricing Optimization",
                "description": "Find optimal prices considering demand elasticity",
                "problem_type": "quadratic",
                "category": "business",
                "icon": "attach_money"
            }
        ],
        "categories": [
            {"id": "business", "name": "Business", "description": "Real-world business optimization"},
            {"id": "finance", "name": "Finance", "description": "Investment and portfolio problems"},
            {"id": "logistics", "name": "Logistics", "description": "Transportation and supply chain"},
            {"id": "planning", "name": "Planning", "description": "Resource and production planning"},
            {"id": "ml", "name": "Machine Learning", "description": "ML and statistical problems"},
            {"id": "education", "name": "Education", "description": "Learning and visualization"}
        ]
    })


@app.route('/api/templates/portfolio', methods=['POST'])
def solve_portfolio():
    """
    Solve portfolio optimization problem

    Request body:
    {
        "expected_returns": [0.12, 0.10, 0.07, 0.03],
        "covariance_matrix": [[...], [...], ...],
        "risk_aversion": 1.0,
        "min_weight": 0.0,
        "max_weight": 1.0,
        "target_return": null
    }
    """
    try:
        data = request.get_json()
        result = templates.portfolio_optimization(
            expected_returns=data['expected_returns'],
            covariance_matrix=data['covariance_matrix'],
            risk_aversion=data.get('risk_aversion', 1.0),
            min_weight=data.get('min_weight', 0.0),
            max_weight=data.get('max_weight', 1.0),
            target_return=data.get('target_return')
        )
        return _format_template_result(result)
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@app.route('/api/templates/diet', methods=['POST'])
def solve_diet():
    """
    Solve diet problem

    Request body:
    {
        "food_costs": [2.0, 1.5, 3.0, ...],
        "food_names": ["Bread", "Milk", "Eggs", ...],
        "nutrients": ["Calories", "Protein", "Fat", ...],
        "nutrient_content": [[...], [...], ...],
        "min_nutrients": [2000, 50, 65, ...],
        "max_nutrients": null,
        "max_servings": null
    }
    """
    try:
        data = request.get_json()
        result = templates.diet_problem(
            food_costs=data['food_costs'],
            food_names=data['food_names'],
            nutrients=data['nutrients'],
            nutrient_content=data['nutrient_content'],
            min_nutrients=data['min_nutrients'],
            max_nutrients=data.get('max_nutrients'),
            max_servings=data.get('max_servings')
        )
        return _format_template_result(result)
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@app.route('/api/templates/transportation', methods=['POST'])
def solve_transportation():
    """
    Solve transportation problem

    Request body:
    {
        "supply": [100, 150, 200],
        "demand": [80, 120, 150, 100],
        "costs": [[...], [...], ...],
        "source_names": ["Factory A", "Factory B", ...],
        "dest_names": ["Store 1", "Store 2", ...]
    }
    """
    try:
        data = request.get_json()
        result = templates.transportation_problem(
            supply=data['supply'],
            demand=data['demand'],
            costs=data['costs'],
            source_names=data.get('source_names'),
            dest_names=data.get('dest_names')
        )
        return _format_template_result(result)
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@app.route('/api/templates/resource_allocation', methods=['POST'])
def solve_resource_allocation():
    """
    Solve resource allocation problem

    Request body:
    {
        "profits": [40, 30, 50],
        "resource_usage": [[2, 1, 3], [1, 2, 2], [3, 2, 1]],
        "resource_limits": [100, 80, 120],
        "product_names": ["A", "B", "C"],
        "resource_names": ["Labor", "Material", "Machine"],
        "min_production": null,
        "max_production": null
    }
    """
    try:
        data = request.get_json()
        result = templates.resource_allocation(
            profits=data['profits'],
            resource_usage=data['resource_usage'],
            resource_limits=data['resource_limits'],
            product_names=data.get('product_names'),
            resource_names=data.get('resource_names'),
            min_production=data.get('min_production'),
            max_production=data.get('max_production')
        )
        return _format_template_result(result)
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@app.route('/api/templates/regression', methods=['POST'])
def solve_regression():
    """
    Solve regularized regression problem

    Request body:
    {
        "X": [[1, 2], [3, 4], ...],
        "y": [1.0, 2.0, ...],
        "regularization": "ridge" | "lasso" | "elastic_net",
        "lambda_param": 1.0,
        "fit_intercept": true
    }
    """
    try:
        data = request.get_json()
        result = templates.regularized_regression(
            X=data['X'],
            y=data['y'],
            regularization=data.get('regularization', 'ridge'),
            lambda_param=data.get('lambda_param', 1.0),
            fit_intercept=data.get('fit_intercept', True)
        )
        return _format_template_result(result)
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@app.route('/api/templates/knapsack', methods=['POST'])
def solve_knapsack():
    """
    Solve knapsack problem

    Request body:
    {
        "values": [60, 100, 120],
        "weights": [10, 20, 30],
        "capacity": 50,
        "item_names": ["Item A", "Item B", "Item C"],
        "max_quantity": null
    }
    """
    try:
        data = request.get_json()
        result = templates.knapsack_problem(
            values=data['values'],
            weights=data['weights'],
            capacity=data['capacity'],
            item_names=data.get('item_names'),
            max_quantity=data.get('max_quantity')
        )
        return _format_template_result(result)
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@app.route('/api/templates/simple_lp', methods=['POST'])
def solve_simple_lp():
    """
    Solve simple 2D linear program

    Request body:
    {
        "c": [3, 2],
        "A": [[1, 1], [2, 1], [1, 2]],
        "b": [4, 5, 4],
        "objective_type": "maximize",
        "bounds": [[0, null], [0, null]]
    }
    """
    try:
        data = request.get_json()
        result = templates.simple_lp_2d(
            c=data['c'],
            A=data['A'],
            b=data['b'],
            objective_type=data.get('objective_type', 'maximize'),
            bounds=data.get('bounds')
        )
        return _format_template_result(result)
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@app.route('/api/templates/min_cost_flow', methods=['POST'])
def solve_min_cost_flow():
    """
    Solve minimum cost flow problem

    Request body:
    {
        "sources": {"S1": 100, "S2": 150},
        "sinks": {"D1": 80, "D2": 120, "D3": 50},
        "arcs": [
            {"from": "S1", "to": "D1", "cost": 2, "capacity": 50},
            ...
        ]
    }
    """
    try:
        data = request.get_json()
        result = templates.min_cost_flow(
            sources=data['sources'],
            sinks=data['sinks'],
            arcs=data['arcs']
        )
        return _format_template_result(result)
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@app.route('/api/templates/assignment', methods=['POST'])
def solve_assignment():
    """
    Solve assignment problem (H&L Chapter 9)

    Request body:
    {
        "costs": [[...], [...], ...],
        "worker_names": ["Alice", "Bob", ...],
        "task_names": ["Task1", "Task2", ...],
        "maximize": false
    }
    """
    try:
        data = request.get_json()
        result = templates.assignment_problem(
            costs=data['costs'],
            worker_names=data.get('worker_names'),
            task_names=data.get('task_names'),
            maximize=data.get('maximize', False)
        )
        return _format_template_result(result)
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


# =============================================================================
# PROBLEM ANALYSIS AND VALIDATION ENDPOINTS
# =============================================================================

@app.route('/api/analyze/<template_id>', methods=['POST'])
def analyze_template(template_id: str):
    """
    Analyze a problem and return clarification questions before solving.

    This endpoint checks:
    - Input validity and completeness
    - Potential issues (unbalanced problems, infeasible constraints)
    - Suggestions for better formulation

    Request body: Same as the template solve endpoint

    Response:
    {
        "can_solve": bool,
        "questions": [
            {
                "id": "question_id",
                "question": "The question text",
                "reason": "Why this is being asked",
                "field": "which_input_field",
                "severity": "error|warning|info",
                "suggestion": "Optional suggestion"
            }
        ],
        "warnings": ["list of warnings"],
        "errors": ["list of errors"]
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        analysis = analyze_problem(template_id, data)
        return jsonify(analysis)

    except Exception as e:
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@app.route('/api/validate/<template_id>', methods=['POST'])
def validate_template_solution(template_id: str):
    """
    Validate a solution after solving.

    This endpoint verifies:
    - All constraints are satisfied
    - Optimal value is correctly computed
    - Solution is feasible and makes sense

    Request body:
    {
        "inputs": { ... original problem inputs ... },
        "solution": { ... the solution returned by solver ... }
    }

    Response:
    {
        "is_valid": bool,
        "checks": [
            {
                "name": "Check name",
                "passed": bool,
                "details": "Description of the check"
            }
        ],
        "warnings": ["list of warnings"],
        "errors": ["list of errors"],
        "suggestions": ["list of suggestions"]
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        inputs = data.get('inputs', {})
        solution = data.get('solution', {})

        validation = validate_solution(template_id, inputs, solution)
        return jsonify(validation)

    except Exception as e:
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@app.route('/api/solve_with_validation/<template_id>', methods=['POST'])
def solve_with_validation(template_id: str):
    """
    Analyze, solve, and validate a problem in one call.

    This endpoint:
    1. Analyzes the problem for issues
    2. Solves if no errors (proceeds with warnings)
    3. Validates the solution

    Response includes analysis, solution, and validation results.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Step 1: Analyze
        analysis = analyze_problem(template_id, data)

        # If errors, return early
        if not analysis['can_solve']:
            return jsonify({
                "phase": "analysis",
                "analysis": analysis,
                "solution": None,
                "validation": None,
                "message": "Problem has errors that must be fixed before solving"
            })

        # Step 2: Solve
        solve_functions = {
            'portfolio': lambda d: templates.portfolio_optimization(
                expected_returns=d['expected_returns'],
                covariance_matrix=d['covariance_matrix'],
                risk_aversion=d.get('risk_aversion', 1.0),
                min_weight=d.get('min_weight', 0.0),
                max_weight=d.get('max_weight', 1.0),
                target_return=d.get('target_return')
            ),
            'diet': lambda d: templates.diet_problem(
                food_costs=d['food_costs'],
                food_names=d['food_names'],
                nutrients=d['nutrients'],
                nutrient_content=d['nutrient_content'],
                min_nutrients=d['min_nutrients'],
                max_nutrients=d.get('max_nutrients'),
                max_servings=d.get('max_servings')
            ),
            'transportation': lambda d: templates.transportation_problem(
                supply=d['supply'],
                demand=d['demand'],
                costs=d['costs'],
                source_names=d.get('source_names'),
                dest_names=d.get('dest_names')
            ),
            'assignment': lambda d: templates.assignment_problem(
                costs=d['costs'],
                worker_names=d.get('worker_names'),
                task_names=d.get('task_names'),
                maximize=d.get('maximize', False)
            ),
            'resource_allocation': lambda d: templates.resource_allocation(
                profits=d['profits'],
                resource_usage=d['resource_usage'],
                resource_limits=d['resource_limits'],
                product_names=d.get('product_names'),
                resource_names=d.get('resource_names'),
                min_production=d.get('min_production'),
                max_production=d.get('max_production')
            ),
        }

        if template_id not in solve_functions:
            return jsonify({"error": f"Template {template_id} not supported for validation"}), 400

        result = solve_functions[template_id](data)

        solution = {
            "status": result.status,
            "optimal_value": result.optimal_value,
            "variables": result.variables,
            "solver_stats": result.solver_stats,
            "problem_type": result.problem_type,
            "is_convex": result.is_convex,
            "interpretation": result.interpretation,
            "message": result.message
        }

        # Step 3: Validate
        validation = validate_solution(template_id, data, solution)

        return jsonify({
            "phase": "completed",
            "analysis": analysis,
            "solution": solution,
            "validation": validation,
            "message": "Problem solved and validated" if validation['is_valid'] else "Solution has validation issues"
        })

    except Exception as e:
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


# =============================================================================
# EXAMPLE DATA ENDPOINTS
# =============================================================================

@app.route('/api/examples/<template_id>', methods=['GET'])
def get_example(template_id: str):
    """Get example data for a template"""
    examples = {
        "portfolio": {
            "expected_returns": [0.12, 0.10, 0.07, 0.03],
            "covariance_matrix": [
                [0.10, 0.03, 0.02, 0.01],
                [0.03, 0.08, 0.02, 0.01],
                [0.02, 0.02, 0.05, 0.01],
                [0.01, 0.01, 0.01, 0.02]
            ],
            "risk_aversion": 2.0,
            "min_weight": 0.0,
            "max_weight": 0.5,
            "asset_names": ["Stocks", "Bonds", "Real Estate", "Cash"]
        },
        "diet": {
            "food_costs": [2.0, 1.5, 3.0, 0.5, 1.0, 2.5],
            "food_names": ["Bread", "Milk", "Eggs", "Rice", "Beans", "Chicken"],
            "nutrients": ["Calories", "Protein (g)", "Fat (g)", "Carbs (g)"],
            "nutrient_content": [
                [250, 8, 2, 50],    # Bread
                [150, 8, 8, 12],   # Milk
                [155, 13, 11, 1],  # Eggs
                [200, 4, 0, 45],   # Rice
                [225, 15, 1, 40],  # Beans
                [335, 25, 15, 0]   # Chicken
            ],
            "min_nutrients": [2000, 50, 40, 200],
            "max_nutrients": [2500, 100, 80, 350],
            "max_servings": [5, 4, 6, 4, 4, 3]
        },
        "transportation": {
            "supply": [100, 150, 200],
            "demand": [80, 120, 150, 100],
            "costs": [
                [8, 6, 10, 9],
                [9, 12, 13, 7],
                [14, 9, 16, 5]
            ],
            "source_names": ["Factory A", "Factory B", "Factory C"],
            "dest_names": ["Store 1", "Store 2", "Store 3", "Store 4"]
        },
        "resource_allocation": {
            "profits": [40, 30, 50, 25],
            "resource_usage": [
                [2, 1, 3, 2],
                [1, 2, 2, 1],
                [3, 2, 1, 2]
            ],
            "resource_limits": [100, 80, 120],
            "product_names": ["Product A", "Product B", "Product C", "Product D"],
            "resource_names": ["Labor (hrs)", "Material (kg)", "Machine (hrs)"]
        },
        "regression": {
            "X": [
                [1, 2], [2, 1], [3, 3], [4, 2], [5, 4],
                [1, 5], [2, 4], [3, 1], [4, 5], [5, 2]
            ],
            "y": [3.1, 2.9, 6.2, 5.8, 9.1, 6.0, 6.1, 3.9, 9.2, 6.8],
            "regularization": "ridge",
            "lambda_param": 0.1,
            "fit_intercept": True
        },
        "knapsack": {
            "values": [60, 100, 120, 80, 50, 90],
            "weights": [10, 20, 30, 15, 8, 25],
            "capacity": 50,
            "item_names": ["Laptop", "Camera", "TV", "Tablet", "Phone", "Console"]
        },
        "simple_lp": {
            "c": [3, 2],
            "A": [[1, 1], [2, 1], [1, 2]],
            "b": [4, 5, 4],
            "objective_type": "maximize",
            "bounds": [[0, None], [0, None]]
        },
        "min_cost_flow": {
            "sources": {"Factory1": 100, "Factory2": 150},
            "sinks": {"Store1": 80, "Store2": 120, "Store3": 50},
            "arcs": [
                {"from": "Factory1", "to": "Store1", "cost": 2, "capacity": 60},
                {"from": "Factory1", "to": "Store2", "cost": 4, "capacity": 50},
                {"from": "Factory1", "to": "Store3", "cost": 3, "capacity": 40},
                {"from": "Factory2", "to": "Store1", "cost": 3, "capacity": 50},
                {"from": "Factory2", "to": "Store2", "cost": 2, "capacity": 80},
                {"from": "Factory2", "to": "Store3", "cost": 5, "capacity": 60}
            ]
        },
        "assignment": {
            "costs": [
                [14, 5, 8, 7],
                [2, 12, 6, 5],
                [7, 8, 3, 9],
                [2, 4, 6, 10]
            ],
            "worker_names": ["Alice", "Bob", "Carol", "Dave"],
            "task_names": ["Project A", "Project B", "Project C", "Project D"],
            "maximize": False
        },
        # Business examples
        "pizza_shop": {
            "products": [
                {"name": "Margherita", "price": 12, "ingredients": {"dough": 1, "sauce": 0.5, "cheese": 0.3}, "demand_estimate": 40},
                {"name": "Pepperoni", "price": 14, "ingredients": {"dough": 1, "sauce": 0.5, "cheese": 0.3, "pepperoni": 0.2}, "demand_estimate": 50},
                {"name": "Veggie", "price": 13, "ingredients": {"dough": 1, "sauce": 0.5, "cheese": 0.2, "vegetables": 0.4}, "demand_estimate": 25},
                {"name": "BBQ Chicken", "price": 16, "ingredients": {"dough": 1, "bbq_sauce": 0.5, "cheese": 0.3, "chicken": 0.3}, "demand_estimate": 35}
            ],
            "ingredient_costs": {"dough": 1.5, "sauce": 2, "cheese": 4, "pepperoni": 6, "vegetables": 2, "bbq_sauce": 3, "chicken": 5},
            "ingredient_inventory": {"dough": 200, "sauce": 80, "cheese": 60, "pepperoni": 30, "vegetables": 40, "bbq_sauce": 40, "chicken": 40},
            "labor_cost_per_item": [2, 2.5, 2.5, 3]
        },
        "staff_scheduling": {
            "shifts": [
                {"name": "Mon AM", "hours": 6},
                {"name": "Mon PM", "hours": 6},
                {"name": "Tue AM", "hours": 6},
                {"name": "Tue PM", "hours": 6},
                {"name": "Wed AM", "hours": 6},
                {"name": "Wed PM", "hours": 6}
            ],
            "staff": [
                {"name": "Alice", "hourly_rate": 15, "availability": [0, 1, 2, 3, 4, 5]},
                {"name": "Bob", "hourly_rate": 14, "availability": [0, 2, 4]},
                {"name": "Carol", "hourly_rate": 16, "availability": [1, 3, 5]},
                {"name": "Dave", "hourly_rate": 13, "availability": [0, 1, 2, 3, 4, 5]}
            ],
            "min_staff_per_shift": [2, 2, 2, 2, 2, 2]
        },
        "inventory_ordering": {
            "items": [
                {"name": "Flour", "unit_cost": 2, "holding_cost": 0.1},
                {"name": "Tomatoes", "unit_cost": 3, "holding_cost": 0.5},
                {"name": "Cheese", "unit_cost": 8, "holding_cost": 0.4},
                {"name": "Pepperoni", "unit_cost": 12, "holding_cost": 0.3}
            ],
            "demand_forecast": [100, 50, 40, 20],
            "current_inventory": [20, 10, 5, 5],
            "storage_capacity": 300,
            "budget": 1000,
            "min_safety_stock": [10, 5, 5, 3]
        },
        "pricing": {
            "products": [
                {"name": "Small Pizza", "base_price": 10},
                {"name": "Medium Pizza", "base_price": 14},
                {"name": "Large Pizza", "base_price": 18}
            ],
            "price_range": [[8, 12], [12, 18], [15, 24]],
            "base_demand": [50, 80, 40],
            "price_elasticity": [1.2, 1.0, 0.8],
            "costs": [4, 6, 8]
        }
    }

    if template_id not in examples:
        return jsonify({"error": f"Unknown template: {template_id}"}), 404

    return jsonify(examples[template_id])


def _format_template_result(result) -> Dict[str, Any]:
    """Format a template result for JSON response"""
    return jsonify({
        "status": result.status,
        "optimal_value": result.optimal_value,
        "variables": result.variables,
        "solver_stats": result.solver_stats,
        "problem_type": result.problem_type,
        "is_convex": result.is_convex,
        "interpretation": result.interpretation,
        "message": result.message
    })


# =============================================================================
# BUSINESS TEMPLATE ENDPOINTS
# =============================================================================

@app.route('/api/templates/pizza_shop', methods=['POST'])
def solve_pizza_shop():
    """Solve pizza shop menu optimization"""
    try:
        data = request.get_json()
        result = business_templates.pizza_shop_menu_optimization(
            products=data['products'],
            ingredient_costs=data['ingredient_costs'],
            ingredient_inventory=data['ingredient_inventory'],
            labor_cost_per_item=data['labor_cost_per_item'],
            max_daily_production=data.get('max_daily_production')
        )
        return _format_template_result(result)
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@app.route('/api/templates/staff_scheduling', methods=['POST'])
def solve_staff_scheduling():
    """Solve staff scheduling problem"""
    try:
        data = request.get_json()
        result = business_templates.staff_scheduling(
            shifts=data['shifts'],
            staff=data['staff'],
            min_staff_per_shift=data['min_staff_per_shift'],
            max_hours_per_week=data.get('max_hours_per_week', 40)
        )
        return _format_template_result(result)
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@app.route('/api/templates/inventory_ordering', methods=['POST'])
def solve_inventory_ordering():
    """Solve inventory ordering problem"""
    try:
        data = request.get_json()
        result = business_templates.inventory_ordering(
            items=data['items'],
            demand_forecast=data['demand_forecast'],
            current_inventory=data['current_inventory'],
            storage_capacity=data['storage_capacity'],
            budget=data['budget'],
            min_safety_stock=data.get('min_safety_stock')
        )
        return _format_template_result(result)
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@app.route('/api/templates/pricing', methods=['POST'])
def solve_pricing():
    """Solve pricing optimization problem"""
    try:
        data = request.get_json()
        result = business_templates.pricing_optimization(
            products=data['products'],
            price_range=data['price_range'],
            base_demand=data['base_demand'],
            price_elasticity=data['price_elasticity'],
            costs=data['costs'],
            capacity=data.get('capacity')
        )
        return _format_template_result(result)
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@app.route('/api/business/analyze_pizza_shop', methods=['POST'])
def analyze_pizza_shop():
    """Comprehensive pizza shop analysis"""
    try:
        data = request.get_json()
        result = business_templates.analyze_pizza_shop(
            menu=data['menu'],
            monthly_fixed_costs=data['monthly_fixed_costs'],
            ingredients=data['ingredients'],
            daily_capacity=data['daily_capacity'],
            days_per_month=data.get('days_per_month', 26)
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


# =============================================================================
# MAIN
# =============================================================================

def run_server(host: str = '0.0.0.0', port: int = 5000, debug: bool = True):
    """Run the Flask development server"""
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_server()
