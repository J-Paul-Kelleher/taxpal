// src/types/index.ts

// User types
export interface User {
    id: string;
    email: string;
    role: string;
    subscription_plan_id?: string;
    subscription_status?: string;
    current_period_usage?: number;
    usage_limit?: number;
  }
  
  // Auth types
  export interface AuthState {
    user: User | null;
    session: any | null;
    isLoading: boolean;
    isAuthenticated: boolean;
  }
  
  // Chat types
  export interface Citation {
    source: string;
    text: string;
    reference: string;
  }
  
  export interface ChatMessage {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    citations?: Citation[];
    tokens_used?: number;
    timestamp: number;
  }
  
  export interface ChatSession {
    id: string;
    title: string;
    messages: ChatMessage[];
    created_at: number;
  }
  
  // Subscription types
  export interface SubscriptionPlan {
    id: string;
    name: string;
    monthly_price: number;
    yearly_price: number;
    token_limit: number;
    features: any;
    is_active: boolean;
  }