// src/components/layout/Layout.tsx
import React from 'react';
import { Box, Flex } from '@chakra-ui/react';
import Header from './Header';
import Footer from './Footer';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <Flex direction="column" minH="100vh">
      <Header />
      <Box as="main" flex="1" py={8}>
        {children}
      </Box>
      <Footer />
    </Flex>
  );
};

export default Layout;