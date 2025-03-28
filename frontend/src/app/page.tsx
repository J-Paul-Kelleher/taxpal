'use client';

import { Box, Container, Heading, Text, Button, VStack, Flex, Image } from '@chakra-ui/react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';

export default function Home() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  
  return (
    <Container maxW="1200px">
      <Flex
        direction={{ base: 'column', md: 'row' }}
        align="center"
        justify="space-between"
        py={16}
        gap={8}
      >
        <VStack align="flex-start" spacing={6} maxW="600px">
          <Heading as="h1" size="2xl">
            Irish Tax Legislation Made Simple
          </Heading>
          
          <Text fontSize="xl" color="gray.600">
            TaxPal helps you navigate the complex world of Irish tax legislation with accurate, cited information from official sources.
          </Text>
          
          <Button 
            size="lg" 
            colorScheme="blue"
            onClick={() => router.push(isAuthenticated ? '/chat' : '/signup')}
          >
            {isAuthenticated ? 'Start Chatting' : 'Get Started for Free'}
          </Button>
          
          <Text fontSize="sm" color="gray.500">
            Free tier includes 10 messages per week.
          </Text>
        </VStack>
        
        <Box 
          w={{ base: "100%", md: "450px" }}
          h="300px"
          bg="gray.200"
          borderRadius="md"
          display="flex"
          alignItems="center"
          justifyContent="center"
        >
          <Text color="gray.500">Illustration Placeholder</Text>
        </Box>
      </Flex>
      
      <Box py={16}>
        <Heading as="h2" size="xl" textAlign="center" mb={10}>
          How TaxPal Works
        </Heading>
        
        <Flex 
          direction={{ base: 'column', md: 'row' }}
          justify="space-between"
          gap={8}
        >
          <Box 
            p={6} 
            borderRadius="lg" 
            boxShadow="md" 
            bg="white" 
            flex="1"
          >
            <Heading as="h3" size="md" mb={4}>
              Ask Questions
            </Heading>
            <Text>
              Ask any question about Irish tax legislation in plain language.
            </Text>
          </Box>
          
          <Box 
            p={6} 
            borderRadius="lg" 
            boxShadow="md" 
            bg="white" 
            flex="1"
          >
            <Heading as="h3" size="md" mb={4}>
              Get Accurate Answers
            </Heading>
            <Text>
              Receive precise answers backed by official tax documentation.
            </Text>
          </Box>
          
          <Box 
            p={6} 
            borderRadius="lg" 
            boxShadow="md" 
            bg="white" 
            flex="1"
          >
            <Heading as="h3" size="md" mb={4}>
              See References
            </Heading>
            <Text>
              Every answer includes citations to relevant tax code sections.
            </Text>
          </Box>
        </Flex>
      </Box>
    </Container>
  );
}