"""
Operations Research Knowledge Base
Based on Hillier & Lieberman "Introduction to Operations Research"

This file encodes correct formulations and methods for optimization problems.
Reference: Hillier & Lieberman, Introduction to Operations Research, 11th Edition
"""

# =============================================================================
# LINEAR PROGRAMMING STANDARD FORMS (H&L Chapter 3-4)
# =============================================================================

LP_STANDARD_FORMS = {
    "maximization": {
        "description": "Standard maximization LP",
        "formulation": """
            maximize    c'x
            subject to  Ax <= b
                       x >= 0
        """,
        "notes": [
            "Objective is to maximize",
            "All constraints are <= (less than or equal)",
            "All variables are non-negative",
            "To convert >= constraint: multiply by -1",
            "To convert = constraint: use two inequalities"
        ]
    },
    "minimization": {
        "description": "Standard minimization LP",
        "formulation": """
            minimize    c'x
            subject to  Ax >= b
                       x >= 0
        """,
        "notes": [
            "Dual of maximization problem",
            "min c'x = -max(-c'x)"
        ]
    }
}

# =============================================================================
# TRANSPORTATION PROBLEM (H&L Chapter 9)
# =============================================================================

TRANSPORTATION_PROBLEM = {
    "description": "Ship goods from m sources to n destinations at minimum cost",
    "formulation": """
        minimize    sum_i sum_j c_ij * x_ij
        subject to  sum_j x_ij <= s_i  for all i (supply constraints)
                   sum_i x_ij >= d_j  for all j (demand constraints)
                   x_ij >= 0          for all i,j
    """,
    "variables": {
        "x_ij": "Amount shipped from source i to destination j",
        "c_ij": "Cost per unit from source i to destination j",
        "s_i": "Supply available at source i",
        "d_j": "Demand at destination j"
    },
    "properties": [
        "Special structure of LP - m+n constraints, mn variables",
        "Always has integer optimal solution if s_i and d_j are integers",
        "Can be solved efficiently with transportation simplex method"
    ],
    "balanced_vs_unbalanced": {
        "balanced": "sum(supply) = sum(demand)",
        "unbalanced_supply_excess": {
            "condition": "sum(supply) > sum(demand)",
            "solution": "Add dummy destination with demand = excess supply, cost = 0"
        },
        "unbalanced_demand_excess": {
            "condition": "sum(supply) < sum(demand)",
            "solution": "Add dummy source with supply = excess demand, cost = 0 (or penalty cost)"
        }
    },
    "solution_methods": [
        "Northwest Corner Method (initial BFS)",
        "Vogel's Approximation Method (better initial BFS)",
        "Stepping Stone Method (optimality test)",
        "MODI Method (Modified Distribution)"
    ]
}

# =============================================================================
# ASSIGNMENT PROBLEM (H&L Chapter 9)
# =============================================================================

ASSIGNMENT_PROBLEM = {
    "description": "Assign n tasks to n workers at minimum cost (one-to-one)",
    "formulation": """
        minimize    sum_i sum_j c_ij * x_ij
        subject to  sum_j x_ij = 1    for all i (each worker assigned once)
                   sum_i x_ij = 1    for all j (each task assigned once)
                   x_ij in {0, 1}    for all i,j
    """,
    "variables": {
        "x_ij": "1 if worker i assigned to task j, 0 otherwise",
        "c_ij": "Cost of assigning worker i to task j"
    },
    "properties": [
        "Special case of transportation problem with all supplies and demands = 1",
        "LP relaxation always has integer optimal solution",
        "Can be solved with Hungarian Method in O(n^3)"
    ],
    "unbalanced": {
        "condition": "Number of workers != number of tasks",
        "solution": "Add dummy workers or tasks with cost = 0"
    },
    "variations": [
        "Maximization: convert to min by subtracting costs from max cost",
        "Multiple assignment: modify constraints for k assignments per worker"
    ]
}

# =============================================================================
# RESOURCE ALLOCATION / PRODUCT MIX (H&L Chapter 3)
# =============================================================================

RESOURCE_ALLOCATION = {
    "description": "Determine production quantities to maximize profit given limited resources",
    "formulation": """
        maximize    sum_j p_j * x_j
        subject to  sum_j a_ij * x_j <= b_i  for all i (resource constraints)
                   x_j >= 0                  for all j
    """,
    "variables": {
        "x_j": "Quantity of product j to produce",
        "p_j": "Profit per unit of product j",
        "a_ij": "Amount of resource i used per unit of product j",
        "b_i": "Available amount of resource i"
    },
    "interpretation": {
        "binding_constraint": "Resource fully utilized (slack = 0)",
        "shadow_price": "Marginal value of additional resource unit",
        "reduced_cost": "Improvement needed for non-basic variable to enter basis"
    }
}

# =============================================================================
# DIET PROBLEM (H&L Chapter 3)
# =============================================================================

DIET_PROBLEM = {
    "description": "Select foods to minimize cost while meeting nutritional requirements",
    "formulation": """
        minimize    sum_j c_j * x_j
        subject to  sum_j a_ij * x_j >= b_i  for all i (minimum nutrients)
                   sum_j a_ij * x_j <= u_i  for all i (maximum nutrients, optional)
                   x_j >= 0                  for all j
    """,
    "variables": {
        "x_j": "Servings of food j",
        "c_j": "Cost per serving of food j",
        "a_ij": "Amount of nutrient i per serving of food j",
        "b_i": "Minimum required amount of nutrient i",
        "u_i": "Maximum allowed amount of nutrient i"
    },
    "history": "Originally formulated by George Stigler (1945), first large LP solved (1947)"
}

# =============================================================================
# KNAPSACK PROBLEM (H&L Chapter 12)
# =============================================================================

KNAPSACK_PROBLEM = {
    "description": "Select items to maximize value within weight capacity",
    "variations": {
        "0-1_knapsack": {
            "formulation": """
                maximize    sum_j v_j * x_j
                subject to  sum_j w_j * x_j <= W
                           x_j in {0, 1}
            """,
            "solution": "Integer Programming (Branch and Bound) or Dynamic Programming"
        },
        "bounded_knapsack": {
            "formulation": """
                maximize    sum_j v_j * x_j
                subject to  sum_j w_j * x_j <= W
                           0 <= x_j <= u_j, x_j integer
            """,
            "solution": "IP or DP with quantity limits"
        },
        "unbounded_knapsack": {
            "formulation": """
                maximize    sum_j v_j * x_j
                subject to  sum_j w_j * x_j <= W
                           x_j >= 0, x_j integer
            """,
            "solution": "Dynamic Programming"
        }
    }
}

# =============================================================================
# NETWORK FLOW PROBLEMS (H&L Chapter 10)
# =============================================================================

NETWORK_FLOW = {
    "minimum_cost_flow": {
        "description": "Send flow through network at minimum cost",
        "formulation": """
            minimize    sum_(i,j) c_ij * x_ij
            subject to  sum_j x_ij - sum_j x_ji = b_i  for all i (flow conservation)
                       0 <= x_ij <= u_ij              for all (i,j)
        """,
        "notes": [
            "b_i > 0 for source nodes (supply)",
            "b_i < 0 for sink nodes (demand)",
            "b_i = 0 for transshipment nodes",
            "Transportation is special case with bipartite network"
        ]
    },
    "shortest_path": {
        "description": "Find shortest path from source to sink",
        "solution": "Special case of min cost flow with unit flow"
    },
    "max_flow": {
        "description": "Maximize flow from source to sink",
        "solution": "Ford-Fulkerson algorithm, min-cut max-flow theorem"
    }
}

# =============================================================================
# DUALITY THEORY (H&L Chapter 6)
# =============================================================================

DUALITY = {
    "primal_dual_relationship": {
        "primal": """
            maximize    c'x
            subject to  Ax <= b
                       x >= 0
        """,
        "dual": """
            minimize    b'y
            subject to  A'y >= c
                       y >= 0
        """
    },
    "key_theorems": {
        "weak_duality": "For any feasible x and y: c'x <= b'y",
        "strong_duality": "At optimality: c'x* = b'y*",
        "complementary_slackness": [
            "If x_j* > 0, then constraint j of dual is tight",
            "If y_i* > 0, then constraint i of primal is tight"
        ]
    },
    "economic_interpretation": {
        "dual_variable": "Shadow price = marginal value of resource",
        "reduced_cost": "Amount objective coefficient must improve for variable to be positive"
    }
}

# =============================================================================
# SENSITIVITY ANALYSIS (H&L Chapter 6-7)
# =============================================================================

SENSITIVITY_ANALYSIS = {
    "description": "How does the optimal solution change with parameter changes?",
    "types": {
        "objective_coefficient": {
            "question": "How much can c_j change before basis changes?",
            "answer": "Allowable increase/decrease range"
        },
        "rhs_constraint": {
            "question": "How much can b_i change before basis changes?",
            "answer": "Allowable increase/decrease range",
            "interpretation": "Shadow price valid within this range"
        },
        "new_variable": {
            "question": "Should we add a new product?",
            "answer": "Add if reduced cost would be positive"
        },
        "new_constraint": {
            "question": "Does adding constraint change solution?",
            "answer": "Only if current optimal violates new constraint"
        }
    }
}

# =============================================================================
# SOLUTION METHODS
# =============================================================================

SOLUTION_METHODS = {
    "simplex": {
        "description": "Standard algorithm for LP",
        "complexity": "Polynomial average case, exponential worst case",
        "steps": [
            "1. Convert to standard form with slack variables",
            "2. Find initial basic feasible solution",
            "3. Check optimality (all reduced costs <= 0 for max)",
            "4. Pivot: select entering and leaving variables",
            "5. Repeat until optimal"
        ]
    },
    "interior_point": {
        "description": "Alternative to simplex, traverses interior",
        "complexity": "Polynomial time",
        "used_by": ["ECOS", "MOSEK", "CLARABEL"]
    },
    "branch_and_bound": {
        "description": "For integer programming",
        "steps": [
            "1. Solve LP relaxation",
            "2. If integer, done. If not, branch on fractional variable",
            "3. Bound: prune if LP bound worse than best integer solution",
            "4. Repeat until all branches explored or pruned"
        ]
    }
}

# =============================================================================
# CONVEXITY (Boyd & Vandenberghe)
# =============================================================================

CONVEXITY = {
    "definition": "A set C is convex if for any x,y in C and 0<=t<=1: tx + (1-t)y in C",
    "convex_function": "f is convex if domain is convex and f(tx+(1-t)y) <= tf(x)+(1-t)f(y)",
    "importance": [
        "Convex problems have no local minima (global optimum guaranteed)",
        "Efficient algorithms exist (polynomial time)",
        "Duality theory is strongest"
    ],
    "problem_types": {
        "LP": "Linear objective, linear constraints - convex",
        "QP": "Quadratic objective (PSD Hessian), linear constraints - convex",
        "SOCP": "Second-order cone constraints - convex",
        "SDP": "Semidefinite constraints - convex",
        "GP": "Geometric programming - can be transformed to convex"
    },
    "DCP_rules": {
        "description": "Disciplined Convex Programming (CVXPY)",
        "rules": [
            "Affine functions are both convex and concave",
            "Max of convex functions is convex",
            "Sum of convex functions is convex",
            "Composition: convex(affine) is convex",
            "Perspective of convex function is convex"
        ]
    }
}
