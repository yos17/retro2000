// SheetGenius - AI-Powered Google Sheets Formula Generator
// =========================================================

// State management
const state = {
    isSignedIn: false,
    accessToken: null,
    user: null,
    connectedSheet: null,
    sheetData: null,
    isLoading: false,
};

// DOM Elements
const elements = {
    googleSignInBtn: null,
    userProfile: null,
    userAvatar: null,
    userName: null,
    connectionStatus: null,
    sheetSelector: null,
    sheetUrl: null,
    connectSheetBtn: null,
    sheetInfo: null,
    sheetName: null,
    sheetColumns: null,
    disconnectBtn: null,
    formulaRequest: null,
    charCount: null,
    generateBtn: null,
    resultSection: null,
    formulaOutput: null,
    explanationOutput: null,
    copyBtn: null,
};

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    initializeElements();
    initializeEventListeners();
    checkConfiguration();
    initializeGoogleAuth();
});

// Cache DOM elements
function initializeElements() {
    elements.googleSignInBtn = document.getElementById('googleSignInBtn');
    elements.userProfile = document.getElementById('userProfile');
    elements.userAvatar = document.getElementById('userAvatar');
    elements.userName = document.getElementById('userName');
    elements.connectionStatus = document.getElementById('connectionStatus');
    elements.sheetSelector = document.getElementById('sheetSelector');
    elements.sheetUrl = document.getElementById('sheetUrl');
    elements.connectSheetBtn = document.getElementById('connectSheetBtn');
    elements.sheetInfo = document.getElementById('sheetInfo');
    elements.sheetName = document.getElementById('sheetName');
    elements.sheetColumns = document.getElementById('sheetColumns');
    elements.disconnectBtn = document.getElementById('disconnectBtn');
    elements.formulaRequest = document.getElementById('formulaRequest');
    elements.charCount = document.getElementById('charCount');
    elements.generateBtn = document.getElementById('generateBtn');
    elements.resultSection = document.getElementById('resultSection');
    elements.formulaOutput = document.getElementById('formulaOutput');
    elements.explanationOutput = document.getElementById('explanationOutput');
    elements.copyBtn = document.getElementById('copyBtn');
}

// Set up event listeners
function initializeEventListeners() {
    // Google Sign In
    elements.googleSignInBtn?.addEventListener('click', handleGoogleSignIn);

    // Sheet connection
    elements.connectSheetBtn?.addEventListener('click', handleConnectSheet);
    elements.disconnectBtn?.addEventListener('click', handleDisconnect);

    // Formula generation
    elements.formulaRequest?.addEventListener('input', handleFormulaInput);
    elements.generateBtn?.addEventListener('click', handleGenerateFormula);

    // Copy button
    elements.copyBtn?.addEventListener('click', handleCopyFormula);

    // Enter key in textarea
    elements.formulaRequest?.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && e.ctrlKey) {
            handleGenerateFormula();
        }
    });
}

// Check if configuration is valid
function checkConfiguration() {
    const issues = validateConfig();
    if (issues.length > 0) {
        console.warn('Configuration issues:', issues);
        // Show a subtle warning but don't block the UI
        // The demo can still work with mock data
    }
}

// ================================
// Google Authentication
// ================================

let tokenClient = null;

function initializeGoogleAuth() {
    // Check if Google Identity Services is loaded
    if (typeof google === 'undefined' || !google.accounts) {
        console.log('Google Identity Services not loaded yet, retrying...');
        setTimeout(initializeGoogleAuth, 100);
        return;
    }

    try {
        tokenClient = google.accounts.oauth2.initTokenClient({
            client_id: CONFIG.GOOGLE_CLIENT_ID,
            scope: CONFIG.GOOGLE_SCOPES,
            callback: handleAuthResponse,
        });
        console.log('Google Auth initialized');
    } catch (error) {
        console.error('Failed to initialize Google Auth:', error);
    }
}

function handleGoogleSignIn() {
    if (!tokenClient) {
        showToast('Google authentication not ready. Please try again.', 'error');
        return;
    }

    // Request access token
    tokenClient.requestAccessToken({ prompt: 'consent' });
}

function handleAuthResponse(response) {
    if (response.error) {
        console.error('Auth error:', response);
        showToast('Authentication failed. Please try again.', 'error');
        return;
    }

    state.accessToken = response.access_token;
    state.isSignedIn = true;

    // Fetch user info
    fetchUserInfo();

    // Update UI
    updateAuthUI();
}

async function fetchUserInfo() {
    try {
        const response = await fetch('https://www.googleapis.com/oauth2/v2/userinfo', {
            headers: {
                Authorization: `Bearer ${state.accessToken}`,
            },
        });

        if (response.ok) {
            state.user = await response.json();
            updateUserProfileUI();
        }
    } catch (error) {
        console.error('Failed to fetch user info:', error);
    }
}

function updateAuthUI() {
    if (state.isSignedIn) {
        elements.googleSignInBtn?.classList.add('hidden');
        elements.userProfile?.classList.remove('hidden');
        elements.sheetSelector?.classList.remove('hidden');
        updateConnectionStatus('signed-in', 'Signed in - Paste a sheet URL below');
    } else {
        elements.googleSignInBtn?.classList.remove('hidden');
        elements.userProfile?.classList.add('hidden');
        elements.sheetSelector?.classList.add('hidden');
        updateConnectionStatus('disconnected', 'Sign in to connect your Google Sheets');
    }
}

function updateUserProfileUI() {
    if (state.user) {
        if (elements.userAvatar) {
            elements.userAvatar.src = state.user.picture || '';
        }
        if (elements.userName) {
            elements.userName.textContent = state.user.name || state.user.email;
        }
    }
}

// ================================
// Google Sheets Integration
// ================================

async function handleConnectSheet() {
    const url = elements.sheetUrl?.value?.trim();

    if (!url) {
        showToast('Please enter a Google Sheet URL', 'error');
        return;
    }

    // Extract spreadsheet ID from URL
    const sheetId = extractSheetId(url);

    if (!sheetId) {
        showToast('Invalid Google Sheet URL. Please check and try again.', 'error');
        return;
    }

    updateConnectionStatus('loading', 'Connecting to sheet...');

    try {
        // Fetch spreadsheet metadata
        const metadata = await fetchSheetMetadata(sheetId);

        if (!metadata) {
            throw new Error('Could not fetch sheet data');
        }

        // Fetch first sheet data to understand structure
        const sheetData = await fetchSheetData(sheetId, metadata.sheets[0].properties.title);

        state.connectedSheet = {
            id: sheetId,
            title: metadata.properties.title,
            sheets: metadata.sheets,
        };

        state.sheetData = sheetData;

        // Update UI
        showSheetInfo();
        showToast('Sheet connected successfully!', 'success');

    } catch (error) {
        console.error('Failed to connect sheet:', error);
        updateConnectionStatus('disconnected', 'Connection failed');
        showToast('Failed to connect. Make sure the sheet is shared or you have access.', 'error');
    }
}

function extractSheetId(url) {
    // Handle various Google Sheets URL formats
    const patterns = [
        /\/spreadsheets\/d\/([a-zA-Z0-9-_]+)/,
        /\/d\/([a-zA-Z0-9-_]+)/,
        /spreadsheets\/d\/([a-zA-Z0-9-_]+)/,
    ];

    for (const pattern of patterns) {
        const match = url.match(pattern);
        if (match) {
            return match[1];
        }
    }

    return null;
}

async function fetchSheetMetadata(sheetId) {
    const url = `https://sheets.googleapis.com/v4/spreadsheets/${sheetId}`;

    const response = await fetch(url, {
        headers: {
            Authorization: `Bearer ${state.accessToken}`,
        },
    });

    if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
    }

    return response.json();
}

async function fetchSheetData(sheetId, sheetName) {
    // Fetch first 10 rows to understand structure
    const range = `'${sheetName}'!A1:Z10`;
    const url = `https://sheets.googleapis.com/v4/spreadsheets/${sheetId}/values/${encodeURIComponent(range)}`;

    const response = await fetch(url, {
        headers: {
            Authorization: `Bearer ${state.accessToken}`,
        },
    });

    if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    return analyzeSheetStructure(data.values || []);
}

function analyzeSheetStructure(values) {
    if (!values || values.length === 0) {
        return {
            columns: [],
            sampleData: [],
            hasHeaders: false,
        };
    }

    const headers = values[0] || [];
    const dataRows = values.slice(1);

    // Try to determine if first row is headers
    const hasHeaders = headers.some(h => typeof h === 'string' && isNaN(h));

    // Analyze column types
    const columns = headers.map((header, index) => {
        const columnLetter = String.fromCharCode(65 + index);
        const sampleValues = dataRows.map(row => row[index]).filter(v => v !== undefined);

        return {
            letter: columnLetter,
            name: hasHeaders ? header : `Column ${columnLetter}`,
            type: inferColumnType(sampleValues),
            sample: sampleValues.slice(0, 3),
        };
    });

    return {
        columns,
        sampleData: dataRows.slice(0, 5),
        hasHeaders,
    };
}

function inferColumnType(values) {
    if (values.length === 0) return 'unknown';

    const types = values.map(v => {
        if (v === null || v === undefined || v === '') return 'empty';
        if (!isNaN(v) && !isNaN(parseFloat(v))) return 'number';
        if (isDateString(v)) return 'date';
        return 'text';
    });

    // Return most common type
    const typeCounts = types.reduce((acc, type) => {
        acc[type] = (acc[type] || 0) + 1;
        return acc;
    }, {});

    delete typeCounts.empty;

    const sortedTypes = Object.entries(typeCounts).sort((a, b) => b[1] - a[1]);
    return sortedTypes.length > 0 ? sortedTypes[0][0] : 'text';
}

function isDateString(value) {
    const datePatterns = [
        /^\d{1,2}\/\d{1,2}\/\d{2,4}$/,
        /^\d{4}-\d{2}-\d{2}$/,
        /^\d{1,2}-\d{1,2}-\d{2,4}$/,
    ];
    return datePatterns.some(p => p.test(value));
}

function showSheetInfo() {
    elements.sheetSelector?.classList.add('hidden');
    elements.sheetInfo?.classList.remove('hidden');

    if (elements.sheetName) {
        elements.sheetName.textContent = state.connectedSheet.title;
    }

    if (elements.sheetColumns && state.sheetData) {
        const columnInfo = state.sheetData.columns
            .map(c => `${c.letter} (${c.name}, ${c.type})`)
            .join(', ');
        elements.sheetColumns.textContent = `Columns: ${columnInfo}`;
    }

    updateConnectionStatus('connected', `Connected to "${state.connectedSheet.title}"`);
}

function handleDisconnect() {
    state.connectedSheet = null;
    state.sheetData = null;

    elements.sheetInfo?.classList.add('hidden');
    elements.sheetSelector?.classList.remove('hidden');
    elements.resultSection?.classList.add('hidden');

    if (elements.sheetUrl) {
        elements.sheetUrl.value = '';
    }

    updateConnectionStatus('signed-in', 'Signed in - Paste a sheet URL below');
    showToast('Sheet disconnected', 'success');
}

// ================================
// Claude AI Integration
// ================================

function handleFormulaInput(e) {
    const length = e.target.value.length;
    if (elements.charCount) {
        elements.charCount.textContent = length;
    }
}

async function handleGenerateFormula() {
    const request = elements.formulaRequest?.value?.trim();

    if (!request) {
        showToast('Please describe what you want to calculate', 'error');
        return;
    }

    if (request.length < 10) {
        showToast('Please provide more detail about what you need', 'error');
        return;
    }

    setLoadingState(true);

    try {
        const result = await generateFormulaWithClaude(request);
        displayResult(result);
        showToast('Formula generated!', 'success');
    } catch (error) {
        console.error('Generation failed:', error);
        showToast('Failed to generate formula. Please try again.', 'error');
    } finally {
        setLoadingState(false);
    }
}

async function generateFormulaWithClaude(userRequest) {
    // Build context about the sheet
    let sheetContext = '';

    if (state.sheetData && state.sheetData.columns.length > 0) {
        sheetContext = `
The user has connected a Google Sheet with the following structure:
${state.sheetData.columns.map(c => `- Column ${c.letter}: "${c.name}" (${c.type} data)${c.sample.length > 0 ? `, sample values: ${c.sample.join(', ')}` : ''}`).join('\n')}

Use these actual column letters and names in your formula.
`;
    }

    const systemPrompt = `You are an expert Google Sheets formula assistant. Your job is to convert natural language requests into working Google Sheets formulas.

${sheetContext}

Guidelines:
1. Always return valid Google Sheets formulas (not Excel)
2. Use the actual column letters from the user's sheet when available
3. Prefer simple formulas when possible
4. For complex operations, consider QUERY, ARRAYFORMULA, or combining functions
5. Always explain how the formula works in simple terms

Respond in this exact JSON format:
{
  "formula": "=YOUR_FORMULA_HERE",
  "explanation": "A clear explanation of how this formula works and what each part does."
}

Only respond with the JSON, no additional text.`;

    const userMessage = `Generate a Google Sheets formula for: "${userRequest}"`;

    // Check if we should use real API or mock
    if (CONFIG.CLAUDE_API_KEY.includes('YOUR_')) {
        // Return mock response for demo
        return generateMockResponse(userRequest);
    }

    // Call Claude API
    const response = await fetch(CONFIG.CLAUDE_API_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'x-api-key': CONFIG.CLAUDE_API_KEY,
            'anthropic-version': '2023-06-01',
            'anthropic-dangerous-direct-browser-access': 'true',
        },
        body: JSON.stringify({
            model: 'claude-sonnet-4-20250514',
            max_tokens: 1024,
            system: systemPrompt,
            messages: [
                { role: 'user', content: userMessage }
            ],
        }),
    });

    if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    const content = data.content[0].text;

    // Parse JSON response
    try {
        return JSON.parse(content);
    } catch {
        // If JSON parsing fails, try to extract formula
        return {
            formula: content.match(/=.+/)?.[0] || content,
            explanation: 'Generated formula based on your request.',
        };
    }
}

function generateMockResponse(request) {
    // Mock responses for demo when API key is not configured
    const lowerRequest = request.toLowerCase();

    if (lowerRequest.includes('sum') && lowerRequest.includes('if')) {
        return {
            formula: '=SUMIF(C:C,"West",B:B)',
            explanation: 'This SUMIF formula adds up all values in column B (your numeric data) where the corresponding cell in column C matches "West". SUMIF takes three arguments: the range to check (C:C), the criteria ("West"), and the range to sum (B:B).',
        };
    }

    if (lowerRequest.includes('average')) {
        return {
            formula: '=AVERAGE(B:B)',
            explanation: 'This formula calculates the arithmetic mean of all numeric values in column B. Empty cells and text values are automatically ignored.',
        };
    }

    if (lowerRequest.includes('count')) {
        return {
            formula: '=COUNTIF(A:A,"<>")',
            explanation: 'This formula counts all non-empty cells in column A. The "<>" criteria means "not empty". Use COUNTA(A:A) for a simpler alternative.',
        };
    }

    if (lowerRequest.includes('vlookup') || lowerRequest.includes('lookup')) {
        return {
            formula: '=VLOOKUP(E2,A:C,2,FALSE)',
            explanation: 'VLOOKUP searches for the value in E2 within the first column of range A:C, and returns the value from the 2nd column of that range. FALSE means exact match only.',
        };
    }

    if (lowerRequest.includes('date') || lowerRequest.includes('today')) {
        return {
            formula: '=IF(A2<TODAY(),"Overdue","On Track")',
            explanation: 'This formula compares the date in A2 to today\'s date. If A2 is before today, it shows "Overdue", otherwise "On Track".',
        };
    }

    // Default response
    return {
        formula: '=SUM(B:B)',
        explanation: 'This formula sums all numeric values in column B. For more specific calculations, try describing which columns to use and any conditions to apply.',
    };
}

function displayResult(result) {
    elements.resultSection?.classList.remove('hidden');

    if (elements.formulaOutput) {
        elements.formulaOutput.textContent = result.formula;
    }

    if (elements.explanationOutput) {
        elements.explanationOutput.textContent = result.explanation;
    }

    // Scroll to result
    elements.resultSection?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

async function handleCopyFormula() {
    const formula = elements.formulaOutput?.textContent;

    if (!formula) return;

    try {
        await navigator.clipboard.writeText(formula);
        showToast('Formula copied to clipboard!', 'success');

        // Update button text temporarily
        if (elements.copyBtn) {
            const originalText = elements.copyBtn.innerHTML;
            elements.copyBtn.innerHTML = '<span class="copy-icon">✓</span> Copied!';
            setTimeout(() => {
                elements.copyBtn.innerHTML = originalText;
            }, 2000);
        }
    } catch (error) {
        console.error('Copy failed:', error);
        showToast('Failed to copy. Please select and copy manually.', 'error');
    }
}

// ================================
// UI Helpers
// ================================

function updateConnectionStatus(status, message) {
    const statusDot = elements.connectionStatus?.querySelector('.status-dot');
    const statusText = elements.connectionStatus?.querySelector('span');

    if (statusDot) {
        statusDot.className = 'status-dot';
        if (status === 'connected') statusDot.classList.add('connected');
        else if (status === 'loading') statusDot.classList.add('loading');
        else statusDot.classList.add('disconnected');
    }

    if (statusText) {
        statusText.textContent = message;
    }
}

function setLoadingState(isLoading) {
    state.isLoading = isLoading;

    const btnText = elements.generateBtn?.querySelector('.btn-text');
    const btnLoading = elements.generateBtn?.querySelector('.btn-loading');

    if (isLoading) {
        elements.generateBtn?.setAttribute('disabled', 'true');
        btnText?.classList.add('hidden');
        btnLoading?.classList.remove('hidden');
    } else {
        elements.generateBtn?.removeAttribute('disabled');
        btnText?.classList.remove('hidden');
        btnLoading?.classList.add('hidden');
    }
}

function showToast(message, type = 'info') {
    // Remove existing toasts
    document.querySelectorAll('.toast').forEach(t => t.remove());

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;

    document.body.appendChild(toast);

    // Auto-remove after 3 seconds
    setTimeout(() => {
        toast.remove();
    }, 3000);
}
