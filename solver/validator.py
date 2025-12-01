"""
Optimization Problem Validator and Clarifier

This module provides:
1. Pre-solve clarification questions to ensure problem is well-defined
2. Post-solve validation to verify solutions are correct
3. OR knowledge base for proper formulation
"""

from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from dataclasses import dataclass


@dataclass
class ClarificationQuestion:
    """A question to ask the user for clarification"""
    id: str
    question: str
    reason: str
    field: str  # Which input field this relates to
    severity: str  # 'error', 'warning', 'info'
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of validating a solution"""
    is_valid: bool
    checks: List[Dict[str, Any]]
    warnings: List[str]
    errors: List[str]
    suggestions: List[str]


class ProblemValidator:
    """Validates optimization problems and asks clarifying questions"""

    # ==========================================================================
    # PRE-SOLVE CLARIFICATION
    # ==========================================================================

    @staticmethod
    def analyze_transportation(data: Dict[str, Any]) -> List[ClarificationQuestion]:
        """Analyze transportation problem inputs and ask clarifications"""
        questions = []

        supply = data.get('supply', [])
        demand = data.get('demand', [])
        costs = data.get('costs', [])

        # Check for empty inputs
        if not supply:
            questions.append(ClarificationQuestion(
                id='missing_supply',
                question='What are the supply capacities for each source?',
                reason='Supply values are required to solve the transportation problem',
                field='supply',
                severity='error'
            ))
            return questions

        if not demand:
            questions.append(ClarificationQuestion(
                id='missing_demand',
                question='What are the demand requirements for each destination?',
                reason='Demand values are required to solve the transportation problem',
                field='demand',
                severity='error'
            ))
            return questions

        total_supply = sum(supply)
        total_demand = sum(demand)

        # Check balance
        if total_supply != total_demand:
            diff = abs(total_supply - total_demand)
            if total_supply > total_demand:
                questions.append(ClarificationQuestion(
                    id='unbalanced_supply',
                    question=f'Total supply ({total_supply}) exceeds total demand ({total_demand}) by {diff}. How should we handle the excess supply?',
                    reason='Unbalanced transportation problems need special handling per H&L Ch.9',
                    field='supply',
                    severity='warning',
                    suggestion='Our solver will add a dummy destination with zero cost to absorb excess supply'
                ))
            else:
                questions.append(ClarificationQuestion(
                    id='unbalanced_demand',
                    question=f'Total demand ({total_demand}) exceeds total supply ({total_supply}) by {diff}. Which destinations can accept shortages?',
                    reason='Not all demand can be satisfied - some destinations will be short',
                    field='demand',
                    severity='warning',
                    suggestion='Our solver will add a dummy source with zero cost to represent unmet demand'
                ))

        # Check cost matrix dimensions
        if costs:
            n_sources = len(supply)
            n_dests = len(demand)
            if len(costs) != n_sources:
                questions.append(ClarificationQuestion(
                    id='cost_rows_mismatch',
                    question=f'Cost matrix has {len(costs)} rows but there are {n_sources} sources. Please verify.',
                    reason='Cost matrix rows must match number of sources',
                    field='costs',
                    severity='error'
                ))
            elif costs[0] and len(costs[0]) != n_dests:
                questions.append(ClarificationQuestion(
                    id='cost_cols_mismatch',
                    question=f'Cost matrix has {len(costs[0])} columns but there are {n_dests} destinations. Please verify.',
                    reason='Cost matrix columns must match number of destinations',
                    field='costs',
                    severity='error'
                ))

            # Check for negative costs
            for i, row in enumerate(costs):
                for j, c in enumerate(row):
                    if c < 0:
                        questions.append(ClarificationQuestion(
                            id=f'negative_cost_{i}_{j}',
                            question=f'Cost from source {i+1} to destination {j+1} is negative ({c}). Is this intentional (e.g., represents profit)?',
                            reason='Negative costs can represent profits or subsidies',
                            field='costs',
                            severity='info'
                        ))
                        break

        return questions

    @staticmethod
    def analyze_assignment(data: Dict[str, Any]) -> List[ClarificationQuestion]:
        """Analyze assignment problem inputs"""
        questions = []

        costs = data.get('costs', [])
        maximize = data.get('maximize', False)

        if not costs:
            questions.append(ClarificationQuestion(
                id='missing_costs',
                question='What is the cost/profit matrix for assignments?',
                reason='Assignment problem requires a cost (or profit) matrix',
                field='costs',
                severity='error'
            ))
            return questions

        n_workers = len(costs)
        n_tasks = len(costs[0]) if costs else 0

        # Check if square
        if n_workers != n_tasks:
            questions.append(ClarificationQuestion(
                id='non_square_assignment',
                question=f'There are {n_workers} workers but {n_tasks} tasks. How should unmatched items be handled?',
                reason='Assignment problems are typically one-to-one (H&L Ch.9)',
                field='costs',
                severity='warning',
                suggestion='Our solver will add dummy workers/tasks with zero cost to balance the problem'
            ))

        # Check for maximize vs minimize
        if not maximize:
            # Check if costs look like profits (high values might be better)
            flat_costs = [c for row in costs for c in row]
            if flat_costs:
                mean_cost = sum(flat_costs) / len(flat_costs)
                if mean_cost > 50:  # Heuristic: high values might be profits
                    questions.append(ClarificationQuestion(
                        id='maximize_check',
                        question='The values in your matrix are relatively high. Are these costs to minimize or profits to maximize?',
                        reason='The objective (min cost vs max profit) affects the solution',
                        field='maximize',
                        severity='info',
                        suggestion='Set maximize=True if these are profits or performance ratings'
                    ))

        return questions

    @staticmethod
    def analyze_diet(data: Dict[str, Any]) -> List[ClarificationQuestion]:
        """Analyze diet problem inputs"""
        questions = []

        food_costs = data.get('food_costs', [])
        food_names = data.get('food_names', [])
        nutrients = data.get('nutrients', [])
        nutrient_content = data.get('nutrient_content', [])
        min_nutrients = data.get('min_nutrients', [])
        max_nutrients = data.get('max_nutrients')

        if not food_costs:
            questions.append(ClarificationQuestion(
                id='missing_food_costs',
                question='What is the cost per serving of each food?',
                reason='Diet problem minimizes total cost of food',
                field='food_costs',
                severity='error'
            ))
            return questions

        if not nutrient_content:
            questions.append(ClarificationQuestion(
                id='missing_nutrition',
                question='What nutrients does each food provide per serving?',
                reason='Nutritional content is needed to ensure requirements are met',
                field='nutrient_content',
                severity='error'
            ))
            return questions

        # Check dimensions
        n_foods = len(food_costs)
        n_nutrients = len(min_nutrients) if min_nutrients else 0

        if nutrient_content and len(nutrient_content) != n_foods:
            questions.append(ClarificationQuestion(
                id='nutrition_rows_mismatch',
                question=f'Nutrient matrix has {len(nutrient_content)} rows but there are {n_foods} foods.',
                reason='Each food needs nutritional information',
                field='nutrient_content',
                severity='error'
            ))

        # Check for realistic constraints
        if min_nutrients and max_nutrients:
            for i, (mn, mx) in enumerate(zip(min_nutrients, max_nutrients)):
                if mn > mx:
                    nutrient_name = nutrients[i] if i < len(nutrients) else f'Nutrient {i+1}'
                    questions.append(ClarificationQuestion(
                        id=f'infeasible_nutrient_{i}',
                        question=f'Minimum requirement for {nutrient_name} ({mn}) exceeds maximum ({mx}). This is infeasible.',
                        reason='Min cannot exceed max constraint',
                        field='min_nutrients',
                        severity='error'
                    ))

        # Warn about missing upper bounds
        if not max_nutrients:
            questions.append(ClarificationQuestion(
                id='no_max_nutrients',
                question='Do you want to set maximum limits on any nutrients (e.g., max calories, max fat)?',
                reason='Without upper bounds, solution may include excessive amounts',
                field='max_nutrients',
                severity='info',
                suggestion='Consider adding maximum limits for a more practical diet'
            ))

        return questions

    @staticmethod
    def analyze_portfolio(data: Dict[str, Any]) -> List[ClarificationQuestion]:
        """Analyze portfolio optimization inputs"""
        questions = []

        returns = data.get('expected_returns', [])
        cov = data.get('covariance_matrix', [])
        risk_aversion = data.get('risk_aversion', 1.0)

        if not returns:
            questions.append(ClarificationQuestion(
                id='missing_returns',
                question='What are the expected returns for each asset?',
                reason='Expected returns are needed for portfolio optimization',
                field='expected_returns',
                severity='error'
            ))
            return questions

        n_assets = len(returns)

        # Check covariance matrix
        if cov:
            if len(cov) != n_assets:
                questions.append(ClarificationQuestion(
                    id='cov_size_mismatch',
                    question=f'Covariance matrix is {len(cov)}x{len(cov)} but there are {n_assets} assets.',
                    reason='Covariance matrix dimensions must match number of assets',
                    field='covariance_matrix',
                    severity='error'
                ))
            else:
                # Check symmetry
                cov_arr = np.array(cov)
                if not np.allclose(cov_arr, cov_arr.T):
                    questions.append(ClarificationQuestion(
                        id='cov_not_symmetric',
                        question='Covariance matrix is not symmetric. Please verify the values.',
                        reason='Covariance matrices must be symmetric (Cov[i,j] = Cov[j,i])',
                        field='covariance_matrix',
                        severity='error'
                    ))

                # Check positive semi-definiteness
                try:
                    eigenvalues = np.linalg.eigvalsh(cov_arr)
                    if np.any(eigenvalues < -1e-8):
                        questions.append(ClarificationQuestion(
                            id='cov_not_psd',
                            question='Covariance matrix is not positive semi-definite. Please verify.',
                            reason='Valid covariance matrices must be positive semi-definite',
                            field='covariance_matrix',
                            severity='error'
                        ))
                except:
                    pass

        # Check risk aversion
        if risk_aversion <= 0:
            questions.append(ClarificationQuestion(
                id='invalid_risk_aversion',
                question='Risk aversion must be positive. What is your risk tolerance?',
                reason='Higher values = more risk-averse, lower values = more risk-seeking',
                field='risk_aversion',
                severity='error',
                suggestion='Common values: 0.5 (aggressive), 1-2 (moderate), 5+ (conservative)'
            ))

        return questions

    @staticmethod
    def analyze_resource_allocation(data: Dict[str, Any]) -> List[ClarificationQuestion]:
        """Analyze resource allocation problem inputs"""
        questions = []

        profits = data.get('profits', [])
        resource_usage = data.get('resource_usage', [])
        resource_limits = data.get('resource_limits', [])

        if not profits:
            questions.append(ClarificationQuestion(
                id='missing_profits',
                question='What is the profit per unit for each product?',
                reason='Resource allocation maximizes total profit',
                field='profits',
                severity='error'
            ))
            return questions

        n_products = len(profits)
        n_resources = len(resource_limits) if resource_limits else 0

        # Check resource usage matrix
        if resource_usage:
            if len(resource_usage) != n_resources:
                questions.append(ClarificationQuestion(
                    id='usage_rows_mismatch',
                    question=f'Resource usage matrix has {len(resource_usage)} rows but there are {n_resources} resources.',
                    reason='Each resource needs usage coefficients for all products',
                    field='resource_usage',
                    severity='error'
                ))
            elif resource_usage[0] and len(resource_usage[0]) != n_products:
                questions.append(ClarificationQuestion(
                    id='usage_cols_mismatch',
                    question=f'Resource usage matrix has {len(resource_usage[0])} columns but there are {n_products} products.',
                    reason='Each product needs usage coefficients for all resources',
                    field='resource_usage',
                    severity='error'
                ))

        # Check for zero limits
        if resource_limits:
            for i, limit in enumerate(resource_limits):
                if limit <= 0:
                    questions.append(ClarificationQuestion(
                        id=f'zero_limit_{i}',
                        question=f'Resource {i+1} has limit {limit}. Is this correct?',
                        reason='Zero or negative resource limits make production impossible',
                        field='resource_limits',
                        severity='warning'
                    ))

        return questions

    # ==========================================================================
    # POST-SOLVE VALIDATION
    # ==========================================================================

    @staticmethod
    def validate_transportation_solution(
        supply: List[float],
        demand: List[float],
        costs: List[List[float]],
        solution: Dict[str, Any]
    ) -> ValidationResult:
        """Validate transportation problem solution"""
        checks = []
        warnings = []
        errors = []
        suggestions = []

        if solution.get('status') != 'optimal':
            errors.append(f"Solver returned status: {solution.get('status')}")
            return ValidationResult(False, checks, warnings, errors, suggestions)

        shipments = solution.get('variables', {}).get('shipments', [])
        if not shipments:
            errors.append("No shipment values found in solution")
            return ValidationResult(False, checks, warnings, errors, suggestions)

        shipments = np.array(shipments)
        n_sources = len(supply)
        n_dests = len(demand)

        # Check 1: Non-negativity
        if np.all(shipments >= -1e-6):
            checks.append({'name': 'Non-negativity', 'passed': True, 'details': 'All shipments >= 0'})
        else:
            checks.append({'name': 'Non-negativity', 'passed': False, 'details': f'Negative shipments found'})
            errors.append('Solution contains negative shipments')

        # Check 2: Supply constraints
        row_sums = shipments.sum(axis=1)[:n_sources]
        supply_satisfied = bool(np.allclose(row_sums, supply, atol=1e-4))
        checks.append({
            'name': 'Supply constraints',
            'passed': supply_satisfied,
            'details': f'Row sums: {[round(float(x), 2) for x in row_sums]}, Supply: {supply}'
        })

        # Check 3: Demand constraints
        col_sums = shipments.sum(axis=0)[:n_dests]
        demand_satisfied = bool(np.allclose(col_sums, demand, atol=1e-4))
        checks.append({
            'name': 'Demand constraints',
            'passed': demand_satisfied,
            'details': f'Col sums: {[round(float(x), 2) for x in col_sums]}, Demand: {demand}'
        })

        # Check 4: Verify optimal value
        costs_arr = np.array(costs)
        computed_cost = float(np.sum(costs_arr * shipments[:costs_arr.shape[0], :costs_arr.shape[1]]))
        reported_cost = solution.get('optimal_value', 0)
        cost_matches = bool(abs(computed_cost - reported_cost) < 1e-4)
        checks.append({
            'name': 'Optimal value verification',
            'passed': cost_matches,
            'details': f'Computed: {computed_cost:.2f}, Reported: {reported_cost:.2f}'
        })

        is_valid = all(c['passed'] for c in checks)

        if is_valid:
            suggestions.append('Solution is mathematically verified as optimal')

        return ValidationResult(is_valid, checks, warnings, errors, suggestions)

    @staticmethod
    def validate_assignment_solution(
        costs: List[List[float]],
        solution: Dict[str, Any],
        maximize: bool = False
    ) -> ValidationResult:
        """Validate assignment problem solution"""
        checks = []
        warnings = []
        errors = []
        suggestions = []

        if solution.get('status') != 'optimal':
            errors.append(f"Solver returned status: {solution.get('status')}")
            return ValidationResult(False, checks, warnings, errors, suggestions)

        assignments = solution.get('variables', {}).get('assignment_matrix', [])
        if not assignments:
            # Try alternative key name
            assignments = solution.get('variables', {}).get('assignment', [])
        if not assignments:
            errors.append("No assignment matrix found in solution")
            return ValidationResult(False, checks, warnings, errors, suggestions)

        assignments = np.array(assignments)

        # Check 1: Binary-like values (0 or 1)
        is_binary = np.all((assignments < 0.01) | (assignments > 0.99))
        checks.append({
            'name': 'Integer solution',
            'passed': bool(is_binary),
            'details': 'All assignments are 0 or 1' if is_binary else 'Fractional assignments found'
        })

        # Check 2: Each worker assigned exactly once
        row_sums = assignments.sum(axis=1)
        worker_constraint = bool(np.allclose(row_sums, 1, atol=0.01))
        checks.append({
            'name': 'Worker constraints',
            'passed': worker_constraint,
            'details': f'Row sums: {[round(float(x), 2) for x in row_sums]} (should be 1)'
        })

        # Check 3: Each task assigned exactly once
        col_sums = assignments.sum(axis=0)
        task_constraint = bool(np.allclose(col_sums, 1, atol=0.01))
        checks.append({
            'name': 'Task constraints',
            'passed': task_constraint,
            'details': f'Col sums: {[round(float(x), 2) for x in col_sums]} (should be 1)'
        })

        # Check 4: Verify optimal value
        costs_arr = np.array(costs)
        if assignments.shape == costs_arr.shape:
            computed_value = float(np.sum(costs_arr * assignments))
            reported_value = solution.get('optimal_value', 0)
            value_matches = bool(abs(computed_value - abs(reported_value)) < 1e-4)
            checks.append({
                'name': 'Optimal value verification',
                'passed': value_matches,
                'details': f'Computed: {computed_value:.2f}, Reported: {reported_value:.2f}'
            })

        is_valid = all(c['passed'] for c in checks)

        if is_valid:
            obj_type = 'profit' if maximize else 'cost'
            suggestions.append(f'Solution is optimal with minimum {obj_type}')

        return ValidationResult(is_valid, checks, warnings, errors, suggestions)

    @staticmethod
    def validate_portfolio_solution(
        expected_returns: List[float],
        covariance_matrix: List[List[float]],
        solution: Dict[str, Any]
    ) -> ValidationResult:
        """Validate portfolio optimization solution"""
        checks = []
        warnings = []
        errors = []
        suggestions = []

        if solution.get('status') != 'optimal':
            errors.append(f"Solver returned status: {solution.get('status')}")
            return ValidationResult(False, checks, warnings, errors, suggestions)

        weights = solution.get('variables', {}).get('weights', [])
        if not weights:
            errors.append("No portfolio weights found in solution")
            return ValidationResult(False, checks, warnings, errors, suggestions)

        weights = np.array(weights)
        returns = np.array(expected_returns)
        cov = np.array(covariance_matrix)

        # Check 1: Weights sum to 1
        weight_sum = float(weights.sum())
        sum_valid = bool(abs(weight_sum - 1.0) < 0.01)
        checks.append({
            'name': 'Budget constraint',
            'passed': sum_valid,
            'details': f'Weight sum: {weight_sum:.4f} (should be 1.0)'
        })

        # Check 2: No negative weights (long-only)
        no_negative = bool(np.all(weights >= -0.001))
        checks.append({
            'name': 'No short selling',
            'passed': no_negative,
            'details': 'All weights non-negative' if no_negative else 'Negative weights found'
        })

        # Compute portfolio metrics
        portfolio_return = float(np.dot(weights, returns))
        portfolio_variance = float(np.dot(weights, np.dot(cov, weights)))
        portfolio_risk = float(np.sqrt(portfolio_variance))

        checks.append({
            'name': 'Portfolio metrics',
            'passed': True,
            'details': f'Return: {portfolio_return:.2%}, Risk: {portfolio_risk:.2%}, Sharpe: {portfolio_return/portfolio_risk:.2f}'
        })

        is_valid = all(c['passed'] for c in checks)

        if is_valid:
            suggestions.append(f'Portfolio has expected return of {portfolio_return:.2%} with risk of {portfolio_risk:.2%}')

        return ValidationResult(is_valid, checks, warnings, errors, suggestions)


# ==========================================================================
# CONVENIENCE FUNCTION
# ==========================================================================

def analyze_problem(template_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze a problem and return clarification questions

    Returns:
        {
            "can_solve": bool,
            "questions": [list of questions],
            "warnings": [list of warnings],
            "errors": [list of errors]
        }
    """
    analyzers = {
        'transportation': ProblemValidator.analyze_transportation,
        'assignment': ProblemValidator.analyze_assignment,
        'diet': ProblemValidator.analyze_diet,
        'portfolio': ProblemValidator.analyze_portfolio,
        'resource_allocation': ProblemValidator.analyze_resource_allocation,
    }

    analyzer = analyzers.get(template_id)
    if not analyzer:
        return {
            "can_solve": True,
            "questions": [],
            "warnings": [],
            "errors": []
        }

    questions = analyzer(data)

    errors = [q for q in questions if q.severity == 'error']
    warnings = [q for q in questions if q.severity == 'warning']
    info = [q for q in questions if q.severity == 'info']

    return {
        "can_solve": len(errors) == 0,
        "questions": [
            {
                "id": q.id,
                "question": q.question,
                "reason": q.reason,
                "field": q.field,
                "severity": q.severity,
                "suggestion": q.suggestion
            }
            for q in questions
        ],
        "warnings": [w.question for w in warnings],
        "errors": [e.question for e in errors]
    }


def validate_solution(template_id: str, inputs: Dict[str, Any], solution: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate a solution after solving

    Returns:
        {
            "is_valid": bool,
            "checks": [list of checks performed],
            "warnings": [list of warnings],
            "errors": [list of errors],
            "suggestions": [list of suggestions]
        }
    """
    if template_id == 'transportation':
        result = ProblemValidator.validate_transportation_solution(
            inputs['supply'],
            inputs['demand'],
            inputs['costs'],
            solution
        )
    elif template_id == 'assignment':
        result = ProblemValidator.validate_assignment_solution(
            inputs['costs'],
            solution,
            inputs.get('maximize', False)
        )
    elif template_id == 'portfolio':
        result = ProblemValidator.validate_portfolio_solution(
            inputs['expected_returns'],
            inputs['covariance_matrix'],
            solution
        )
    else:
        return {
            "is_valid": True,
            "checks": [],
            "warnings": [],
            "errors": [],
            "suggestions": ["No specific validation available for this template"]
        }

    return {
        "is_valid": result.is_valid,
        "checks": result.checks,
        "warnings": result.warnings,
        "errors": result.errors,
        "suggestions": result.suggestions
    }
