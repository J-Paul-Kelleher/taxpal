// src/app/chat/page.tsx
'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { 
  Container, 
  Box, 
  Flex, 
  VStack,
  Button,
  Heading,
  Text,
  Divider
} from '@chakra-ui/react';
import { useAuth } from '@/context/AuthContext';
import { useChat } from '@/context/ChatContext';
import ChatMessage from '@/components/chat/ChatMessage';
import ChatInput from '@/components/chat/ChatInput';
import ChatDisclaimer from '@/components/chat/ChatDisclaimer';

export default function ChatPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const { 
    currentSession, 
    sendMessage, 
    createNewSession, 
    isLoading: chatLoading 
  } = useChat();
  
  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, authLoading, router]);
  
  if (authLoading) {
    return (
      <Container maxW="1200px" centerContent py={10}>
        <Text>Loading...</Text>
      </Container>
    );
  }
  
  if (!isAuthenticated) {
    return null; // Will redirect
  }
  
  return (
    <Container maxW="1200px" h="calc(100vh - 160px)">
      <Flex h="full" direction="column">
        <ChatDisclaimer />
        
        <Flex 
          flex="1" 
          direction="column" 
          bg="white" 
          borderRadius="md" 
          boxShadow="sm" 
          p={4}
          overflow="hidden"
        >
          <Flex justify="space-between" mb={4}>
            <Heading size="md">
              {currentSession?.title || 'New Chat'}
            </Heading>
            
            <Button 
              size="sm" 
              colorScheme="blue" 
              variant="outline"
              onClick={createNewSession}
            >
              New Chat
            </Button>
          </Flex>
          
          <Divider mb={4} />
          
          <VStack 
            flex="1" 
            spacing={4} 
            overflowY="auto" 
            px={2}
            align="stretch"
          >
            {currentSession && currentSession.messages.length > 0 ? (
              currentSession.messages.map(message => (
                <ChatMessage key={message.id} message={message} />
              ))
            ) : (
              <Flex 
                direction="column" 
                justify="center" 
                align="center" 
                h="full" 
                color="gray.500"
              >
                <Text fontSize="lg" fontWeight="medium">
                  No messages yet
                </Text>
                <Text fontSize="sm">
                  Start a conversation by asking a question about Irish tax legislation.
                </Text>
              </Flex>
            )}
          </VStack>
          
          <ChatInput 
            onSendMessage={sendMessage} 
            isLoading={chatLoading} 
          />
        </Flex>
      </Flex>
    </Container>
  );
}