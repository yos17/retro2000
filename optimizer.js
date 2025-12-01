/**
 * CONVEX OPTIMIZER 2000 - Frontend JavaScript
 * Retro-styled optimization solver interface
 */

// =============================================================================
// CONFIGURATION
// =============================================================================

const API_BASE = '/api';
let currentTemplate = null;
let currentData = null;
let solveCount = 0;

// =============================================================================
// TEMPLATE DEFINITIONS
// =============================================================================

const templateForms = {
    portfolio: {
        title: 'Portfolio Optimization',
        description: 'Markowitz Mean-Variance Portfolio Optimization',
        fields: [
            {
                name: 'expected_returns',
                label: 'Expected Returns (comma-separated)',
                type: 'text',
                placeholder: '0.12, 0.10, 0.07, 0.03',
                help: 'Expected return for each asset'
            },
            {
                name: 'covariance_matrix',
                label: 'Covariance Matrix (JSON)',
                type: 'textarea',
                placeholder: '[[0.10, 0.03, 0.02], [0.03, 0.08, 0.02], [0.02, 0.02, 0.05]]',
                help: 'Covariance matrix of returns'
            },
            {
                name: 'risk_aversion',
                label: 'Risk Aversion (λ)',
                type: 'number',
                default: 1.0,
                step: 0.1,
                help: 'Higher = more risk averse'
            },
            {
                name: 'min_weight',
                label: 'Min Weight',
                type: 'number',
                default: 0.0,
                step: 0.05,
                help: 'Minimum weight per asset (0 = no short selling)'
            },
            {
                name: 'max_weight',
                label: 'Max Weight',
                type: 'number',
                default: 1.0,
                step: 0.1,
                help: 'Maximum weight per asset'
            }
        ]
    },

    diet: {
        title: 'Diet Problem',
        description: 'Minimize food cost while meeting nutritional requirements',
        fields: [
            {
                name: 'food_names',
                label: 'Food Names (comma-separated)',
                type: 'text',
                placeholder: 'Bread, Milk, Eggs, Rice'
            },
            {
                name: 'food_costs',
                label: 'Food Costs (comma-separated)',
                type: 'text',
                placeholder: '2.0, 1.5, 3.0, 0.5',
                help: 'Cost per serving of each food'
            },
            {
                name: 'nutrients',
                label: 'Nutrients (comma-separated)',
                type: 'text',
                placeholder: 'Calories, Protein, Fat, Carbs'
            },
            {
                name: 'nutrient_content',
                label: 'Nutrient Content Matrix (JSON)',
                type: 'textarea',
                placeholder: '[[250, 8, 2, 50], [150, 8, 8, 12], ...]',
                help: 'Matrix [food][nutrient] of content per serving'
            },
            {
                name: 'min_nutrients',
                label: 'Min Nutrients (comma-separated)',
                type: 'text',
                placeholder: '2000, 50, 40, 200',
                help: 'Minimum required nutrients'
            }
        ]
    },

    transportation: {
        title: 'Transportation Problem',
        description: 'Minimize shipping costs from sources to destinations',
        fields: [
            {
                name: 'source_names',
                label: 'Source Names (comma-separated)',
                type: 'text',
                placeholder: 'Factory A, Factory B, Factory C'
            },
            {
                name: 'supply',
                label: 'Supply (comma-separated)',
                type: 'text',
                placeholder: '100, 150, 200',
                help: 'Supply available at each source'
            },
            {
                name: 'dest_names',
                label: 'Destination Names (comma-separated)',
                type: 'text',
                placeholder: 'Store 1, Store 2, Store 3, Store 4'
            },
            {
                name: 'demand',
                label: 'Demand (comma-separated)',
                type: 'text',
                placeholder: '80, 120, 150, 100',
                help: 'Demand at each destination'
            },
            {
                name: 'costs',
                label: 'Cost Matrix (JSON)',
                type: 'textarea',
                placeholder: '[[8, 6, 10, 9], [9, 12, 13, 7], [14, 9, 16, 5]]',
                help: 'Cost matrix [source][destination]'
            }
        ]
    },

    resource_allocation: {
        title: 'Resource Allocation',
        description: 'Maximize profit given limited resources',
        fields: [
            {
                name: 'product_names',
                label: 'Product Names (comma-separated)',
                type: 'text',
                placeholder: 'Product A, Product B, Product C'
            },
            {
                name: 'profits',
                label: 'Profits (comma-separated)',
                type: 'text',
                placeholder: '40, 30, 50',
                help: 'Profit per unit of each product'
            },
            {
                name: 'resource_names',
                label: 'Resource Names (comma-separated)',
                type: 'text',
                placeholder: 'Labor, Material, Machine'
            },
            {
                name: 'resource_usage',
                label: 'Resource Usage Matrix (JSON)',
                type: 'textarea',
                placeholder: '[[2, 1, 3], [1, 2, 2], [3, 2, 1]]',
                help: 'Matrix [resource][product] of usage per unit'
            },
            {
                name: 'resource_limits',
                label: 'Resource Limits (comma-separated)',
                type: 'text',
                placeholder: '100, 80, 120',
                help: 'Available amount of each resource'
            }
        ]
    },

    regression: {
        title: 'Regularized Regression',
        description: 'Ridge, LASSO, or Elastic Net regression',
        fields: [
            {
                name: 'X',
                label: 'Feature Matrix X (JSON)',
                type: 'textarea',
                placeholder: '[[1, 2], [3, 4], [5, 6], ...]',
                help: 'Feature matrix [samples][features]'
            },
            {
                name: 'y',
                label: 'Target Vector y (comma-separated)',
                type: 'text',
                placeholder: '1.5, 2.3, 3.1, 4.2, ...'
            },
            {
                name: 'regularization',
                label: 'Regularization Type',
                type: 'select',
                options: ['ridge', 'lasso', 'elastic_net'],
                default: 'ridge'
            },
            {
                name: 'lambda_param',
                label: 'Lambda (regularization strength)',
                type: 'number',
                default: 1.0,
                step: 0.1
            },
            {
                name: 'fit_intercept',
                label: 'Fit Intercept',
                type: 'checkbox',
                default: true
            }
        ]
    },

    knapsack: {
        title: 'Knapsack Problem',
        description: 'Select items to maximize value within weight limit',
        fields: [
            {
                name: 'item_names',
                label: 'Item Names (comma-separated)',
                type: 'text',
                placeholder: 'Laptop, Camera, TV, Phone'
            },
            {
                name: 'values',
                label: 'Values (comma-separated)',
                type: 'text',
                placeholder: '60, 100, 120, 50',
                help: 'Value of each item'
            },
            {
                name: 'weights',
                label: 'Weights (comma-separated)',
                type: 'text',
                placeholder: '10, 20, 30, 8',
                help: 'Weight of each item'
            },
            {
                name: 'capacity',
                label: 'Capacity',
                type: 'number',
                placeholder: '50',
                help: 'Maximum weight capacity'
            }
        ]
    },

    simple_lp: {
        title: 'Simple 2D Linear Program',
        description: 'Two-variable LP for learning and visualization',
        fields: [
            {
                name: 'c',
                label: 'Objective Coefficients (comma-separated)',
                type: 'text',
                placeholder: '3, 2',
                help: 'Coefficients c1, c2 for max c1*x1 + c2*x2'
            },
            {
                name: 'A',
                label: 'Constraint Matrix A (JSON)',
                type: 'textarea',
                placeholder: '[[1, 1], [2, 1], [1, 2]]',
                help: 'Constraint coefficients'
            },
            {
                name: 'b',
                label: 'Constraint RHS (comma-separated)',
                type: 'text',
                placeholder: '4, 5, 4',
                help: 'Right-hand side of constraints'
            },
            {
                name: 'objective_type',
                label: 'Objective',
                type: 'select',
                options: ['maximize', 'minimize'],
                default: 'maximize'
            }
        ]
    },

    min_cost_flow: {
        title: 'Minimum Cost Flow',
        description: 'Network flow optimization',
        fields: [
            {
                name: 'sources',
                label: 'Sources (JSON)',
                type: 'textarea',
                placeholder: '{"Factory1": 100, "Factory2": 150}',
                help: 'Source nodes with supply amounts'
            },
            {
                name: 'sinks',
                label: 'Sinks (JSON)',
                type: 'textarea',
                placeholder: '{"Store1": 80, "Store2": 120}',
                help: 'Sink nodes with demand amounts'
            },
            {
                name: 'arcs',
                label: 'Arcs (JSON)',
                type: 'textarea',
                placeholder: '[{"from": "Factory1", "to": "Store1", "cost": 2, "capacity": 50}, ...]',
                help: 'Network arcs with costs and optional capacities'
            }
        ]
    }
};

// =============================================================================
// INITIALIZATION
// =============================================================================

document.addEventListener('DOMContentLoaded', function() {
    // Load solve counter from localStorage
    solveCount = parseInt(localStorage.getItem('solveCount') || '0');
    updateSolveCounter();

    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'Enter') {
            solveProblem();
        }
    });

    console.log('CONVEX OPTIMIZER 2000 initialized!');
    console.log('Ready to solve optimization problems...');
});

// =============================================================================
// TEMPLATE SELECTION
// =============================================================================

function selectTemplate(templateId) {
    // Update selection state
    document.querySelectorAll('.template-card').forEach(card => {
        card.classList.remove('selected');
    });
    event.currentTarget.classList.add('selected');

    currentTemplate = templateId;
    currentData = null;

    // Generate form
    const template = templateForms[templateId];
    if (!template) {
        console.error('Unknown template:', templateId);
        return;
    }

    const inputArea = document.getElementById('input-area');
    inputArea.innerHTML = generateForm(template);

    // Enable buttons
    document.getElementById('solve-btn').disabled = false;
    document.getElementById('load-example-btn').disabled = false;

    // Scroll to input area
    document.getElementById('problem-input').scrollIntoView({ behavior: 'smooth' });
}

function generateForm(template) {
    let html = `
        <div class="input-form">
            <div class="form-section">
                <h4>${template.title}</h4>
                <p style="color: #aaa; margin-bottom: 15px;">${template.description}</p>
            </div>
    `;

    for (const field of template.fields) {
        html += `<div class="form-row">`;
        html += `<label for="${field.name}">${field.label}:</label>`;

        if (field.type === 'text') {
            html += `<input type="text" id="${field.name}" placeholder="${field.placeholder || ''}"
                     value="${field.default || ''}">`;
        } else if (field.type === 'number') {
            html += `<input type="number" id="${field.name}"
                     value="${field.default !== undefined ? field.default : ''}"
                     step="${field.step || 1}"
                     placeholder="${field.placeholder || ''}">`;
        } else if (field.type === 'textarea') {
            html += `<textarea id="${field.name}" placeholder="${field.placeholder || ''}">${field.default || ''}</textarea>`;
        } else if (field.type === 'select') {
            html += `<select id="${field.name}">`;
            for (const opt of field.options) {
                const selected = opt === field.default ? 'selected' : '';
                html += `<option value="${opt}" ${selected}>${opt}</option>`;
            }
            html += `</select>`;
        } else if (field.type === 'checkbox') {
            const checked = field.default ? 'checked' : '';
            html += `<input type="checkbox" id="${field.name}" ${checked}>`;
        }

        html += `</div>`;

        if (field.help) {
            html += `<div style="color: #666; font-size: 0.8em; margin-left: 120px; margin-bottom: 10px;">
                     ${field.help}</div>`;
        }
    }

    html += `</div>`;
    return html;
}

// =============================================================================
// DATA LOADING
// =============================================================================

async function loadExample() {
    if (!currentTemplate) {
        alert('Please select a template first!');
        return;
    }

    showLoading();

    try {
        const response = await fetch(`${API_BASE}/examples/${currentTemplate}`);
        if (!response.ok) throw new Error('Failed to load example');

        const data = await response.json();
        populateForm(data);
        currentData = data;

        hideLoading();
    } catch (error) {
        hideLoading();
        showError('Failed to load example: ' + error.message);
    }
}

function populateForm(data) {
    const template = templateForms[currentTemplate];

    for (const field of template.fields) {
        const element = document.getElementById(field.name);
        if (!element) continue;

        let value = data[field.name];
        if (value === undefined || value === null) continue;

        if (field.type === 'textarea' || (field.type === 'text' && typeof value === 'object')) {
            element.value = JSON.stringify(value, null, 2);
        } else if (field.type === 'text' && Array.isArray(value)) {
            element.value = value.join(', ');
        } else if (field.type === 'checkbox') {
            element.checked = value;
        } else {
            element.value = value;
        }
    }
}

// =============================================================================
// SOLVING
// =============================================================================

async function solveProblem() {
    if (!currentTemplate) {
        alert('Please select a template first!');
        return;
    }

    showLoading();

    try {
        const data = collectFormData();
        const response = await fetch(`${API_BASE}/templates/${currentTemplate}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok) {
            displayResults(result);
            incrementSolveCounter();
        } else {
            showError(result.error || 'Unknown error occurred');
        }

        hideLoading();
    } catch (error) {
        hideLoading();
        showError('Failed to solve: ' + error.message);
    }
}

function collectFormData() {
    const template = templateForms[currentTemplate];
    const data = {};

    for (const field of template.fields) {
        const element = document.getElementById(field.name);
        if (!element) continue;

        let value;
        if (field.type === 'checkbox') {
            value = element.checked;
        } else if (field.type === 'number') {
            value = parseFloat(element.value);
        } else if (field.type === 'textarea') {
            try {
                value = JSON.parse(element.value);
            } catch {
                value = element.value;
            }
        } else if (field.type === 'text') {
            // Check if it's a comma-separated list
            const val = element.value.trim();
            if (val.includes(',')) {
                value = val.split(',').map(s => {
                    const trimmed = s.trim();
                    const num = parseFloat(trimmed);
                    return isNaN(num) ? trimmed : num;
                });
            } else {
                value = val;
            }
        } else {
            value = element.value;
        }

        data[field.name] = value;
    }

    return data;
}

// =============================================================================
// RESULTS DISPLAY
// =============================================================================

function displayResults(result) {
    const resultsArea = document.getElementById('results-area');

    let statusClass = 'optimal';
    if (result.status === 'infeasible') statusClass = 'infeasible';
    else if (result.status === 'unbounded') statusClass = 'unbounded';
    else if (result.status !== 'optimal') statusClass = 'infeasible';

    let html = `
        <div class="results-content">
            <div class="result-status ${statusClass}">
                STATUS: ${result.status.toUpperCase()}
            </div>

            <div class="result-section">
                <h4>Optimal Value</h4>
                <div class="result-value">${formatNumber(result.optimal_value)}</div>
            </div>
    `;

    // Variables section
    if (result.variables && Object.keys(result.variables).length > 0) {
        html += `<div class="result-section"><h4>Variables</h4>`;
        html += formatVariables(result.variables);
        html += `</div>`;
    }

    // Interpretation section (template-specific)
    if (result.interpretation) {
        html += `<div class="result-section"><h4>Interpretation</h4>`;
        html += formatInterpretation(result.interpretation);
        html += `</div>`;
    }

    // Solver stats
    html += `
        <div class="result-section">
            <h4>Solver Information</h4>
            <table class="result-table">
                <tr><th>Property</th><th>Value</th></tr>
                <tr><td>Solver</td><td>${result.solver_stats?.solver_name || 'N/A'}</td></tr>
                <tr><td>Problem Type</td><td>${result.problem_type || 'N/A'}</td></tr>
                <tr><td>Is Convex</td><td>${result.is_convex ? 'Yes' : 'No'}</td></tr>
            </table>
        </div>
    `;

    html += `</div>`;
    resultsArea.innerHTML = html;

    // Scroll to results
    document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
}

function formatNumber(value) {
    if (value === null || value === undefined) return 'N/A';
    if (typeof value === 'number') {
        return value.toFixed(6);
    }
    return String(value);
}

function formatVariables(variables) {
    let html = '<table class="result-table"><tr><th>Variable</th><th>Value</th></tr>';

    for (const [name, value] of Object.entries(variables)) {
        let displayValue;
        if (Array.isArray(value)) {
            displayValue = '[' + value.map(v => formatNumber(v)).join(', ') + ']';
        } else {
            displayValue = formatNumber(value);
        }
        html += `<tr><td>${name}</td><td>${displayValue}</td></tr>`;
    }

    html += '</table>';
    return html;
}

function formatInterpretation(interp) {
    let html = '<div style="font-family: Courier New, monospace;">';

    for (const [key, value] of Object.entries(interp)) {
        if (value === null || value === undefined) continue;

        const displayKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

        if (Array.isArray(value)) {
            html += `<p><b>${displayKey}:</b></p><ul>`;
            for (const item of value) {
                if (typeof item === 'object') {
                    html += `<li>${JSON.stringify(item)}</li>`;
                } else {
                    html += `<li>${item}</li>`;
                }
            }
            html += '</ul>';
        } else if (typeof value === 'object') {
            html += `<p><b>${displayKey}:</b></p>`;
            html += '<table class="result-table"><tr><th>Item</th><th>Value</th></tr>';
            for (const [k, v] of Object.entries(value)) {
                const displayV = typeof v === 'object' ? JSON.stringify(v) : formatNumber(v);
                html += `<tr><td>${k}</td><td>${displayV}</td></tr>`;
            }
            html += '</table>';
        } else {
            html += `<p><b>${displayKey}:</b> ${formatNumber(value)}</p>`;
        }
    }

    html += '</div>';
    return html;
}

// =============================================================================
// CUSTOM PROBLEM BUILDER
// =============================================================================

function addVariable() {
    const list = document.getElementById('variables-list');
    const row = document.createElement('div');
    row.className = 'variable-row';
    row.innerHTML = `
        <input type="text" placeholder="Name" class="var-name">
        <select class="var-type">
            <option value="continuous">Continuous</option>
            <option value="integer">Integer</option>
            <option value="binary">Binary</option>
        </select>
        <input type="number" placeholder="Size" class="var-size" value="1">
        <label><input type="checkbox" class="var-nonneg"> >= 0</label>
        <button class="remove-btn" onclick="this.parentElement.remove()">X</button>
    `;
    list.appendChild(row);
}

function addConstraint() {
    const list = document.getElementById('constraints-list');
    const row = document.createElement('div');
    row.className = 'constraint-row';
    row.innerHTML = `
        <input type="text" placeholder="LHS expression" class="const-lhs">
        <select class="const-type">
            <option value="<="><=</option>
            <option value=">=">>=</option>
            <option value="==">=</option>
        </select>
        <input type="text" placeholder="RHS" class="const-rhs">
        <button class="remove-btn" onclick="this.parentElement.remove()">X</button>
    `;
    list.appendChild(row);
}

function removeConstraint(btn) {
    btn.parentElement.remove();
}

async function solveCustomProblem() {
    showLoading();

    try {
        // Collect custom problem data
        const objectiveType = document.getElementById('custom-obj-type').value;
        const objectiveExpr = document.getElementById('custom-objective').value;

        // Collect variables
        const variables = [];
        document.querySelectorAll('.variable-row').forEach(row => {
            const name = row.querySelector('.var-name').value.trim();
            if (name) {
                variables.push({
                    name: name,
                    type: row.querySelector('.var-type').value,
                    size: parseInt(row.querySelector('.var-size').value) || 1,
                    nonneg: row.querySelector('.var-nonneg').checked
                });
            }
        });

        // Collect constraints
        const constraints = [];
        document.querySelectorAll('.constraint-row').forEach(row => {
            const lhs = row.querySelector('.const-lhs').value.trim();
            const rhs = row.querySelector('.const-rhs').value.trim();
            if (lhs && rhs) {
                constraints.push({
                    lhs: lhs,
                    type: row.querySelector('.const-type').value,
                    rhs: rhs
                });
            }
        });

        // For now, show a message since custom expression parsing needs backend work
        hideLoading();
        const resultsArea = document.getElementById('results-area');
        resultsArea.innerHTML = `
            <div class="results-content">
                <div class="result-section">
                    <h4>Custom Problem Definition</h4>
                    <p><b>Objective:</b> ${objectiveType} ${objectiveExpr}</p>
                    <p><b>Variables:</b> ${variables.map(v => v.name).join(', ') || 'None'}</p>
                    <p><b>Constraints:</b> ${constraints.length}</p>
                </div>
                <div class="result-section">
                    <h4>Note</h4>
                    <p style="color: #ffff00;">Custom expression parsing is available via the Python API directly.</p>
                    <p>For complex custom problems, use the Python interface:</p>
                    <pre style="color: #00ff00; background: #000011; padding: 10px;">
from solver.engine import ConvexSolver

solver = ConvexSolver()
x = solver.create_variable("x", nonneg=True)
y = solver.create_variable("y", nonneg=True)
solver.set_objective("maximize", 3*x + 2*y)
solver.add_constraint(x + y <= 4)
result = solver.solve()
print(result)
                    </pre>
                </div>
            </div>
        `;

        document.getElementById('results').scrollIntoView({ behavior: 'smooth' });

    } catch (error) {
        hideLoading();
        showError('Failed to process custom problem: ' + error.message);
    }
}

// =============================================================================
// UTILITIES
// =============================================================================

function showLoading() {
    document.getElementById('loading-modal').classList.add('active');
    animateLoadingSpinner();
}

function hideLoading() {
    document.getElementById('loading-modal').classList.remove('active');
}

let spinnerInterval;
function animateLoadingSpinner() {
    const chars = ['/', '-', '\\', '|'];
    let i = 0;
    const spinner = document.querySelector('.spinner-char');
    if (spinnerInterval) clearInterval(spinnerInterval);
    spinnerInterval = setInterval(() => {
        spinner.textContent = chars[i % chars.length];
        i++;
    }, 100);
}

function showError(message) {
    const resultsArea = document.getElementById('results-area');
    resultsArea.innerHTML = `
        <div class="results-content">
            <div class="result-status infeasible">ERROR</div>
            <div class="result-section">
                <h4>Error Details</h4>
                <p style="color: #ff6666;">${message}</p>
            </div>
        </div>
    `;
    document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
}

function clearAll() {
    currentTemplate = null;
    currentData = null;

    document.querySelectorAll('.template-card').forEach(card => {
        card.classList.remove('selected');
    });

    document.getElementById('input-area').innerHTML = `
        <div class="placeholder-text">
            <pre>
   _____      _           _     _____           _     _
  / ____|    | |         | |   |  __ \\         | |   | |
 | (___   ___| | ___  ___| |_  | |__) | __ ___ | |__ | | ___ _ __ ___
  \\___ \\ / _ \\ |/ _ \\/ __| __| |  ___/ '__/ _ \\| '_ \\| |/ _ \\ '_ \` _ \\
  ____) |  __/ |  __/ (__| |_  | |   | | | (_) | |_) | |  __/ | | | | |
 |_____/ \\___|_|\\___|\\___\\__| |_|   |_|  \\___/|_.__/|_|\\___|_| |_| |_|
            </pre>
            <p>Click on a template above to get started!</p>
        </div>
    `;

    document.getElementById('results-area').innerHTML = `
        <div class="waiting-text">
            <pre>
+------------------------------------------+
|                                          |
|     Waiting for optimization...          |
|                                          |
|     Status: IDLE                         |
|                                          |
+------------------------------------------+
            </pre>
        </div>
    `;

    document.getElementById('solve-btn').disabled = true;
    document.getElementById('load-example-btn').disabled = true;
}

function updateSolveCounter() {
    const counter = document.getElementById('solve-counter');
    counter.textContent = String(solveCount).padStart(5, '0');
}

function incrementSolveCounter() {
    solveCount++;
    localStorage.setItem('solveCount', solveCount.toString());
    updateSolveCounter();
}

// Fun effects
function flashColors(element) {
    const colors = ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff'];
    let i = 0;
    const interval = setInterval(() => {
        element.style.color = colors[i % colors.length];
        i++;
        if (i > 10) {
            clearInterval(interval);
            element.style.color = '';
        }
    }, 100);
}

// Log startup message
console.log(`
   _____ _______      _______ _   _  _____
  / ____/ __ \\ \\    / /_   _| \\ | |/ ____|
 | |   | |  | \\ \\  / /  | | |  \\| | |  __
 | |   | |  | |\\ \\/ /   | | | . \` | | |_ |
 | |___| |__| | \\  /   _| |_| |\\  | |__| |
  \\_____\\____/   \\/   |_____|_| \\_|\\_____|

   OPTIMIZER 2000 - Frontend Loaded!
`);
