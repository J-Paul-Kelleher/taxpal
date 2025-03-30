# TaxPal Authentication - Unified Implementation Guide

## Overview

This document provides the definitive guide for TaxPal's authentication implementation, superseding previous documentation in `auth-flow.md` and the auth sections in `tech-stack-versions.md`. It follows a hybrid approach that leverages Supabase for user-facing authentication while implementing minimal but secure backend validation.

## Core Principles

1. **Separation of Concerns**:
   - Supabase handles user management, credential verification, and JWT issuance
   - Backend only validates JWTs and extracts user context
   - Frontend handles the UI and token storage

2. **Minimize Custom Code**:
   - Use Supabase Auth Client SDK for all user-facing operations
   - Rely on Supabase Row Level Security (RLS) for database access control
   - Backend implements a single, standardized JWT validation middleware

3. **Stateless Authentication**:
   - JWT validation happens locally using Supabase's JWT secret
   - No direct API calls to Supabase Auth during validation
   - All necessary user context is extracted from the JWT payload

## Authentication Flow

### User Registration & Login

1. User interacts with Next.js Auth UI components
2. Auth requests are sent to Supabase Auth service via the Supabase Auth Client
3. Supabase Auth verifies credentials or creates new users
4. Supabase issues a JWT containing user identity and role information
5. JWT is stored securely in the browser by the Supabase client
6. React hooks make the auth state available throughout the frontend

### API Request Flow

1. Frontend includes the JWT in the Authorization header of API requests
2. FastAPI routes pass all requests through the JWT validation middleware
3. Middleware validates the JWT signature using the Supabase JWT secret
4. Middleware extracts user context (id, email, role) from the validated JWT
5. User context is passed to route handlers for authorization checks
6. Database queries apply RLS policies based on the user's identity and role

## Implementation Specifications

### Frontend Implementation (Next.js)

```typescript
// No actual code at planning stage, but interfaces defined
interface AuthState {
  user: User | null;
  session: Session | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}

interface AuthActions {
  signUp(email: string, password: string): Promise<AuthResponse>;
  signIn(email: string, password: string): Promise<AuthResponse>;
  signInWithGoogle(): Promise<AuthResponse>;
  signOut(): Promise<void>;
  resetPassword(email: string): Promise<void>;
}
```

Key components:
- Use Supabase Auth Client for all auth operations
- Create a custom `useAuth` hook to wrap Supabase functionality
- Store session in Supabase's secure storage
- Include JWT in all API requests automatically

### Backend Implementation (FastAPI)

The backend will use a **standardized JWT validation middleware** based on the implementation from `tech-stack-versions.md`:

```python
# Conceptual interface - not actual code
async def validate_token(credentials: HTTPAuthorizationCredentials) -> dict:
    """
    Validates the Supabase-issued JWT token and returns user context.
    
    Returns:
    {
        "user_id": str,  # Supabase user ID
        "role": str,     # User role (user, admin)
        "email": str,    # User email
        "token": str     # Original token
    }
    
    Raises:
    HTTPException(401) - If token is invalid or expired
    """
```

Key characteristics:
- Validates token signature using Supabase JWT secret
- Extracts comprehensive user context for authorization
- Uses Python-JOSE library for JWT operations
- Returns consistent user context object to all route handlers

## Edge Cases

### Admin Access Control

1. **Admin Role Assignment**:
   - Admin roles are assigned directly in Supabase user management
   - Role is included in the JWT payload
   - Backend middleware extracts role information for authorization checks

2. **Admin-only Routes**:
   ```python
   # Conceptual interface - not actual code
   async def require_admin(user_context: dict = Depends(validate_token)) -> dict:
       """
       Ensures the user has admin privileges.
       
       Raises:
       HTTPException(403) - If user is not an admin
       """
       if user_context.get("role") != "admin":
           raise HTTPException(status_code=403, detail="Admin access required")
       return user_context
   ```

### Token Refresh

1. **Refresh Flow**:
   - Supabase handles token refresh automatically via the client SDK
   - Frontend doesn't need custom refresh logic
   - Backend doesn't participate in the refresh process

2. **Handling Expired Tokens**:
   - JWT middleware returns 401 Unauthorized for expired tokens
   - Frontend catches 401 responses and triggers session refresh
   - If refresh fails, user is redirected to login

### Session Expiry

1. **Configuration**:
   - JWT expiry set to 24 hours (as specified in Project Specification)
   - Refresh tokens valid for 60 days

2. **Inactivity Timeout**:
   - Frontend monitors user activity
   - After 24 hours of inactivity, force session termination
   - Implement in a custom auth hook

## Interface Definitions

### Frontend-Backend Interface

API requests follow this structure:
```
Headers:
  Authorization: Bearer <jwt_token>
  Content-Type: application/json

Response Status Codes:
  200 - Success
  401 - Unauthorized (invalid/expired token)
  403 - Forbidden (insufficient permissions)
  429 - Too Many Requests (rate limiting)
```

### Backend-Supabase Interface

- Backend uses Supabase JWT secret to validate tokens locally
- No direct API calls to Supabase during validation
- Database queries utilize Supabase PostgreSQL with RLS policies

## Security Considerations

1. **Token Storage**:
   - JWTs stored securely by Supabase client (localStorage or cookies based on security settings)
   - Consider enabling httpOnly cookies for production

2. **HTTPS Enforcement**:
   - All API communication must use HTTPS
   - Set Secure and SameSite cookie attributes in production

3. **Rate Limiting**:
   - Implement rate limiting on auth endpoints to prevent brute force attacks
   - Consider IP-based and user-based rate limiting

4. **Token Validation Best Practices**:
   - Validate token signature
   - Check expiration time (exp claim)
   - Verify issuer (iss claim)
   - Validate audience (aud claim) if applicable

5. **JWT Secret Management**:
   - Store Supabase JWT secret as an environment variable
   - Rotate secrets periodically (coordinate with Supabase)
   - Use different secrets for development and production

6. **Audit Logging**:
   - Log authentication events for security monitoring
   - Include user ID, timestamp, IP address, and action
   - Do not log sensitive information like tokens

## Implementation Roadmap

1. **Phase 1: Basic Auth Setup**
   - Implement Supabase Auth integration in frontend
   - Create JWT validation middleware in backend
   - Test basic authentication flow

2. **Phase 2: Role-Based Access**
   - Implement admin role checks
   - Set up RLS policies in Supabase
   - Test permission enforcement

3. **Phase 3: Enhanced Security**
   - Add rate limiting
   - Implement proper error handling
   - Add audit logging
   - Security testing

## Appendix: Changes from Previous Documentation

This document supersedes:
1. `auth-flow.md` - Simplified approach with minimal middleware
2. Auth sections in `tech-stack-versions.md` - More detailed implementation

Key changes:
- Standardized on the more comprehensive user context extraction
- Clarified that JWT validation happens locally, not via API calls to Supabase
- Added edge case handling for admin access, token refresh, and session expiry
- Enhanced security considerations