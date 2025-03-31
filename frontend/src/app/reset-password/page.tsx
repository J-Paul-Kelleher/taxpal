import { Metadata } from 'next';
import ResetPasswordForm from '@/components/auth/ResetPasswordForm';
import { Box, Container } from '@chakra-ui/react';

export const metadata: Metadata = {
  title: 'Reset Password | TaxPal',
  description: 'Reset your TaxPal account password',
};

export default function ResetPasswordPage() {
  return (
    <Container maxW="container.xl" py={12}>
      <Box maxW="md" mx="auto">
        <ResetPasswordForm />
      </Box>
    </Container>
  );
}