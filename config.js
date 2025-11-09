// Supabase Configuration
// This file initializes Supabase client

// For development: You can hardcode values here temporarily
// For production: Use environment variables (Vercel will inject them)

const SUPABASE_URL = window.ENV?.SUPABASE_URL || 'YOUR_SUPABASE_URL_HERE';
const SUPABASE_ANON_KEY = window.ENV?.SUPABASE_ANON_KEY || 'YOUR_SUPABASE_ANON_KEY_HERE';

// Initialize Supabase client
let supabase;

try {
    if (SUPABASE_URL.includes('YOUR_SUPABASE') || SUPABASE_ANON_KEY.includes('YOUR_SUPABASE')) {
        console.warn('⚠️ Supabase not configured! Using demo mode with localStorage.');
        console.log('📝 To enable Supabase:');
        console.log('1. Replace values in config.js with your Supabase credentials');
        console.log('2. Or deploy to Vercel with environment variables');
        supabase = null; // Will fallback to localStorage
    } else {
        const { createClient } = supabase;
        supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
        console.log('✅ Supabase initialized successfully!');
    }
} catch (error) {
    console.error('❌ Failed to initialize Supabase:', error);
    supabase = null;
}

// Check if Supabase is available
const isSupabaseEnabled = () => supabase !== null;
