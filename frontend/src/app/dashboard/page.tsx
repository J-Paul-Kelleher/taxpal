import { Metadata } from 'next';
import { Container, Grid, GridItem, Heading, Box, Text } from '@chakra-ui/react';
import UserProfile from '@/components/auth/UserProfile';

export const metadata: Metadata = {
  title: 'Dashboard | TaxPal',
  description: 'Ask questions about Irish tax legislation',
};

export default function DashboardPage() {
  return (
    <Container maxW="container.xl" py={6}>
      <Heading as="h1" size="xl" mb={6}>
        TaxPal Dashboard
      </Heading>
      
      <Grid templateColumns={{ base: "1fr", md: "3fr 1fr" }} gap={6}>
        <GridItem>
          <Box p={5} borderWidth="1px" borderRadius="lg">
            <Heading as="h2" size="md" mb={4}>
              Ask about Irish Tax Legislation
            </Heading>
            {/* Placeholder for chat interface */}
            <Box height="500px" bg="gray.100" borderRadius="md" p={4} display="flex" justifyContent="center" alignItems="center">
              <Text color="gray.500" textAlign="center">
                Chat interface will be implemented in the next step
              </Text>
            </Box>
          </Box>
        </GridItem>
        
        <GridItem>
          <UserProfile />
        </GridItem>
      </Grid>
    </Container>
  );
}