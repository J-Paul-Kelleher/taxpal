'use client';

import { useAuth } from '@/contexts/AuthContext';
import {
  Box,
  VStack,
  HStack,
  Heading,
  Text,
  Button,
  Divider,
  Badge,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Card,
  CardHeader,
  CardBody,
  useToast,
} from '@chakra-ui/react';

export default function UserProfile() {
  const { user, profile, signOut } = useAuth();
  const toast = useToast();

  const handleSignOut = async () => {
    try {
      await signOut();
      toast({
        title: 'Signed out successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      toast({
        title: 'Error signing out',
        description: 'Please try again',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    }
  };

  if (!user || !profile) {
    return (
      <Box p={5} textAlign="center">
        <Text>Loading profile...</Text>
      </Box>
    );
  }

  return (
    <Card boxShadow="md" borderRadius="lg">
      <CardHeader>
        <Heading size="md">User Profile</Heading>
      </CardHeader>
      <CardBody>
        <VStack spacing={6} align="stretch">
          <Box>
            <Heading size="sm" mb={2}>Account Information</Heading>
            <Text>Email: {user.email}</Text>
            <HStack mt={2}>
              <Badge colorScheme="green">Email {user.email_confirmed_at ? 'Verified' : 'Not Verified'}</Badge>
              {profile.is_admin && <Badge colorScheme="purple">Admin</Badge>}
            </HStack>
          </Box>
          
          <Divider />
          
          <Box>
            <Heading size="sm" mb={2}>Subscription</Heading>
            <HStack spacing={4}>
              <Stat>
                <StatLabel>Plan</StatLabel>
                <StatNumber>{profile.subscription_plan || 'Free'}</StatNumber>
                <StatHelpText>{profile.subscription_status || 'Active'}</StatHelpText>
              </Stat>
              
              <Stat>
                <StatLabel>Usage</StatLabel>
                <StatNumber>{profile.usage || 0} / {profile.usage_limit || 10}</StatNumber>
                <StatHelpText>Tokens</StatHelpText>
              </Stat>
            </HStack>
          </Box>
          
          <Divider />
          
          <Box>
            <Button colorScheme="red" onClick={handleSignOut}>
              Sign Out
            </Button>
          </Box>
        </VStack>
      </CardBody>
    </Card>
  );
}