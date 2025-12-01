# Convex Optimizer 2000

A nostalgic retro 2000s-styled web application for solving convex optimization problems, powered by CVXPY.

```
   _____ _______      _______ _   _  _____
  / ____/ __ \ \    / /_   _| \ | |/ ____|
 | |   | |  | \ \  / /  | | |  \| | |  __
 | |   | |  | |\ \/ /   | | | . ` | | |_ |
 | |___| |__| | \  /   _| |_| |\  | |__| |
  \_____\____/   \/   |_____|_| \_|\_____|

           OPTIMIZER 2000
```

## Features

### Optimization Capabilities

- **Linear Programming (LP)** - Diet problem, transportation, resource allocation
- **Quadratic Programming (QP)** - Portfolio optimization, regularized regression
- **Second-Order Cone Programming (SOCP)** - LASSO regression, robust optimization
- **Semidefinite Programming (SDP)** - Available through custom API
- **Mixed Integer LP (MILP)** - Knapsack problem, scheduling

### Problem Templates

| Template | Type | Description |
|----------|------|-------------|
| Portfolio Optimization | QP | Markowitz mean-variance optimization |
| Diet Problem | LP | Minimize cost, meet nutritional requirements |
| Transportation | LP | Minimize shipping costs from sources to destinations |
| Resource Allocation | LP | Maximize profit given limited resources |
| Regression | QP/SOCP | Ridge, LASSO, Elastic Net |
| Knapsack | MILP | Select items within weight capacity |
| Simple 2D LP | LP | Two-variable LP for learning |
| Min Cost Flow | LP | Network flow optimization |

### Powered By

- **CVXPY** - Disciplined Convex Programming framework
- **CLARABEL** - Modern interior-point solver
- **ECOS** - Embedded Conic Solver
- **OSQP** - Operator Splitting QP Solver
- **SCS** - Splitting Conic Solver

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd retro2000

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Server

```bash
# Start the Flask server
python run_server.py

# Or with options
python run_server.py --host 0.0.0.0 --port 5000 --debug
```

Then open http://localhost:5000/optimizer.html in your browser.

## Usage

### Web Interface

1. **Select a Template** - Click on one of the problem templates
2. **Configure Parameters** - Fill in the problem data or click "Load Example Data"
3. **Solve** - Click the "SOLVE OPTIMIZATION" button
4. **View Results** - See optimal values, variable solutions, and interpretations

### Python API

You can also use the solver directly from Python:

```python
from solver.engine import ConvexSolver, ObjectiveType
from solver import templates

# Example 1: Using a template
result = templates.portfolio_optimization(
    expected_returns=[0.12, 0.10, 0.07, 0.03],
    covariance_matrix=[
        [0.10, 0.03, 0.02, 0.01],
        [0.03, 0.08, 0.02, 0.01],
        [0.02, 0.02, 0.05, 0.01],
        [0.01, 0.01, 0.01, 0.02]
    ],
    risk_aversion=2.0
)
print(f"Status: {result.status}")
print(f"Optimal weights: {result.interpretation['portfolio_weights']}")

# Example 2: Custom problem
import cvxpy as cp

solver = ConvexSolver()
x = solver.create_variable("x", shape=(3,), nonneg=True)
solver.set_objective(ObjectiveType.MAXIMIZE, 3*x[0] + 2*x[1] + 5*x[2])
solver.add_constraint(x[0] + x[1] + x[2] <= 10)
solver.add_constraint(2*x[0] + x[1] <= 8)

result = solver.solve()
print(f"Optimal value: {result.optimal_value}")
print(f"Solution: {result.variables}")
```

### REST API

The Flask server provides a REST API:

```bash
# Health check
GET /api/health

# List templates
GET /api/templates

# Get example data for a template
GET /api/examples/<template_id>

# Solve a template problem
POST /api/templates/<template_id>
Content-Type: application/json
{...problem data...}
```

## Problem Examples

### Portfolio Optimization

```python
from solver.templates import portfolio_optimization

result = portfolio_optimization(
    expected_returns=[0.12, 0.10, 0.07],
    covariance_matrix=[
        [0.10, 0.03, 0.02],
        [0.03, 0.08, 0.02],
        [0.02, 0.02, 0.05]
    ],
    risk_aversion=1.5,
    min_weight=0.0,  # No short selling
    max_weight=0.5   # Max 50% in one asset
)
```

### Transportation Problem

```python
from solver.templates import transportation_problem

result = transportation_problem(
    supply=[100, 150, 200],
    demand=[80, 120, 150, 100],
    costs=[
        [8, 6, 10, 9],
        [9, 12, 13, 7],
        [14, 9, 16, 5]
    ],
    source_names=["Factory A", "Factory B", "Factory C"],
    dest_names=["Store 1", "Store 2", "Store 3", "Store 4"]
)
```

### LASSO Regression

```python
from solver.templates import regularized_regression

result = regularized_regression(
    X=[[1, 2], [2, 1], [3, 3], [4, 2], [5, 4]],
    y=[3.1, 2.9, 6.2, 5.8, 9.1],
    regularization="lasso",
    lambda_param=0.1,
    fit_intercept=True
)
```

## Project Structure

```
retro2000/
├── index.html          # Original retro landing page
├── optimizer.html      # Optimization solver interface
├── optimizer.css       # Retro 2000s styling
├── optimizer.js        # Frontend JavaScript
├── solver/
│   ├── __init__.py
│   ├── engine.py       # Core CVXPY solver engine
│   ├── templates.py    # Pre-built problem templates
│   └── app.py          # Flask REST API
├── run_server.py       # Server startup script
├── requirements.txt    # Python dependencies
└── README.md
```

## What is Convex Optimization?

Convex optimization is a subfield of mathematical optimization that studies the problem of minimizing convex functions over convex sets. The main advantage is that **any local minimum is also a global minimum**, making these problems efficiently solvable.

### Standard Form

```
minimize    f(x)
subject to  g_i(x) <= 0,  i = 1,...,m
            h_j(x) = 0,   j = 1,...,p

where f and g_i are convex functions
and h_j are affine functions
```

### Why Convex?

- **Global optimum guaranteed** - No local minima traps
- **Polynomial time algorithms** - Efficient even for large problems
- **Duality theory** - Provides bounds and sensitivity analysis
- **Wide applicability** - Finance, ML, engineering, operations research

## Retro Design

This application features authentic early 2000s web aesthetics:

- Comic Sans and Courier fonts
- Neon colors on dark backgrounds
- Animated GIF decorations
- "Under Construction" banners
- Blinking text effects
- Scanline overlay
- Marquee scrolling text
- Outset/inset borders

## License

MIT License - Feel free to use, modify, and distribute!

---

*"Making Optimization Cool Since Y2K!"*
