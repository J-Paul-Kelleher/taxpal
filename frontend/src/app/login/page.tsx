import { Metadata } from 'next';
import LoginForm from '@/components/auth/LoginForm';
import { Box, Container, Heading } from '@chakra-ui/react';

export const metadata: Metadata = {
  title: 'Login | TaxPal',
  description: 'Log in to your TaxPal account',
};

export default function LoginPage() {
  return (
    <Container maxW="container.xl" py={12}>
      <Box maxW="md" mx="auto">
        <LoginForm />
      </Box>
    </Container>
  );
}