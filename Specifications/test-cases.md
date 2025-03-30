# TaxPal Test Cases

## RAG Implementation Tests

### Query Accuracy Tests

| ID | Test Case | Expected Outcome | Actual Outcome | Pass/Fail |
|----|-----------|-----------------|----------------|-----------|
| RA-001 | Basic income tax rate query: "What are the current income tax rates in Ireland?" | Response should accurately list tax rates with proper citation | | |
| RA-002 | VAT-related query: "What are the VAT rates for restaurant services?" | Response should provide current VAT rates for restaurant services with citation | | |
| RA-003 | Specific tax code query: "Explain Section 195 of the TCA 1997" | Response should provide a clear explanation of Section 195 (artists exemption) with citation | | |
| RA-004 | Complex tax scenario: "What tax implications arise from selling a property in Ireland that was inherited?" | Response should address CGT, inheritance tax considerations with proper citations | | |
| RA-005 | Temporal question: "What were the income tax rates in 2020?" | Response should provide 2020 rates if in corpus, or indicate temporal limitation | | |

### Retrieval Tests

| ID | Test Case | Expected Outcome | Actual Outcome | Pass/Fail |
|----|-----------|-----------------|----------------|-----------|
| RT-001 | Query with keywords not directly matched in corpus | Should use semantic search to find relevant information | | |
| RT-002 | Query requiring information from multiple documents | Should retrieve and synthesize information from multiple sources | | |
| RT-003 | Query with potential for confusion between similar topics | Should disambiguate and provide the most relevant information | | |
| RT-004 | Query with very specific technical term | Should identify and retrieve documents with the technical term | | |
| RT-005 | Query with typos in tax terminology | Should handle typos and still retrieve relevant information | | |

### Citation Tests

| ID | Test Case | Expected Outcome | Actual Outcome | Pass/Fail |
|----|-----------|-----------------|----------------|-----------|
| CT-001 | Any tax information query | Response should include proper citation in format: [Act Name] [Year], Section [Number] | | |
| CT-002 | Query with multiple relevant sections | Response should include all relevant citations | | |
| CT-003 | Query with information from guidance documents | Response should cite Tax and Duty Manual with part number | | |
| CT-004 | Query where information comes from multiple sources | Response should clearly indicate which information comes from which source | | |
| CT-005 | Query where no specific citation exists | Response should indicate information is general and not cite a specific section | | |

### Disclaimer & Reliability Tests

| ID | Test Case | Expected Outcome | Actual Outcome | Pass/Fail |
|----|-----------|-----------------|----------------|-----------|
| DR-001 | Any tax query | Response should include disclaimer about not being formal legal advice | | |
| DR-002 | Query with potentially outdated information | Response should indicate potential for updates since information was last indexed | | |
| DR-003 | Query outside the scope of Irish tax law | Response should clearly state limitations of knowledge domain | | |
| DR-004 | Ambiguous query with multiple interpretations | Response should ask for clarification rather than assume | | |
| DR-005 | Query requesting specific tax advice | Response should provide general information and recommend consulting a tax professional | | |

## User Authentication & Authorization Tests

### Registration & Login

| ID | Test Case | Expected Outcome | Actual Outcome | Pass/Fail |
|----|-----------|-----------------|----------------|-----------|
| UA-001 | New user registration with valid email/password | User account created successfully, confirmation message displayed | | |
| UA-002 | Registration with already existing email | Error message indicating email already in use | | |
| UA-003 | Registration with invalid email format | Validation error for email format | | |
| UA-004 | Registration with password less than 8 characters | Validation error for password length | | |
| UA-005 | Login with valid credentials | Successful login, redirect to chat interface | | |
| UA-006 | Login with invalid password | Error message for invalid credentials, no login | | |
| UA-007 | Login with non-existent email | Error message for invalid credentials, no login | | |
| UA-008 | Login with Google OAuth | Successful login via Google, account created if first time | | |
| UA-009 | Password reset request for valid email | Password reset email sent | | |
| UA-010 | Password reset request for non-existent email | Generic confirmation message (for security) but no email sent | | |

### Access Control

| ID | Test Case | Expected Outcome | Actual Outcome | Pass/Fail |
|----|-----------|-----------------|----------------|-----------|
| AC-001 | Accessing chat feature without login | Redirect to login page | | |
| AC-002 | Accessing admin dashboard as regular user | Access denied error | | |
| AC-003 | Accessing admin dashboard as admin user | Successful access to admin dashboard | | |
| AC-004 | JWT token tampering | Authentication rejected, user logged out | | |
| AC-005 | Using expired JWT token | Authentication rejected, user prompted to login again | | |

## Subscription & Billing Tests

### Plan Management

| ID | Test Case | Expected Outcome | Actual Outcome | Pass/Fail |
|----|-----------|-----------------|----------------|-----------|
| SB-001 | View available subscription plans | Display plans with features and pricing | | |
| SB-002 | Select plan and proceed to checkout | Redirect to Stripe checkout with correct plan details | | |
| SB-003 | Complete subscription payment | Account upgraded to paid tier, updated in database | | |
| SB-004 | Cancel subscription | Subscription marked for cancellation at end of current period | | |
| SB-005 | Subscription webhook - payment succeeded | User subscription status updated to active | | |
| SB-006 | Subscription webhook - payment failed | User notified of payment failure | | |

### Usage Limits

| ID | Test Case | Expected Outcome | Actual Outcome | Pass/Fail |
|----|-----------|-----------------|----------------|-----------|
| UL-001 | Free tier user under usage limit | Query processed normally | | |
| UL-002 | Free tier user reaches usage limit | Query blocked, upgrade modal displayed | | |
| UL-003 | Paid tier user under usage limit | Query processed normally | | |
| UL-004 | Paid tier user reaches usage limit | Query blocked, usage limit notification | | |
| UL-005 | Usage reset at scheduled interval | Usage counter reset to zero for billing period | | |

## Chat Interface Tests

### Chat Functionality

| ID | Test Case | Expected Outcome | Actual Outcome | Pass/Fail |
|----|-----------|-----------------|----------------|-----------|
| CI-001 | Submit basic query | Response displayed with appropriate formatting | | |
| CI-002 | Submit empty query | Validation error, no query sent | | |
| CI-003 | Submit very long query | Query truncated or warning displayed | | |
| CI-004 | Follow-up question | Context maintained from previous question | | |
| CI-005 | Response with citations | Citations displayed and clickable | | |
| CI-006 | Rate limiting test (>60 queries/minute) | Rate limit error displayed | | |

### User Experience

| ID | Test Case | Expected Outcome | Actual Outcome | Pass/Fail |
|----|-----------|-----------------|----------------|-----------|
| UX-001 | First-time user experience | Welcome message and sample queries displayed | | |
| UX-002 | Mobile responsiveness | UI adapts correctly to mobile viewport | | |
| UX-003 | Chat history persistence | Previous chats accessible in history sidebar | | |
| UX-004 | Loading state | Loading indicator shown while processing query | | |
| UX-005 | Error handling - backend error | User-friendly error message displayed | | |
| UX-006 | Feedback submission | Feedback recorded in database | | |

## Admin Interface Tests

### User Management

| ID | Test Case | Expected Outcome | Actual Outcome | Pass/Fail |
|----|-----------|-----------------|----------------|-----------|
| AM-001 | View list of users | Users displayed with key information | | |
| AM-002 | Search for specific user | User found and displayed | | |
| AM-003 | View user details | Complete user profile and subscription details displayed | | |
| AM-004 | Change user status (ban/suspend) | User status updated in database | | |

### Document Management

| ID | Test Case | Expected Outcome | Actual Outcome | Pass/Fail |
|----|-----------|-----------------|----------------|-----------|
| DM-001 | Upload new document | Document processed and added to database | | |
| DM-002 | Update existing document | Document updated, embeddings regenerated | | |
| DM-003 | Change document status | Document status updated | | |
| DM-004 | View document list | All documents displayed with status | | |
| DM-005 | Document version tracking | Previous versions accessible | | |

### Feedback Review

| ID | Test Case | Expected Outcome | Actual Outcome | Pass/Fail |
|----|-----------|-----------------|----------------|-----------|
| FR-001 | View feedback list | All feedback displayed with filters | | |
| FR-002 | Filter feedback by type | Only selected feedback type displayed | | |
| FR-003 | View detailed feedback | Complete feedback with context displayed | | |
| FR-004 | Mark feedback as reviewed | Feedback status updated | | |

## Performance & Security Tests

### Performance

| ID | Test Case | Expected Outcome | Actual Outcome | Pass/Fail |
|----|-----------|-----------------|----------------|-----------|
| PT-001 | Response time under normal load | Response time < 3 seconds | | |
| PT-002 | Response time with 50 concurrent users | Response time < 5 seconds | | |
| PT-003 | Load test with 100 concurrent users | System remains stable | | |
| PT-004 | Load test with 200 concurrent users | System scales appropriately | | |
| PT-005 | Database query performance | Key queries complete in < 100ms | | |

### Security

| ID | Test Case | Expected Outcome | Actual Outcome | Pass/Fail |
|----|-----------|-----------------|----------------|-----------|
| ST-001 | XSS attack attempt | Script content sanitized, attack prevented | | |
| ST-002 | SQL injection attempt | Parameterized queries prevent injection | | |
| ST-003 | CSRF attack | CSRF token validation prevents attack | | |
| ST-004 | Brute force login attempt | Rate limiting and account locking protect account | | |
| ST-005 | Prompt injection attempt | Input validation prevents system prompt modification | | |
| ST-006 | Authentication header manipulation | Request rejected | | |
| ST-007 | Access to sensitive files | Files not accessible | | |
| ST-008 | Data validation on all inputs | Invalid data rejected | | |

## Compliance Tests

### GDPR Compliance

| ID | Test Case | Expected Outcome | Actual Outcome | Pass/Fail |
|----|-----------|-----------------|----------------|-----------|
| GD-001 | Privacy policy accessibility | Privacy policy easily accessible in UI | | |
| GD-002 | User data export | User can export all their data | | |
| GD-003 | User account deletion | User data fully deleted from system | | |
| GD-004 | Chat history deletion | User can delete chat history | | |
| GD-005 | Cookie consent | Appropriate cookie consent mechanism in place | | |

### Disclaimer & Legal

| ID | Test Case | Expected Outcome | Actual Outcome | Pass/Fail |
|----|-----------|-----------------|----------------|-----------|
| DL-001 | Disclaimer visibility | Disclaimer visible on every page | | |
| DL-002 | Terms of service acceptance | User must accept terms to register | | |
| DL-003 | Response disclaimer | Every chatbot response includes disclaimer | | |
