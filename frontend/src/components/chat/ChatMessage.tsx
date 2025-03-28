// src/components/chat/ChatMessage.tsx
import React from 'react';
import { Box, Text, Flex, Badge, Tooltip } from '@chakra-ui/react';
import { ChatMessage as ChatMessageType } from '@/types';

interface ChatMessageProps {
  message: ChatMessageType;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';
  
  return (
    <Box
      mb={4}
      p={4}
      borderRadius="md"
      bg={isUser ? 'blue.50' : 'gray.50'}
      alignSelf={isUser ? 'flex-end' : 'flex-start'}
      maxW="80%"
    >
      <Flex direction="column">
        <Text fontWeight="bold" mb={1} color={isUser ? 'blue.600' : 'gray.600'}>
          {isUser ? 'You' : 'TaxPal'}
        </Text>
        
        <Text>{message.content}</Text>
        
        {message.citations && message.citations.length > 0 && (
          <Box mt={3}>
            <Text fontWeight="bold" fontSize="sm" color="gray.600" mb={1}>
              Citations:
            </Text>
            {message.citations.map((citation, index) => (
              <Tooltip 
                key={index} 
                label={citation.text} 
                placement="top"
                maxW="400px"
              >
                <Badge 
                  colorScheme="blue" 
                  mr={2} 
                  mb={1}
                  p={1}
                  borderRadius="md"
                  cursor="pointer"
                >
                  {citation.source} {citation.reference}
                </Badge>
              </Tooltip>
            ))}
          </Box>
        )}
        
        {message.tokens_used && (
          <Text fontSize="xs" color="gray.500" mt={2} alignSelf="flex-end">
            Tokens used: {message.tokens_used}
          </Text>
        )}
      </Flex>
    </Box>
  );
};

export default ChatMessage;