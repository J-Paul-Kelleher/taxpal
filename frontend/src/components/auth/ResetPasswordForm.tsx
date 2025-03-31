'use client';

import { useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useAuth } from '@/contexts/AuthContext';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  FormErrorMessage,
  Stack,
  Heading,
  Text,
  useToast,
} from '@chakra-ui/react';

// Request reset schema (step 1)
const requestResetSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
});

// Set new password schema (step 2)
const resetPasswordSchema = z
  .object({
    password: z
      .string()
      .min(8, 'Password must be at least 8 characters')
      .regex(
        /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/,
        'Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character'
      ),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  });

type RequestResetFormValues = z.infer<typeof requestResetSchema>;
type ResetPasswordFormValues = z.infer<typeof resetPasswordSchema>;

export default function ResetPasswordForm() {
  const { resetPassword, updatePassword } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const toast = useToast();
  const [isLoading, setIsLoading] = useState(false);
  
  // Check if this is the confirmation step (with token in URL)
  const hasResetToken = !!searchParams.get('token');

  // Form for requesting password reset
  const requestResetForm = useForm<RequestResetFormValues>({
    resolver: zodResolver(requestResetSchema),
    defaultValues: {
      email: '',
    },
  });

  // Form for setting new password
  const resetPasswordForm = useForm<ResetPasswordFormValues>({
    resolver: zodResolver(resetPasswordSchema),
    defaultValues: {
      password: '',
      confirmPassword: '',
    },
  });

  const handleRequestReset = async (data: RequestResetFormValues) => {
    try {
      setIsLoading(true);
      await resetPassword(data.email);
      
      toast({
        title: 'Reset email sent',
        description: 'Please check your email for a link to reset your password',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
    } catch (error) {
      let errorMessage = 'An error occurred while sending the reset email';
      
      if (error instanceof Error) {
        errorMessage = error.message;
      }
      
      toast({
        title: 'Reset request failed',
        description: errorMessage,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetPassword = async (data: ResetPasswordFormValues) => {
    try {
      setIsLoading(true);
      await updatePassword(data.password);
      
      toast({
        title: 'Password reset successful',
        description: 'Your password has been successfully updated',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      
      router.push('/login');
    } catch (error) {
      let errorMessage = 'An error occurred while resetting your password';
      
      if (error instanceof Error) {
        errorMessage = error.message;
      }
      
      toast({
        title: 'Password reset failed',
        description: errorMessage,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box maxW="md" mx="auto" p={6} borderWidth="1px" borderRadius="lg">
      <Stack spacing={6}>
        <Heading as="h1" size="lg" textAlign="center">
          {hasResetToken ? 'Reset Your Password' : 'Forgot Password'}
        </Heading>
        <Text textAlign="center" color="gray.600">
          {hasResetToken
            ? 'Enter your new password below'
            : 'Enter your email and we\'ll send you a link to reset your password'}
        </Text>
        
        {hasResetToken ? (
          <form onSubmit={resetPasswordForm.handleSubmit(handleResetPassword)}>
            <Stack spacing={4}>
              <FormControl isInvalid={!!resetPasswordForm.formState.errors.password}>
                <FormLabel>New Password</FormLabel>
                <Input
                  type="password"
                  placeholder="********"
                  {...resetPasswordForm.register('password')}
                />
                <FormErrorMessage>
                  {resetPasswordForm.formState.errors.password?.message}
                </FormErrorMessage>
              </FormControl>
              
              <FormControl isInvalid={!!resetPasswordForm.formState.errors.confirmPassword}>
                <FormLabel>Confirm New Password</FormLabel>
                <Input
                  type="password"
                  placeholder="********"
                  {...resetPasswordForm.register('confirmPassword')}
                />
                <FormErrorMessage>
                  {resetPasswordForm.formState.errors.confirmPassword?.message}
                </FormErrorMessage>
              </FormControl>
              
              <Button
                type="submit"
                colorScheme="blue"
                size="lg"
                isLoading={isLoading}
                loadingText="Resetting password"
                width="full"
                mt={4}
              >
                Reset Password
              </Button>
            </Stack>
          </form>
        ) : (
          <form onSubmit={requestResetForm.handleSubmit(handleRequestReset)}>
            <Stack spacing={4}>
              <FormControl isInvalid={!!requestResetForm.formState.errors.email}>
                <FormLabel>Email</FormLabel>
                <Input
                  type="email"
                  placeholder="your.email@example.com"
                  {...requestResetForm.register('email')}
                />
                <FormErrorMessage>
                  {requestResetForm.formState.errors.email?.message}
                </FormErrorMessage>
              </FormControl>
              
              <Button
                type="submit"
                colorScheme="blue"
                size="lg"
                isLoading={isLoading}
                loadingText="Sending reset link"
                width="full"
                mt={4}
              >
                Send Reset Link
              </Button>
              
              <Text textAlign="center">
                Remember your password?{' '}
                <Link href="/login">
                  <Text as="span" color="blue.500">
                    Log in
                  </Text>
                </Link>
              </Text>
            </Stack>
          </form>
        )}
      </Stack>
    </Box>
  );
}