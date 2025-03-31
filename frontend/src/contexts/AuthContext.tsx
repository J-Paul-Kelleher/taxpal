// src/contexts/AuthContext.tsx
'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { 
  getSupabaseClient,
  signIn as supabaseSignIn, 
  signUp as supabaseSignUp, 
  signOut as supabaseSignOut, 
  getCurrentUser,
  getSession,
  resetPassword as supabaseResetPassword,
  updatePassword as supabaseUpdatePassword
} from '@/utils/supabase';
import { Session, User } from '@supabase/supabase-js';

interface UserProfile {
  id: string;
  email: string;
  subscription_plan?: string;
  subscription_status?: string;
  is_admin: boolean;
  usage?: number;
  usage_limit?: number;
}

interface AuthContextType {
  user: User | null;
  profile: UserProfile | null;
  session: Session | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
  resetPassword: (email: string) => Promise<void>;
  updatePassword: (password: string) => Promise<void>;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  // Fetch user profile from the API
  const fetchProfile = async (token: string) => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/profile`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const profileData = await response.json();
        setProfile(profileData);
      } else {
        console.error('Failed to fetch user profile');
        setProfile(null);
      }
    } catch (error) {
      console.error('Error fetching profile:', error);
      setProfile(null);
    }
  };

  // Refresh the user's profile
  const refreshProfile = async () => {
    if (!session?.access_token) return;
    await fetchProfile(session.access_token);
  };

  // Set up authentication state listener
  useEffect(() => {
    const supabase = getSupabaseClient();
    
    const setupAuth = async () => {
      setLoading(true);
      
      // Get current session and user
      const currentSession = await getSession();
      setSession(currentSession);
      
      const currentUser = await getCurrentUser();
      setUser(currentUser);
      
      // Fetch profile if user is authenticated
      if (currentSession?.access_token) {
        await fetchProfile(currentSession.access_token);
      }
      
      // Listen for auth state changes
      const { data: authListener } = supabase.auth.onAuthStateChange(
        async (event, newSession) => {
          setSession(newSession);
          
          if (newSession) {
            const { data: { user } } = await supabase.auth.getUser();
            setUser(user);
            
            if (newSession.access_token) {
              await fetchProfile(newSession.access_token);
            } 
          } else {
            setUser(null);
            setProfile(null);
          }
        }
      );
      
      setLoading(false);
      
      // Clean up subscription on unmount
      return () => {
        authListener.subscription.unsubscribe();
      };
    };
    
    setupAuth();
  }, []);

  // Custom sign in function
  const handleSignIn = async (email: string, password: string) => {
    const data = await supabaseSignIn(email, password);
    if (data.session?.access_token) {
      await fetchProfile(data.session.access_token);
    }
  };

  // Custom sign up function
  const handleSignUp = async (email: string, password: string) => {
    await supabaseSignUp(email, password);
    // Profile will be fetched automatically when the auth state changes
  };

  // Custom sign out function
  const handleSignOut = async () => {
    await supabaseSignOut();
    setProfile(null);
  };

  // Custom reset password function
  const handleResetPassword = async (email: string) => {
    await supabaseResetPassword(email);
  };

  // Custom update password function
  const handleUpdatePassword = async (password: string) => {
    await supabaseUpdatePassword(password);
  };

  const value = {
    user,
    profile,
    session,
    loading,
    signIn: handleSignIn,
    signUp: handleSignUp,
    signOut: handleSignOut,
    resetPassword: handleResetPassword,
    updatePassword: handleUpdatePassword,
    refreshProfile
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}