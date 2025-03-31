// src/components/auth/LoginForm.tsx
'use client';

import { useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
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
  Checkbox,
  Flex,
} from '@chakra-ui/react';

// Form validation schema
const loginSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  rememberMe: z.boolean().optional(),
});

type LoginFormValues = z.infer<typeof loginSchema>;

// Import the AuthContext from the correct location
// Make sure this path matches your actual file structure
import { useAuth } from '../../contexts/AuthContext';

export default function LoginForm() {
  const { signIn } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirectPath = searchParams.get('redirect') || '/dashboard';
  const toast = useToast();
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
      rememberMe: false,
    },
  });

  const onSubmit = async (data: LoginFormValues) => {
    try {
      setIsLoading(true);
      await signIn(data.email, data.password);
      
      toast({
        title: 'Login successful',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      
      router.push(redirectPath);
    } catch (error) {
      let errorMessage = 'An error occurred during login';
      
      if (error instanceof Error) {
        errorMessage = error.message;
      }
      
      toast({
        title: 'Login failed',
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
          Welcome back
        </Heading>
        <Text textAlign="center" color="gray.600">
          Log in to your account
        </Text>
        
        <form onSubmit={handleSubmit(onSubmit)}>
          <Stack spacing={4}>
            <FormControl isInvalid={!!errors.email}>
              <FormLabel>Email</FormLabel>
              <Input
                type="email"
                placeholder="your.email@example.com"
                {...register('email')}
              />
              <FormErrorMessage>{errors.email?.message}</FormErrorMessage>
            </FormControl>
            
            <FormControl isInvalid={!!errors.password}>
              <FormLabel>Password</FormLabel>
              <Input
                type="password"
                placeholder="********"
                {...register('password')}
              />
              <FormErrorMessage>{errors.password?.message}</FormErrorMessage>
            </FormControl>
            
            <Flex justify="space-between" align="center">
              <Checkbox {...register('rememberMe')}>Remember me</Checkbox>
              <Link href="/reset-password">
                <Text color="blue.500" fontSize="sm">
                  Forgot password?
                </Text>
              </Link>
            </Flex>
            
            <Button
              type="submit"
              colorScheme="blue"
              size="lg"
              isLoading={isLoading}
              loadingText="Logging in"
              width="full"
            >
              Log in
            </Button>
            
            <Text textAlign="center">
              Don&apos;t have an account?{' '}
              <Link href="/register">
                <Text as="span" color="blue.500">
                  Sign up
                </Text>
              </Link>
            </Text>
          </Stack>
        </form>
      </Stack>
    </Box>
  );
}