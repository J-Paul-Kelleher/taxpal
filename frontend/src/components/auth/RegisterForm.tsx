'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useForm, SubmitHandler } from 'react-hook-form';
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
  Checkbox,
} from '@chakra-ui/react';

// Form validation schema
const registerSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .regex(
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/,
      'Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character'
    ),
  confirmPassword: z.string(),
  agreeToTerms: z.boolean().refine(val => val === true, {
    message: 'You must agree to the terms and conditions',
  }),
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Passwords do not match',
  path: ['confirmPassword'],
});

type RegisterFormValues = z.infer<typeof registerSchema>;

export default function RegisterForm() {
  const { signUp } = useAuth();
  const router = useRouter();
  const toast = useToast();
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      email: '',
      password: '',
      confirmPassword: '',
      agreeToTerms: false,
    },
  });

  const onSubmit: SubmitHandler<RegisterFormValues> = async (data) => {
    try {
      setIsLoading(true);
      await signUp(data.email, data.password);
      
      toast({
        title: 'Registration successful',
        description: 'Please check your email to confirm your account',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
      
      router.push('/login');
    } catch (error) {
      let errorMessage = 'An error occurred during registration';
      
      if (error instanceof Error) {
        errorMessage = error.message;
      }
      
      toast({
        title: 'Registration failed',
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
          Create an account
        </Heading>
        <Text textAlign="center" color="gray.600">
          Sign up to start using TaxPal
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
            
            <FormControl isInvalid={!!errors.confirmPassword}>
              <FormLabel>Confirm Password</FormLabel>
              <Input
                type="password"
                placeholder="********"
                {...register('confirmPassword')}
              />
              <FormErrorMessage>{errors.confirmPassword?.message}</FormErrorMessage>
            </FormControl>
            
            <FormControl isInvalid={!!errors.agreeToTerms}>
              <Checkbox {...register('agreeToTerms')}>
                I agree to the{' '}
                <Link href="/terms-of-service">
                  <Text as="span" color="blue.500">
                    Terms of Service
                  </Text>
                </Link>{' '}
                and{' '}
                <Link href="/privacy-policy">
                  <Text as="span" color="blue.500">
                    Privacy Policy
                  </Text>
                </Link>
              </Checkbox>
              <FormErrorMessage>{errors.agreeToTerms?.message}</FormErrorMessage>
            </FormControl>
            
            <Button
              type="submit"
              colorScheme="blue"
              size="lg"
              isLoading={isLoading}
              loadingText="Creating account"
              width="full"
              mt={4}
            >
              Create account
            </Button>
            
            <Text textAlign="center">
              Already have an account?{' '}
              <Link href="/login">
                <Text as="span" color="blue.500">
                  Log in
                </Text>
              </Link>
            </Text>
          </Stack>
        </form>
      </Stack>
    </Box>
  );
}