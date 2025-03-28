'use client';

import { useRouter } from 'next/navigation';
import {
  Container,
  Box,
  Heading,
  Text,
  Button,
  VStack,
  Icon,
} from '@chakra-ui/react';
import { CheckCircleIcon } from '@chakra-ui/icons';

export default function SignupSuccessPage() {
  const router = useRouter();
  
  return (
    <Container maxW="md" py={12}>
      <Box p={8} borderWidth={1} borderRadius="lg" boxShadow="lg" textAlign="center">
        <VStack spacing={6}>
          <Icon as={CheckCircleIcon} w={16} h={16} color="green.500" />
          
          <Heading>Sign Up Successful!</Heading>
          
          <Text>
            Thank you for signing up with TaxPal. Please check your email to verify your account.
          </Text>
          
          <Button
            colorScheme="blue"
            onClick={() => router.push('/login')}
            size="lg"
            width="full"
          >
            Go to Login
          </Button>
        </VStack>
      </Box>
    </Container>
  );
}