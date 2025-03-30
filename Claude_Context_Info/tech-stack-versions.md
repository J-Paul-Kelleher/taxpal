# TaxPal Tech Stack Version Requirements

## Frontend Technologies

### Core Framework
| Technology | Version | Purpose | Notes |
|------------|---------|---------|-------|
| Next.js | 15.2.3+ | React framework | Using App Router for improved routing and server components |
| React | 19.0.0+ | UI library | Using React hooks and functional components |
| TypeScript | 5.8.2+ | Type safety | Strict mode enabled for better code quality |
| Node.js | 22.14.0+ (LTS) | JavaScript runtime | Required for Next.js development environment |

### UI & Styling
| Technology | Version | Purpose | Notes |
|------------|---------|---------|-------|
| Chakra UI | 3.14.2+ | Component library | Alternative to Tailwind for faster MVP delivery |
| Framer Motion | 12.6.2+ | Animation library | For smooth UI transitions |

### State Management & Data Fetching
| Technology | Version | Purpose | Notes |
|------------|---------|---------|-------|
| React Query | 5.69.0+ | Data fetching & caching | For API data management |
| Zustand | 5.0.3+ | State management | Lightweight state management for global state |

### Authentication
| Technology | Version | Purpose | Notes |
|------------|---------|---------|-------|
| Supabase Auth Client | 2.69.1+ | Authentication | Client-side auth integration |

### Form Handling
| Technology | Version | Purpose | Notes |
|------------|---------|---------|-------|
| React Hook Form | 7.54.2+ | Form state management | For complex forms |
| Zod | 3.24.2+ | Schema validation | For form validation |

### Testing
| Technology | Version | Purpose | Notes |
|------------|---------|---------|-------|
| Jest | 29.7.0+ | Unit testing | For component and utility tests |
| React Testing Library | 14.0.0+ | Component testing | For component tests |
| Playwright | 1.38.1+ | End-to-end testing | For browser testing |
| MSW | 2.0.0+ | API mocking | For mocking backend in tests |

## Backend Technologies

### Core Framework
| Technology | Version | Purpose | Notes |
|------------|---------|---------|-------|
| Python | 3.11+ | Programming language | For backend services |
| FastAPI | 0.103.1+ | API framework | For building the REST API |
| Pydantic | 2.4.2+ | Data validation | For request/response models |
| Uvicorn | 0.23.2+ | ASGI server | For running FastAPI application |
| Gunicorn | 21.2.0+ | WSGI HTTP server | For production deployment |

### Database & ORM
| Technology | Version | Purpose | Notes |
|------------|---------|---------|-------|
| PostgreSQL | 15.0+ | Relational database | Via Supabase |
| SQLAlchemy | 2.0.21+ | ORM | For database interactions |
| Alembic | 1.12.0+ | Database migrations | For schema versioning |
| asyncpg | 0.28.0+ | PostgreSQL driver | For async database operations |

### Authentication & Security
| Technology | Version | Purpose | Notes |
|------------|---------|---------|-------|
| Supabase Auth Client | 2.38.4+ | Authentication | Client-side auth integration - handles user login/signup and issues JWTs |
| Python-JOSE | 3.3.0+ | JWT handling | For validating Supabase-issued JWTs in backend middleware |

**Note:** For the complete authentication implementation details, please refer to the "TaxPal Authentication - Unified Implementation Guide" document, which serves as the single source of truth for authentication implementation.



### RAG Components
| Technology | Version | Purpose | Notes |
|------------|---------|---------|-------|
| LangChain | 0.3.21+ | RAG framework | For building the RAG pipeline |
| Pinecone SDK | 6.0.2+ | Vector database client | For vector search |
| Google Generative AI | 0.3.1+ | Gemini API | For embeddings and completion |
| sentence-transformers | 2.2.2+ | Embedding models | Fallback for local embeddings |
| tiktoken | 0.5.1+ | Token counting | For token usage tracking |
| NLTK | 3.8.1+ | NLP toolkit | For text processing |
| spaCy | 3.7.0+ | NLP pipeline | For advanced text processing |

### Subscription Management
| Technology | Version | Purpose | Notes |
|------------|---------|---------|-------|
| Stripe SDK | 7.3.0+ | Payment processing | For subscription management |
| stripe-webhook-handler | 0.5.0+ | Webhook handling | For processing Stripe events |

### Testing
| Technology | Version | Purpose | Notes |
|------------|---------|---------|-------|
| pytest | 7.4.2+ | Testing framework | For unit and integration tests |
| pytest-asyncio | 0.21.1+ | Async test support | For testing async code |
| coverage | 7.3.2+ | Code coverage | For test coverage reporting |
| requests | 2.31.0+ | HTTP client | For API testing |
| Faker | 19.6.2+ | Test data generation | For generating test data |

## Infrastructure & DevOps

### Hosting & Deployment
| Technology | Version | Purpose | Notes |
|------------|---------|---------|-------|
| Vercel | N/A | Frontend hosting | For Next.js deployment |
| Fly.io | N/A | Backend hosting | For FastAPI deployment |
| Docker | 24.0.6+ | Containerization | For backend services |
| Docker Compose | 2.21.0+ | Local development | For local environment setup |

### CI/CD
| Technology | Version | Purpose | Notes |
|------------|---------|---------|-------|
| GitHub Actions | N/A | CI/CD pipeline | For automated testing and deployment |
| act | 0.2.45+ | Local Actions testing | For testing GitHub Actions locally |

### Monitoring & Logging
| Technology | Version | Purpose | Notes |
|------------|---------|---------|-------|
| Sentry | N/A | Error tracking | For error monitoring |
| Datadog | N/A | Application monitoring | For performance monitoring |
| Loguru | 0.7.2+ | Logging | Enhanced logging for Python |

### Development Tools
| Technology | Version | Purpose | Notes |
|------------|---------|---------|-------|
| ESLint | 8.51.0+ | JavaScript linting | For code quality |
| Prettier | 3.0.3+ | Code formatting | For consistent code style |
| Husky | 8.0.3+ | Git hooks | For pre-commit checks |
| lint-staged | 14.0.1+ | Staged file linting | For efficient linting |
| Black | 23.9.1+ | Python formatting | For consistent Python code style |
| isort | 5.12.0+ | Python import sorting | For organizing imports |
| Flake8 | 6.1.0+ | Python linting | For code quality |
| mypy | 1.5.1+ | Python type checking | For type safety |
| pre-commit | 3.4.0+ | Git hooks framework | For automated checks |

## Third-Party Services

### Data Storage
| Service | Version/Plan | Purpose | Notes |
|---------|--------------|---------|-------|
| Supabase | Pro plan | Auth, Database | For user data and chat history |
| Pinecone | Starter plan | Vector database | For embeddings storage |

### AI/ML Services
| Service | Version/Plan | Purpose | Notes |
|---------|--------------|---------|-------|
| Google AI (Gemini) | Flash 2.0 | LLM | For chat completions |
| Google AI Embeddings | gemini-embedding-exp-03-07 | Embeddings | For vector embeddings |

### Payment Processing
| Service | Version/Plan | Purpose | Notes |
|---------|--------------|---------|-------|
| Stripe | Standard plan | Payments | For subscription management |

### Monitoring & Analytics
| Service | Version/Plan | Purpose | Notes |
|---------|--------------|---------|-------|
| Sentry | Team plan | Error tracking | For error monitoring |
| Datadog | Pro plan | Monitoring | For performance monitoring |
| PostHog | Starter plan | Product analytics | For user behavior analysis |

## Environment Requirements

### Development Environment
| Requirement | Specification | Notes |
|-------------|---------------|-------|
| Node.js | 18.17.0+ | For frontend development |
| Python | 3.11+ | For backend development |
| Docker | 24.0.6+ | For local services |
| Git | 2.40.0+ | For version control |
| VS Code (recommended) | Latest | With recommended extensions |
| PostgreSQL | 15.0+ | Local development database |

### Production Environment
| Requirement | Specification | Notes |
|-------------|---------------|-------|
| Vercel | Enterprise plan | Frontend hosting |
| Fly.io | Production plan | Backend hosting |
| EU Region | Required | For GDPR compliance |
| TLS/SSL | Required | For secure connections |
| CDN | Required | For static assets |

## Compatibility Requirements

### Browser Support
| Browser | Minimum Version | Notes |
|---------|-----------------|-------|
| Chrome | 100+ | Primary support |
| Firefox | 100+ | Full support |
| Safari | 15+ | Full support |
| Edge | 100+ | Full support |
| iOS Safari | 15+ | Mobile support |
| Chrome for Android | 100+ | Mobile support |

### Device Support
| Device | Specifications | Notes |
|--------|---------------|-------|
| Desktop | 1024px+ width | Full feature set |
| Tablet | 768px+ width | Full feature set |
| Mobile | 320px+ width | Optimized interface |

## Dependency Management

### Frontend
| Tool | Version | Purpose | Notes |
|------|---------|---------|-------|
| npm | 9.0.0+ | Package management | Primary package manager |
| yarn | 1.22.19+ | Package management | Alternative package manager |
| pnpm | 8.7.4+ | Package management | Alternative package manager |

### Backend
| Tool | Version | Purpose | Notes |
|------|---------|---------|-------|
| pip | 23.2.1+ | Package management | For Python dependencies |
| Poetry | 1.6.1+ | Dependency management | Alternative to pip |
| virtualenv | 20.24.5+ | Environment management | For Python environments |

## Version Control Requirements

| Requirement | Specification | Notes |
|-------------|---------------|-------|
| Git | 2.40.0+ | Version control system |
| Branch Strategy | GitHub Flow | Feature branches, PRs to main |
| Commit Style | Conventional Commits | For automated changelog |
| Code Review | Required | For all PRs |
| PR Template | Required | For consistent PRs |

## Documentation Requirements

| Documentation | Tool/Format | Notes |
|---------------|-------------|-------|
| API Documentation | OpenAPI/Swagger | Auto-generated from FastAPI |
| Code Documentation | JSDoc/docstrings | For code-level documentation |
| User Documentation | Markdown/NextJS | For user guides |
| Architecture Documentation | Markdown/Diagrams | For system architecture |
