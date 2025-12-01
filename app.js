/**
 * OptiSolve - Modern Optimization Solver
 * Clean, minimal JavaScript for the frontend
 */

// =============================================================================
// CONFIGURATION
// =============================================================================

const API_BASE = '/api';
let templates = [];
let currentTemplate = null;
let currentCategory = 'all';
let lastResult = null;

// =============================================================================
// TEMPLATE FORM DEFINITIONS
// =============================================================================

const templateForms = {
    portfolio: {
        fields: [
            { name: 'expected_returns', label: 'Expected Returns', type: 'text', placeholder: '0.12, 0.10, 0.07, 0.03', help: 'Comma-separated expected returns for each asset' },
            { name: 'covariance_matrix', label: 'Covariance Matrix', type: 'textarea', placeholder: '[[0.10, 0.03], [0.03, 0.08]]', help: 'JSON format covariance matrix' },
            { name: 'risk_aversion', label: 'Risk Aversion', type: 'number', default: 1.0, step: 0.1 },
            { name: 'min_weight', label: 'Min Weight', type: 'number', default: 0.0, step: 0.05 },
            { name: 'max_weight', label: 'Max Weight', type: 'number', default: 1.0, step: 0.1 }
        ]
    },
    diet: {
        fields: [
            { name: 'food_names', label: 'Food Names', type: 'text', placeholder: 'Bread, Milk, Eggs' },
            { name: 'food_costs', label: 'Food Costs', type: 'text', placeholder: '2.0, 1.5, 3.0' },
            { name: 'nutrients', label: 'Nutrients', type: 'text', placeholder: 'Calories, Protein, Fat' },
            { name: 'nutrient_content', label: 'Nutrient Content Matrix', type: 'textarea', placeholder: '[[250, 8, 2], [150, 8, 8]]' },
            { name: 'min_nutrients', label: 'Min Nutrients', type: 'text', placeholder: '2000, 50, 40' }
        ]
    },
    transportation: {
        fields: [
            { name: 'source_names', label: 'Source Names', type: 'text', placeholder: 'Factory A, Factory B' },
            { name: 'supply', label: 'Supply', type: 'text', placeholder: '100, 150, 200' },
            { name: 'dest_names', label: 'Destination Names', type: 'text', placeholder: 'Store 1, Store 2' },
            { name: 'demand', label: 'Demand', type: 'text', placeholder: '80, 120, 150' },
            { name: 'costs', label: 'Cost Matrix', type: 'textarea', placeholder: '[[8, 6], [9, 12]]' }
        ]
    },
    resource_allocation: {
        fields: [
            { name: 'product_names', label: 'Product Names', type: 'text', placeholder: 'Product A, Product B' },
            { name: 'profits', label: 'Profits', type: 'text', placeholder: '40, 30, 50' },
            { name: 'resource_names', label: 'Resource Names', type: 'text', placeholder: 'Labor, Material' },
            { name: 'resource_usage', label: 'Resource Usage Matrix', type: 'textarea', placeholder: '[[2, 1], [1, 2]]' },
            { name: 'resource_limits', label: 'Resource Limits', type: 'text', placeholder: '100, 80' }
        ]
    },
    regression: {
        fields: [
            { name: 'X', label: 'Feature Matrix X', type: 'textarea', placeholder: '[[1, 2], [3, 4], [5, 6]]' },
            { name: 'y', label: 'Target y', type: 'text', placeholder: '1.5, 2.3, 3.1' },
            { name: 'regularization', label: 'Regularization', type: 'select', options: ['ridge', 'lasso', 'elastic_net'] },
            { name: 'lambda_param', label: 'Lambda', type: 'number', default: 1.0, step: 0.1 },
            { name: 'fit_intercept', label: 'Fit Intercept', type: 'checkbox', default: true }
        ]
    },
    knapsack: {
        fields: [
            { name: 'item_names', label: 'Item Names', type: 'text', placeholder: 'Laptop, Camera, Phone' },
            { name: 'values', label: 'Values', type: 'text', placeholder: '60, 100, 120' },
            { name: 'weights', label: 'Weights', type: 'text', placeholder: '10, 20, 30' },
            { name: 'capacity', label: 'Capacity', type: 'number', placeholder: '50' }
        ]
    },
    simple_lp: {
        fields: [
            { name: 'c', label: 'Objective Coefficients', type: 'text', placeholder: '3, 2' },
            { name: 'A', label: 'Constraint Matrix', type: 'textarea', placeholder: '[[1, 1], [2, 1]]' },
            { name: 'b', label: 'Constraint RHS', type: 'text', placeholder: '4, 5' },
            { name: 'objective_type', label: 'Objective', type: 'select', options: ['maximize', 'minimize'] }
        ]
    },
    min_cost_flow: {
        fields: [
            { name: 'sources', label: 'Sources (JSON)', type: 'textarea', placeholder: '{"Factory1": 100}' },
            { name: 'sinks', label: 'Sinks (JSON)', type: 'textarea', placeholder: '{"Store1": 80}' },
            { name: 'arcs', label: 'Arcs (JSON)', type: 'textarea', placeholder: '[{"from": "Factory1", "to": "Store1", "cost": 2}]' }
        ]
    },
    pizza_shop: {
        fields: [
            { name: 'products', label: 'Products (JSON)', type: 'textarea', placeholder: '[{"name": "Margherita", "price": 12, "ingredients": {"dough": 1}, "demand_estimate": 40}]', help: 'Array of products with name, price, ingredients, demand' },
            { name: 'ingredient_costs', label: 'Ingredient Costs (JSON)', type: 'textarea', placeholder: '{"dough": 1.5, "sauce": 2}' },
            { name: 'ingredient_inventory', label: 'Inventory (JSON)', type: 'textarea', placeholder: '{"dough": 200, "sauce": 80}' },
            { name: 'labor_cost_per_item', label: 'Labor Costs', type: 'text', placeholder: '2, 2.5, 3', help: 'Cost per item produced' }
        ]
    },
    staff_scheduling: {
        fields: [
            { name: 'shifts', label: 'Shifts (JSON)', type: 'textarea', placeholder: '[{"name": "Mon AM", "hours": 6}]' },
            { name: 'staff', label: 'Staff (JSON)', type: 'textarea', placeholder: '[{"name": "Alice", "hourly_rate": 15, "availability": [0, 1, 2]}]' },
            { name: 'min_staff_per_shift', label: 'Min Staff per Shift', type: 'text', placeholder: '2, 2, 2' },
            { name: 'max_hours_per_week', label: 'Max Hours/Week', type: 'number', default: 40 }
        ]
    },
    inventory_ordering: {
        fields: [
            { name: 'items', label: 'Items (JSON)', type: 'textarea', placeholder: '[{"name": "Flour", "unit_cost": 2, "holding_cost": 0.1}]' },
            { name: 'demand_forecast', label: 'Demand Forecast', type: 'text', placeholder: '100, 50, 40' },
            { name: 'current_inventory', label: 'Current Inventory', type: 'text', placeholder: '20, 10, 5' },
            { name: 'storage_capacity', label: 'Storage Capacity', type: 'number', placeholder: '300' },
            { name: 'budget', label: 'Budget', type: 'number', placeholder: '1000' }
        ]
    },
    pricing: {
        fields: [
            { name: 'products', label: 'Products (JSON)', type: 'textarea', placeholder: '[{"name": "Small Pizza", "base_price": 10}]' },
            { name: 'price_range', label: 'Price Ranges', type: 'textarea', placeholder: '[[8, 12], [12, 18]]', help: '[min, max] for each product' },
            { name: 'base_demand', label: 'Base Demand', type: 'text', placeholder: '50, 80, 40' },
            { name: 'price_elasticity', label: 'Price Elasticity', type: 'text', placeholder: '1.2, 1.0, 0.8' },
            { name: 'costs', label: 'Variable Costs', type: 'text', placeholder: '4, 6, 8' }
        ]
    }
};

// =============================================================================
// INITIALIZATION
// =============================================================================

document.addEventListener('DOMContentLoaded', async function() {
    await loadTemplates();
    setupCategoryTabs();
    console.log('OptiSolve initialized');
});

async function loadTemplates() {
    try {
        const response = await fetch(`${API_BASE}/templates`);
        const data = await response.json();
        templates = data.templates;
        renderTemplates(templates);
    } catch (error) {
        console.error('Failed to load templates:', error);
    }
}

function setupCategoryTabs() {
    document.querySelectorAll('.category-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.category-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            currentCategory = tab.dataset.category;
            filterTemplates();
        });
    });
}

function filterTemplates() {
    if (currentCategory === 'all') {
        renderTemplates(templates);
    } else {
        renderTemplates(templates.filter(t => t.category === currentCategory));
    }
}

// =============================================================================
// RENDER TEMPLATES
// =============================================================================

function renderTemplates(templatesToRender) {
    const grid = document.getElementById('template-grid');
    grid.innerHTML = templatesToRender.map(template => `
        <div class="template-card" onclick="openTemplate('${template.id}')">
            <div class="template-card-header">
                <div class="template-icon ${template.category}">
                    <span class="material-icons-round">${template.icon || 'auto_graph'}</span>
                </div>
                <div class="template-info">
                    <h3>${template.name}</h3>
                    <span class="template-type">${template.problem_type}</span>
                </div>
            </div>
            <p class="template-description">${template.description}</p>
            <div class="template-footer">
                <span class="template-category">
                    <span class="material-icons-round">folder</span>
                    ${template.category}
                </span>
                <span class="template-action">
                    Open
                    <span class="material-icons-round">arrow_forward</span>
                </span>
            </div>
        </div>
    `).join('');
}

// =============================================================================
// MODAL HANDLING
// =============================================================================

function openTemplate(templateId) {
    const template = templates.find(t => t.id === templateId);
    if (!template) return;

    currentTemplate = templateId;

    document.getElementById('modal-icon').textContent = template.icon || 'auto_graph';
    document.getElementById('modal-title').textContent = template.name;
    document.getElementById('modal-description').textContent = template.description;

    const formDef = templateForms[templateId];
    if (formDef) {
        document.getElementById('modal-body').innerHTML = generateForm(formDef.fields);
    } else {
        document.getElementById('modal-body').innerHTML = '<p>Form not available for this template.</p>';
    }

    document.getElementById('problem-modal').classList.add('active');
}

function closeModal() {
    document.getElementById('problem-modal').classList.remove('active');
    currentTemplate = null;
}

function closeResultsModal() {
    document.getElementById('results-modal').classList.remove('active');
}

function generateForm(fields) {
    return fields.map(field => `
        <div class="form-group">
            <label class="form-label" for="${field.name}">${field.label}</label>
            ${generateFormInput(field)}
            ${field.help ? `<p class="form-help">${field.help}</p>` : ''}
        </div>
    `).join('');
}

function generateFormInput(field) {
    switch (field.type) {
        case 'textarea':
            return `<textarea class="form-textarea" id="${field.name}" placeholder="${field.placeholder || ''}">${field.default || ''}</textarea>`;
        case 'select':
            return `<select class="form-select" id="${field.name}">
                ${field.options.map(opt => `<option value="${opt}">${opt}</option>`).join('')}
            </select>`;
        case 'checkbox':
            return `<div class="form-checkbox">
                <input type="checkbox" id="${field.name}" ${field.default ? 'checked' : ''}>
                <label for="${field.name}">Enable</label>
            </div>`;
        case 'number':
            return `<input class="form-input" type="number" id="${field.name}" value="${field.default || ''}" step="${field.step || 1}" placeholder="${field.placeholder || ''}">`;
        default:
            return `<input class="form-input" type="text" id="${field.name}" placeholder="${field.placeholder || ''}" value="${field.default || ''}">`;
    }
}

// =============================================================================
// DATA HANDLING
// =============================================================================

async function loadExample() {
    if (!currentTemplate) return;

    try {
        const response = await fetch(`${API_BASE}/examples/${currentTemplate}`);
        const data = await response.json();
        populateForm(data);
    } catch (error) {
        console.error('Failed to load example:', error);
    }
}

function populateForm(data) {
    const formDef = templateForms[currentTemplate];
    if (!formDef) return;

    for (const field of formDef.fields) {
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

function collectFormData() {
    const formDef = templateForms[currentTemplate];
    if (!formDef) return {};

    const data = {};
    for (const field of formDef.fields) {
        const element = document.getElementById(field.name);
        if (!element) continue;

        let value;
        if (field.type === 'checkbox') {
            value = element.checked;
        } else if (field.type === 'number') {
            value = parseFloat(element.value);
        } else if (field.type === 'textarea') {
            try { value = JSON.parse(element.value); }
            catch { value = element.value; }
        } else if (field.type === 'text') {
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
// SOLVING
// =============================================================================

async function solveProblem() {
    if (!currentTemplate) return;

    showLoading();

    try {
        const data = collectFormData();
        const response = await fetch(`${API_BASE}/templates/${currentTemplate}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        lastResult = result;

        hideLoading();
        closeModal();

        if (response.ok) {
            displayResults(result);
        } else {
            displayError(result.error || 'Unknown error');
        }
    } catch (error) {
        hideLoading();
        displayError(error.message);
    }
}

// =============================================================================
// RESULTS DISPLAY
// =============================================================================

function displayResults(result) {
    const isSuccess = result.status === 'optimal';

    document.getElementById('result-status-icon').textContent = isSuccess ? 'check_circle' : 'error';
    document.getElementById('result-status-icon').className = `material-icons-round modal-icon ${isSuccess ? 'success' : 'error'}`;
    document.getElementById('result-title').textContent = 'Optimization Results';
    document.getElementById('result-status').textContent = `Status: ${result.status}`;

    let html = `
        <div class="result-summary ${isSuccess ? '' : 'error'}">
            <div class="result-value">${formatNumber(result.optimal_value)}</div>
            <div class="result-label">Optimal Value</div>
        </div>
    `;

    // Variables
    if (result.variables && Object.keys(result.variables).length > 0) {
        html += `
            <div class="result-section">
                <h4><span class="material-icons-round">data_array</span> Variables</h4>
                <table class="result-table">
                    <thead><tr><th>Variable</th><th>Value</th></tr></thead>
                    <tbody>
                        ${Object.entries(result.variables).map(([k, v]) => `
                            <tr><td>${k}</td><td>${formatValue(v)}</td></tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }

    // Interpretation
    if (result.interpretation) {
        html += `
            <div class="result-section">
                <h4><span class="material-icons-round">insights</span> Interpretation</h4>
                ${formatInterpretation(result.interpretation)}
            </div>
        `;
    }

    // Solver Info
    html += `
        <div class="result-section">
            <h4><span class="material-icons-round">info</span> Solver Information</h4>
            <div class="result-grid">
                <div class="result-card">
                    <div class="result-card-value">${result.solver_stats?.solver_name || 'N/A'}</div>
                    <div class="result-card-label">Solver</div>
                </div>
                <div class="result-card">
                    <div class="result-card-value">${result.problem_type || 'N/A'}</div>
                    <div class="result-card-label">Problem Type</div>
                </div>
                <div class="result-card">
                    <div class="result-card-value">${result.is_convex ? 'Yes' : 'No'}</div>
                    <div class="result-card-label">Convex</div>
                </div>
            </div>
        </div>
    `;

    document.getElementById('results-body').innerHTML = html;
    document.getElementById('results-modal').classList.add('active');
}

function displayError(message) {
    document.getElementById('result-status-icon').textContent = 'error';
    document.getElementById('result-status-icon').className = 'material-icons-round modal-icon error';
    document.getElementById('result-title').textContent = 'Error';
    document.getElementById('result-status').textContent = 'Failed to solve';

    document.getElementById('results-body').innerHTML = `
        <div class="result-summary error">
            <div class="result-value">Error</div>
            <div class="result-label">${message}</div>
        </div>
    `;

    document.getElementById('results-modal').classList.add('active');
}

function formatNumber(value) {
    if (value === null || value === undefined) return 'N/A';
    if (typeof value === 'number') {
        return value.toLocaleString(undefined, { maximumFractionDigits: 4 });
    }
    return String(value);
}

function formatValue(value) {
    if (Array.isArray(value)) {
        return '[' + value.map(v => formatNumber(v)).join(', ') + ']';
    }
    return formatNumber(value);
}

function formatInterpretation(interp) {
    let html = '<div class="result-grid">';

    for (const [key, value] of Object.entries(interp)) {
        if (value === null || value === undefined) continue;

        const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

        if (typeof value === 'object' && !Array.isArray(value)) {
            html += `</div><h5 style="margin: 16px 0 8px; font-size: 14px;">${label}</h5>`;
            html += `<table class="result-table"><tbody>`;
            for (const [k, v] of Object.entries(value)) {
                const displayV = typeof v === 'object' ? JSON.stringify(v) : formatNumber(v);
                html += `<tr><td>${k}</td><td>${displayV}</td></tr>`;
            }
            html += `</tbody></table><div class="result-grid">`;
        } else if (Array.isArray(value)) {
            // Skip arrays for now
        } else {
            html += `
                <div class="result-card">
                    <div class="result-card-value">${formatNumber(value)}</div>
                    <div class="result-card-label">${label}</div>
                </div>
            `;
        }
    }

    html += '</div>';
    return html;
}

// =============================================================================
// UTILITIES
// =============================================================================

function showLoading() {
    document.getElementById('loading').classList.add('active');
}

function hideLoading() {
    document.getElementById('loading').classList.remove('active');
}

function downloadResults() {
    if (!lastResult) return;

    const blob = new Blob([JSON.stringify(lastResult, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `optimization-result-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});
