const SUPABASE_URL = 'https://houlztopqujrgxtbwmyh.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhvdWx6dG9wcXVqcmd4dGJ3bXloIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY5Mzg1NTMsImV4cCI6MjA3MjUxNDU1M30.-eYbPW6pW2d-FjQHFe5OtoG0f61RmkXhXkU8HOIBXXU';

const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

const CONFIG = {
    ITEMS_PER_PAGE: 20,
    MAX_SEARCH_RESULTS: 1000,
    DEBOUNCE_DELAY: 300,
    API_TIMEOUT: 10000
};

if (typeof module !== 'undefined' && module.exports) {
    module.exports = { supabase, CONFIG };
}