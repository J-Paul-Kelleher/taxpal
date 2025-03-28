// src/components/chat/ChatDisclaimer.tsx
import React from 'react';
import { Box, Text, Alert, AlertIcon } from '@chakra-ui/react';

const ChatDisclaimer: React.FC = () => {
  return (
    <Alert status="info" mb={4} borderRadius="md">
      <AlertIcon />
      <Text fontSize="sm">
        This information is provided for general guidance only and does not constitute formal legal advice. 
        For definitive guidance, please consult with a qualified tax professional or contact the Irish Revenue Commissioners.
      </Text>
    </Alert>
  );
};

export default ChatDisclaimer;