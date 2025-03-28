// src/components/layout/Header.tsx
import React from 'react';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { 
  Box, 
  Flex, 
  Button, 
  Heading, 
  Spacer, 
  HStack 
} from '@chakra-ui/react';

const Header: React.FC = () => {
  const { isAuthenticated, signOut } = useAuth();

  return (
    <Box as="header" bg="blue.700" color="white" px={4} py={2}>
      <Flex align="center" maxW="1200px" mx="auto">
        <Heading as="h1" size="md">
          <Link href="/">TaxPal</Link>
        </Heading>
        
        <Spacer />
        
        <HStack spacing={4}>
          {isAuthenticated ? (
            <>
              <Button as={Link} href="/chat" variant="ghost" colorScheme="whiteAlpha">
                Chat
              </Button>
              <Button as={Link} href="/profile" variant="ghost" colorScheme="whiteAlpha">
                Profile
              </Button>
              <Button onClick={signOut} variant="outline" colorScheme="whiteAlpha">
                Sign Out
              </Button>
            </>
          ) : (
            <>
              <Button as={Link} href="/login" variant="ghost" colorScheme="whiteAlpha">
                Login
              </Button>
              <Button as={Link} href="/signup" variant="solid" colorScheme="blue">
                Sign Up
              </Button>
            </>
          )}
        </HStack>
      </Flex>
    </Box>
  );
};

export default Header;