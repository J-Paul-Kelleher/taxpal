// src/components/chat/ChatInput.tsx
import React, { useState } from 'react';
import { 
  Box, 
  Textarea, 
  Button, 
  Flex,
  IconButton,
  Tooltip
} from '@chakra-ui/react';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage, isLoading }) => {
  const [message, setMessage] = useState('');
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (message.trim() && !isLoading) {
      onSendMessage(message);
      setMessage('');
    }
  };
  
  return (
    <Box as="form" onSubmit={handleSubmit} mt={4}>
      <Flex>
        <Textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Ask about Irish tax legislation..."
          resize="none"
          rows={3}
          mr={2}
          disabled={isLoading}
        />
        
        <Button
          type="submit"
          colorScheme="blue"
          isLoading={isLoading}
          loadingText="Sending"
          alignSelf="flex-end"
          disabled={!message.trim() || isLoading}
        >
          Send
        </Button>
      </Flex>
    </Box>
  );
};

export default ChatInput;