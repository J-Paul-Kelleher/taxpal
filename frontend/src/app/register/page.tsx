import { Metadata } from 'next';
import RegisterForm from '@/components/auth/RegisterForm';
import { Box, Container } from '@chakra-ui/react';

export const metadata: Metadata = {
  title: 'Register | TaxPal',
  description: 'Create a new TaxPal account',
};

export default function RegisterPage() {
  return (
    <Container maxW="container.xl" py={12}>
      <Box maxW="md" mx="auto">
        <RegisterForm />
      </Box>
    </Container>
  );
}