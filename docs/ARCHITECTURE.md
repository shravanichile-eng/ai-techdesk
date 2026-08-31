# AITECHDESK Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Frontend (React + TypeScript)         │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Pages: Auth, Dashboard, Tickets, Chat, Admin   │   │
│  │  State: AuthContext, React Query                │   │
│  │  Styling: Tailwind CSS                          │   │
│  └──────────────────────────��───────────────────────┘   │
└──────────────────────────┬──────────────────────────────┘
                           │ HTTP/REST (Axios)
                           │
┌──────────────────────────▼──────────────────────────────┐
│              Backend (FastAPI + Python)                 │
│  ┌──────────────────────────────────────────────────┐   │
│  │  API Routers                                     │   │
│  │  - /api/auth        (JWT tokens)                 │   │
│  │  - /api/users       (User management)            │   │
│  │  - /api/tickets     (Ticket CRUD) [Phase 2]    │   │
│  │  - /api/ai/*        (AI operations) [Phase 3]  │   │
│  │  - /api/chat        (RAG chatbot) [Phase 4]    │   │
│  │  - /api/admin/*     (Admin operations)          │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Services Layer (Business Logic)                 │   │
│  │  - AuthService      (Authentication)            │   │
│  │  - UserService      (User management)           │   │
│  │  - TicketService    (Ticket operations)         │   │
│  │  - AIService        (AI/ML operations)          │   │
│  │  - RAGService       (Knowledge base)            │   │
│  │  - NotificationService (Notifications)          │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Core Utilities                                  │   │
│  │  - Security (JWT, password hashing)             │   │
│  │  - Config (environment variables)               │   │
│  │  - Logger (structured logging)                  │   │
│  └───────────────���──────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────┘
                           │ SQLAlchemy ORM
                           │
┌──────────────────────────▼──────────────────────────────┐
│              Database & Storage                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │  PostgreSQL 16                                   │   │
│  │  - users, roles, departments                     │   │
│  │  - tickets, categories, subcategories            │   │
│  │  - ticket_messages, ticket_status_history        │   │
│  │  - teams, team_members                           │   │
│  │  - ticket_ai_analyses, rag_queries               │   │
│  │  - notifications, audit_logs                     │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  pgvector Extension                              │   │
│  │  - document_chunks (vector embeddings)           │   │
│  │  - Vector similarity search for RAG              │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │ LangChain   │
                    │ Vector Ops  │
                    └──────┬──────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│              AI Provider Abstraction                    │
│  ┌──────────────────────────────────────────────────┐   │
│  │  AIProvider Interface                            │   │
│  │  ├─ OllamaProvider (default)                     │   │
│  │  ├─ OpenAIProvider (future)                      │   │
│  │  └─ AnthropicProvider (future)                   │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│              Ollama (Local LLM)                         │
│  - mistral (7B) - Primary LLM for classification       │
│  - nomic-embed-text - Embeddings for RAG               │
└──────────────────────────────────────────────────────────┘
```

## Data Flow Examples

### Authentication Flow
```
1. User enters credentials
2. Frontend POST /api/auth/login
3. AuthService.login() -> password verification
4. JWT token created (exp: 30 min)
5. Token stored in localStorage
6. Subsequent requests include Authorization header
7. Security.get_current_user() validates token
8. Request proceeds with user context
```

### Ticket Creation Flow (Phase 2+)
```
1. User submits ticket via form
2. Frontend POST /api/tickets
3. TicketService validates input
4. Ticket created in DRAFT status
5. AI analysis triggered [Phase 3]
6. Category, priority, team assigned by AI
7. Ticket status → CLASSIFIED
8. Assignment created
9. Admin notification sent
10. User receives confirmation
```

### AI Analysis Flow (Phase 3+)
```
User Input (Natural Language)
        ↓
Intent Classification (KNOWLEDGE_QUERY vs CREATE_TICKET)
        ↓
    IF KNOWLEDGE_QUERY:
        → RAG Query → DocumentChunk embeddings → LLM → Answer + Citations
    
    IF CREATE_TICKET:
        → Category Classification → Priority Prediction → Team Recommendation
        → Sentiment Analysis → Summary Generation
        → Confidence Scoring → User Confirmation
```

### RAG Retrieval Flow (Phase 4+)
```
User Question
    ↓
Generate Query Embedding
    ↓
PostgreSQL pgvector Similarity Search
    ↓
Retrieve Top-K Chunks (similarity > threshold)
    ↓
Construct Context Window
    ↓
LLM Generation with Context
    ↓
Format Response with Source Citations
    ↓
Return to User
```

## Database Schema Highlights

### Core Tables

**users**
- id (UUID, PK)
- email (unique, indexed)
- password_hash (bcrypt)
- role_id (FK → roles)
- department_id (FK → departments)
- status (ACTIVE, INACTIVE, LOCKED, SUSPENDED)
- last_login, login_attempts

**tickets**
- id (UUID, PK)
- ticket_number (TK-000001, unique)
- title, description
- creator_id (FK → users)
- category_id, subcategory_id
- status (DRAFT → SUBMITTED → ... → CLOSED)
- priority (CRITICAL, HIGH, MEDIUM, LOW)
- assigned_team_id, assigned_agent_id
- sla_policy_id, response_due_at, resolution_due_at
- ai_analyzed, ai_summary, ai_sentiment

**ticket_ai_analyses**
- ticket_id (FK → tickets, unique)
- intent, category, priority, team (all with confidence scores)
- sentiment, keywords, extracted_entities
- suggested_resolution_summary, troubleshooting_steps

**knowledge_documents**
- id (UUID, PK)
- filename, file_type, content
- status (UPLOADED → PROCESSING → INDEXED → FAILED)
- total_chunks, chunk_size

**document_chunks**
- id (UUID, PK)
- document_id (FK → knowledge_documents)
- content (text)
- embedding (VECTOR(384)) - pgvector
- is_indexed, search_score

### Relationship Map

```
User (1) ──── (M) Role
User (1) ──── (M) Department  
User (1) ──── (M) Ticket (creator)
User (1) ──── (M) Ticket (assignee)
User (1) ──── (M) TeamMember
User (1) ──── (M) Notification
User (1) ──── (M) AuditLog

Ticket (1) ──── (1) TicketAIAnalysis
Ticket (1) ──── (M) TicketMessage
Ticket (1) ──── (M) TicketStatusHistory
Ticket (1) ──── (M) TicketAssignment
Ticket (1) ──── (1) TicketFeedback

Category (1) ──── (M) SubCategory
Category (1) ──── (M) Ticket

Team (1) ──── (M) TeamMember
Team (1) ──── (M) TeamCategory

KnowledgeDocument (1) ──── (M) DocumentChunk
```

## Security Model

### Authentication
- **Method**: JWT tokens (HS256)
- **Token TTL**: 30 minutes (configurable)
- **Refresh**: Token refresh endpoint (Phase 2)
- **Storage**: localStorage (frontend)

### Authorization
- **Model**: Role-Based Access Control (RBAC)
- **Roles**: ADMIN, MANAGER, AGENT, USER
- **Enforcement**: Route-level decorators with role checking
- **Escalation**: Admins can override AI decisions

### Password Security
- **Hashing**: Bcrypt with 12 rounds
- **Minimum Length**: 8 characters (configurable)
- **Validation**: Server-side, never stored plaintext
- **Lockout**: 5 failed attempts ��� 15 min lockout

### Data Protection
- **Database**: All sensitive data encrypted at rest (configurable)
- **Transit**: HTTPS in production
- **SQL Injection**: Protected by SQLAlchemy ORM
- **CORS**: Configurable allowed origins
- **Secrets**: Environment variables only, never in code

## Scalability Considerations

### Current Design (Phase 1)
- Stateless API (scales horizontally)
- Database connection pooling
- JWT validation without database hits
- Indexed queries on high-traffic columns

### Future Additions
- Redis caching layer (Phase 5+)
- Celery workers for async tasks (Phase 6+)
- Message queue for notifications (Phase 5+)
- Database read replicas
- CDN for static frontend assets

## Deployment Targets

### Development
- Local Docker Compose (all-in-one)
- Individual service startup scripts

### Production (Planned)
- Kubernetes with separate pods
- Managed PostgreSQL (AWS RDS, Azure DB)
- Managed Redis (ElastiCache, Azure Cache)
- Container registry (Docker Hub, ECR, ACR)
- CI/CD Pipeline (GitHub Actions, GitLab CI)

## Technology Isolation

### Frontend
- Pure React, no server dependencies
- API-first communication
- Can be deployed to any static host
- Swappable HTTP client (currently Axios)

### Backend
- Vendor-independent AI provider interface
- Pluggable database (SQLAlchemy supports multiple DBs)
- Container-ready
- Can run on any Python 3.11+ environment

### AI
- Default: Ollama (free, local)
- Future: Easy swap to OpenAI, Anthropic, etc.
- Configuration-driven model selection
- No AI vendor lock-in

---

**Last Updated**: August 31, 2026  
**Architecture Version**: 1.0  
**Status**: Foundation Complete, Ready for Phase 2
