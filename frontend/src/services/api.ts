// src/services/api.ts
import { supabase } from './supabase';
import { ChatMessage, Citation } from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// Helper function to get auth token
const getToken = async () => {
  const { data } = await supabase.auth.getSession();
  return data.session?.access_token || '';
};

// Helper function for API requests
const apiRequest = async (endpoint: string, method: string, data?: any) => {
  const token = await getToken();
  
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
  };
  
  const config: RequestInit = {
    method,
    headers,
    body: data ? JSON.stringify(data) : undefined,
  };
  
  const response = await fetch(`${API_URL}${endpoint}`, config);
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new Error(errorData?.detail || `API request failed with status ${response.status}`);
  }
  
  return response.json();
};

// Chat API functions
export const chatApi = {
  async sendMessage(query: string, sessionId?: string) {
    return apiRequest('/chat/ask', 'POST', { query, session_id: sessionId });
  },
};

// Auth API functions
export const authApi = {
  async verifyToken() {
    return apiRequest('/auth/verify-token', 'GET');
  },
};