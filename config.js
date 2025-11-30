// SheetGenius Configuration
// =========================
// IMPORTANT: Replace these with your actual API keys before deploying
// For production, these should be handled server-side!

const CONFIG = {
    // Google Cloud Console: https://console.cloud.google.com/
    // 1. Create a new project
    // 2. Enable Google Sheets API
    // 3. Create OAuth 2.0 credentials (Web application)
    // 4. Add your domain to authorized JavaScript origins
    GOOGLE_CLIENT_ID: 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com',

    // Google API Key (for Sheets API)
    // Create in Google Cloud Console > APIs & Services > Credentials
    GOOGLE_API_KEY: 'YOUR_GOOGLE_API_KEY',

    // Claude API Key from: https://console.anthropic.com/
    // WARNING: In production, NEVER expose this client-side!
    // Use a backend proxy instead
    CLAUDE_API_KEY: 'YOUR_CLAUDE_API_KEY',

    // API endpoints
    CLAUDE_API_URL: 'https://api.anthropic.com/v1/messages',

    // Scopes for Google OAuth
    GOOGLE_SCOPES: 'https://www.googleapis.com/auth/spreadsheets.readonly',

    // Discovery doc for Sheets API
    GOOGLE_DISCOVERY_DOC: 'https://sheets.googleapis.com/$discovery/rest?version=v4',
};

// Validation helper
function validateConfig() {
    const issues = [];

    if (CONFIG.GOOGLE_CLIENT_ID.includes('YOUR_')) {
        issues.push('Google Client ID not configured');
    }
    if (CONFIG.GOOGLE_API_KEY.includes('YOUR_')) {
        issues.push('Google API Key not configured');
    }
    if (CONFIG.CLAUDE_API_KEY.includes('YOUR_')) {
        issues.push('Claude API Key not configured');
    }

    return issues;
}
