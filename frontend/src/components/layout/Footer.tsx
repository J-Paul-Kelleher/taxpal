// src/components/layout/Footer.tsx
import React from 'react';
import { Box, Container, Text, Link, HStack } from '@chakra-ui/react';

const Footer: React.FC = () => {
  return (
    <Box as="footer" bg="gray.100" py={4} mt="auto">
      <Container maxW="1200px">
        <HStack justifyContent="space-between">
          <Text fontSize="sm" color="gray.500">
            © {new Date().getFullYear()} TaxPal. All rights reserved.
          </Text>
          
          <HStack spacing={4}>
            <Link href="/terms" fontSize="sm" color="gray.500">
              Terms of Service
            </Link>
            <Link href="/privacy" fontSize="sm" color="gray.500">
              Privacy Policy
            </Link>
          </HStack>
        </HStack>
      </Container>
    </Box>
  );
};

export default Footer;