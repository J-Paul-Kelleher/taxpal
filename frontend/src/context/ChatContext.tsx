// src/context/ChatContext.tsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { ChatMessage, ChatSession, Citation } from '@/types';
import { chatApi } from '@/services/api';
import { useAuth } from './AuthContext';

interface ChatContextType {
  currentSession: ChatSession | null;
  sessions: ChatSession[];
  isLoading: boolean;
  error: string | null;
  createNewSession: () => void;
  sendMessage: (message: string) => Promise<void>;
  setCurrentSession: (sessionId: string) => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const ChatProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Initialize with a default session if authenticated
  useEffect(() => {
    if (isAuthenticated && sessions.length === 0) {
      createNewSession();
    }
  }, [isAuthenticated]);

  const createNewSession = () => {
    const newSession: ChatSession = {
      id: uuidv4(),
      title: 'New Chat',
      messages: [],
      created_at: Date.now(),
    };
    
    setSessions(prev => [newSession, ...prev]);
    setCurrentSession(newSession);
  };

  const selectSession = (sessionId: string) => {
    const session = sessions.find(s => s.id === sessionId);
    if (session) {
      setCurrentSession(session);
    }
  };

  const sendMessage = async (content: string) => {
    if (!currentSession) return;
    
    // Create user message
    const userMessage: ChatMessage = {
      id: uuidv4(),
      role: 'user',
      content,
      timestamp: Date.now(),
    };
    
    // Update session with user message
    const updatedSession = {
      ...currentSession,
      messages: [...currentSession.messages, userMessage],
    };
    
    setCurrentSession(updatedSession);
    updateSession(updatedSession);
    
    // Send to API
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await chatApi.sendMessage(content, currentSession.id);
      
      // Create assistant message
      const assistantMessage: ChatMessage = {
        id: uuidv4(),
        role: 'assistant',
        content: response.response,
        citations: response.citations,
        tokens_used: response.tokens_used,
        timestamp: Date.now(),
      };
      
      // Update session with assistant message
      const finalSession = {
        ...updatedSession,
        messages: [...updatedSession.messages, assistantMessage],
      };
      
      setCurrentSession(finalSession);
      updateSession(finalSession);
    } catch (err: any) {
      setError(err.message || 'Failed to send message');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };
  
  const updateSession = (session: ChatSession) => {
    setSessions(prev => 
      prev.map(s => s.id === session.id ? session : s)
    );
  };

  return (
    <ChatContext.Provider
      value={{
        currentSession,
        sessions,
        isLoading,
        error,
        createNewSession,
        sendMessage,
        setCurrentSession: selectSession,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};