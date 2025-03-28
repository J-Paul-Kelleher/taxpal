// src/services/supabase.ts
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

// Check if environment variables are defined
if (!supabaseUrl || !supabaseKey) {
  console.error('Missing Supabase environment variables. Please check your .env file.');
}

export const supabase = createClient(
  supabaseUrl || '',
  supabaseKey || '', 
  {
    auth: {
      persistSession: true,
      autoRefreshToken: true,
    }
  }
);