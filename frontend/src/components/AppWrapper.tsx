// src/components/AppWrapper.tsx
'use client';

import React from 'react';
import { ChakraProvider } from '@chakra-ui/react';
import { AuthProvider } from '@/context/AuthContext';
import { ChatProvider } from '@/context/ChatContext';
import Layout from '@/components/layout/Layout';

interface AppWrapperProps {
  children: React.ReactNode;
}

const AppWrapper: React.FC<AppWrapperProps> = ({ children }) => {
  return (
    <ChakraProvider>
      <AuthProvider>
        <ChatProvider>
          <Layout>
            {children}
          </Layout>
        </ChatProvider>
      </AuthProvider>
    </ChakraProvider>
  );
};

export default AppWrapper;