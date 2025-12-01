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

app = Flask(__name__, static_folder='../static', static_url_path='/static')
CORS(app)  # Enable CORS for frontend requests


# =============================================================================
# STATIC FILE SERVING
# =============================================================================

@app.route('/')
def index():
    """Serve the main optimizer page"""
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
            {
                "id": "portfolio",
                "name": "Portfolio Optimization",
                "description": "Markowitz mean-variance portfolio optimization (QP)",
                "problem_type": "quadratic"
            },
            {
                "id": "diet",
                "name": "Diet Problem",
                "description": "Minimize cost while meeting nutritional requirements (LP)",
                "problem_type": "linear"
            },
            {
                "id": "transportation",
                "name": "Transportation Problem",
                "description": "Minimize shipping costs from sources to destinations (LP)",
                "problem_type": "linear"
            },
            {
                "id": "resource_allocation",
                "name": "Resource Allocation",
                "description": "Maximize profit given limited resources (LP)",
                "problem_type": "linear"
            },
            {
                "id": "regression",
                "name": "Regularized Regression",
                "description": "Ridge, LASSO, or Elastic Net regression (QP/SOCP)",
                "problem_type": "quadratic"
            },
            {
                "id": "knapsack",
                "name": "Knapsack Problem",
                "description": "Select items to maximize value within weight limit (MILP)",
                "problem_type": "mixed_integer"
            },
            {
                "id": "simple_lp",
                "name": "Simple 2D LP",
                "description": "Two-variable linear program for visualization (LP)",
                "problem_type": "linear"
            },
            {
                "id": "min_cost_flow",
                "name": "Minimum Cost Flow",
                "description": "Network flow optimization (LP)",
                "problem_type": "linear"
            }
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
# MAIN
# =============================================================================

def run_server(host: str = '0.0.0.0', port: int = 5000, debug: bool = True):
    """Run the Flask development server"""
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_server()
