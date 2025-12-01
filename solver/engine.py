"""
Optimization Solver Engine
Core solver functionality using CVXPY for convex optimization
"""

import cvxpy as cp
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ProblemType(Enum):
    """Supported optimization problem types"""
    LINEAR = "linear"           # Linear Programming (LP)
    QUADRATIC = "quadratic"     # Quadratic Programming (QP)
    SOCP = "socp"              # Second-Order Cone Programming
    SDP = "sdp"                # Semidefinite Programming
    GEOMETRIC = "geometric"     # Geometric Programming
    MIXED_INTEGER = "milp"      # Mixed Integer Linear Programming


class ObjectiveType(Enum):
    """Optimization objective direction"""
    MINIMIZE = "minimize"
    MAXIMIZE = "maximize"


@dataclass
class Variable:
    """Represents an optimization variable"""
    name: str
    size: int = 1
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    integer: bool = False
    binary: bool = False


@dataclass
class OptimizationResult:
    """Result of an optimization problem"""
    status: str
    optimal_value: Optional[float]
    variables: Dict[str, Any]
    solver_stats: Dict[str, Any]
    problem_type: str
    is_convex: bool
    dual_values: Optional[Dict[str, Any]] = None
    message: str = ""


class ConvexSolver:
    """
    Main solver class using CVXPY for disciplined convex programming
    """

    AVAILABLE_SOLVERS = ['CLARABEL', 'ECOS', 'OSQP', 'SCS', 'SCIPY']

    def __init__(self, solver: Optional[str] = None):
        """
        Initialize solver

        Args:
            solver: Specific solver to use (None for auto-select)
        """
        self.solver = solver
        self._variables = {}
        self._constraints = []
        self._objective = None
        self._problem = None

    def create_variable(self, name: str, shape: Tuple[int, ...] = (1,),
                       nonneg: bool = False, integer: bool = False,
                       boolean: bool = False, symmetric: bool = False,
                       PSD: bool = False) -> cp.Variable:
        """
        Create a CVXPY variable

        Args:
            name: Variable name
            shape: Variable dimensions
            nonneg: Non-negative constraint
            integer: Integer constraint
            boolean: Binary/boolean constraint
            symmetric: Symmetric matrix constraint
            PSD: Positive semidefinite constraint

        Returns:
            CVXPY Variable object
        """
        if len(shape) == 1 and shape[0] == 1:
            var = cp.Variable(name=name, nonneg=nonneg, integer=integer, boolean=boolean)
        elif PSD:
            var = cp.Variable(shape, name=name, PSD=True)
        elif symmetric:
            var = cp.Variable(shape, name=name, symmetric=True)
        else:
            var = cp.Variable(shape, name=name, nonneg=nonneg, integer=integer, boolean=boolean)

        self._variables[name] = var
        return var

    def get_variable(self, name: str) -> Optional[cp.Variable]:
        """Get a variable by name"""
        return self._variables.get(name)

    def add_constraint(self, constraint) -> None:
        """Add a constraint to the problem"""
        self._constraints.append(constraint)

    def set_objective(self, objective_type: ObjectiveType, expression) -> None:
        """
        Set the optimization objective

        Args:
            objective_type: MINIMIZE or MAXIMIZE
            expression: CVXPY expression for objective
        """
        if objective_type == ObjectiveType.MINIMIZE:
            self._objective = cp.Minimize(expression)
        else:
            self._objective = cp.Maximize(expression)

    def solve(self, verbose: bool = False) -> OptimizationResult:
        """
        Solve the optimization problem

        Args:
            verbose: Print solver output

        Returns:
            OptimizationResult with solution details
        """
        if self._objective is None:
            return OptimizationResult(
                status="error",
                optimal_value=None,
                variables={},
                solver_stats={},
                problem_type="unknown",
                is_convex=False,
                message="No objective function set"
            )

        # Create problem
        self._problem = cp.Problem(self._objective, self._constraints)

        # Check if problem is DCP (Disciplined Convex Programming)
        is_convex = self._problem.is_dcp()

        # Determine problem type
        problem_type = self._detect_problem_type()

        # Solve
        try:
            if self.solver:
                self._problem.solve(solver=self.solver, verbose=verbose)
            else:
                self._problem.solve(verbose=verbose)
        except Exception as e:
            return OptimizationResult(
                status="error",
                optimal_value=None,
                variables={},
                solver_stats={},
                problem_type=problem_type,
                is_convex=is_convex,
                message=str(e)
            )

        # Extract results
        var_values = {}
        for name, var in self._variables.items():
            if var.value is not None:
                val = var.value
                if isinstance(val, np.ndarray):
                    if val.size == 1:
                        var_values[name] = float(val.flatten()[0])
                    else:
                        var_values[name] = val.tolist()
                else:
                    var_values[name] = float(val)
            else:
                var_values[name] = None

        # Extract dual values
        dual_values = {}
        for i, constraint in enumerate(self._constraints):
            if constraint.dual_value is not None:
                dual_val = constraint.dual_value
                if isinstance(dual_val, np.ndarray):
                    if dual_val.size == 1:
                        dual_values[f"constraint_{i}"] = float(dual_val.flatten()[0])
                    else:
                        dual_values[f"constraint_{i}"] = dual_val.tolist()
                else:
                    dual_values[f"constraint_{i}"] = float(dual_val)

        # Solver stats
        solver_stats = {
            "solver_name": self._problem.solver_stats.solver_name if self._problem.solver_stats else "unknown",
            "solve_time": self._problem.solver_stats.solve_time if self._problem.solver_stats else None,
            "num_iters": getattr(self._problem.solver_stats, 'num_iters', None) if self._problem.solver_stats else None
        }

        return OptimizationResult(
            status=self._problem.status,
            optimal_value=self._problem.value,
            variables=var_values,
            solver_stats=solver_stats,
            problem_type=problem_type,
            is_convex=is_convex,
            dual_values=dual_values if dual_values else None,
            message="Solution found" if self._problem.status == "optimal" else f"Status: {self._problem.status}"
        )

    def _detect_problem_type(self) -> str:
        """Detect the type of optimization problem"""
        if self._problem is None:
            return "unknown"

        # Check for integer/boolean variables
        has_integer = any(var.attributes.get('integer', False) or var.attributes.get('boolean', False)
                         for var in self._variables.values())
        if has_integer:
            return ProblemType.MIXED_INTEGER.value

        # Check objective and constraints for problem type indicators
        # This is a simplified detection - CVXPY handles the details
        obj_str = str(self._objective) if self._objective else ""

        if "quad_form" in obj_str or "sum_squares" in obj_str:
            return ProblemType.QUADRATIC.value
        elif "norm" in obj_str:
            return ProblemType.SOCP.value
        else:
            return ProblemType.LINEAR.value

    def reset(self) -> None:
        """Reset the solver state"""
        self._variables = {}
        self._constraints = []
        self._objective = None
        self._problem = None


def solve_from_dict(problem_dict: Dict[str, Any]) -> OptimizationResult:
    """
    Solve an optimization problem from a dictionary specification

    Args:
        problem_dict: Dictionary containing problem specification
            - objective_type: "minimize" or "maximize"
            - objective: dict with coefficient and variable info
            - variables: list of variable definitions
            - constraints: list of constraint definitions

    Returns:
        OptimizationResult
    """
    solver = ConvexSolver()

    # Create variables
    variables = {}
    for var_def in problem_dict.get('variables', []):
        name = var_def['name']
        shape = tuple(var_def.get('shape', [1]))
        nonneg = var_def.get('nonneg', False)
        integer = var_def.get('integer', False)
        boolean = var_def.get('boolean', False)

        variables[name] = solver.create_variable(
            name=name, shape=shape, nonneg=nonneg,
            integer=integer, boolean=boolean
        )

    # Build objective expression
    obj_def = problem_dict.get('objective', {})
    obj_expr = _build_expression(obj_def, variables)

    obj_type = ObjectiveType.MINIMIZE if problem_dict.get('objective_type', 'minimize') == 'minimize' else ObjectiveType.MAXIMIZE
    solver.set_objective(obj_type, obj_expr)

    # Add constraints
    for const_def in problem_dict.get('constraints', []):
        const_expr = _build_constraint(const_def, variables)
        if const_expr is not None:
            solver.add_constraint(const_expr)

    return solver.solve()


def _build_expression(expr_def: Dict, variables: Dict[str, cp.Variable]):
    """Build a CVXPY expression from definition"""
    expr_type = expr_def.get('type', 'linear')

    if expr_type == 'linear':
        # Linear combination: sum of coef * var
        terms = expr_def.get('terms', [])
        result = 0
        for term in terms:
            coef = term.get('coefficient', 1)
            var_name = term.get('variable')
            if var_name and var_name in variables:
                result += coef * variables[var_name]
            elif 'constant' in term:
                result += term['constant']
        return result

    elif expr_type == 'quadratic':
        # Quadratic form: x'Qx + c'x
        Q = np.array(expr_def.get('Q', []))
        c = np.array(expr_def.get('c', []))
        var_name = expr_def.get('variable')
        x = variables.get(var_name)
        if x is not None:
            result = 0
            if Q.size > 0:
                result += cp.quad_form(x, Q)
            if c.size > 0:
                result += c @ x
            return result

    elif expr_type == 'norm':
        var_name = expr_def.get('variable')
        norm_type = expr_def.get('norm', 2)
        x = variables.get(var_name)
        if x is not None:
            return cp.norm(x, norm_type)

    elif expr_type == 'sum_squares':
        var_name = expr_def.get('variable')
        x = variables.get(var_name)
        if x is not None:
            return cp.sum_squares(x)

    return 0


def _build_constraint(const_def: Dict, variables: Dict[str, cp.Variable]):
    """Build a CVXPY constraint from definition"""
    const_type = const_def.get('type', '<=')

    # Build left-hand side
    lhs = _build_expression(const_def.get('lhs', {}), variables)

    # Build right-hand side
    rhs_def = const_def.get('rhs', {})
    if isinstance(rhs_def, (int, float)):
        rhs = rhs_def
    else:
        rhs = _build_expression(rhs_def, variables)

    # Create constraint
    if const_type == '<=':
        return lhs <= rhs
    elif const_type == '>=':
        return lhs >= rhs
    elif const_type == '==':
        return lhs == rhs

    return None
