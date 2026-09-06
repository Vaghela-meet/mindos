# MindOS Architecture

MindOS is an adaptive personal productivity operating system built as a **modular monolith**. It manages attention and dynamic scheduling across personal workload and goals.

---

## Architectural Topology

```text
React UI (TypeScript + Vite + Tailwind CSS)
    │
    ▼ (HTTP / REST)
FastAPI Application (/api/v1)
    │
    ▼
Core Layer (Config, Database Engine, Security)
    │
    ▼
Application Services (Modular Monolith)
    ├── Task Service
    ├── Goal Service
    ├── Planning Service
    ├── Adaptation Service
    ├── Focus Service
    ├── AI Service (Provider-agnostic)
    └── Voice Service
    │
    ▼
PostgreSQL Database (SQLAlchemy 2.0 ORM + Alembic Migrations)
```

---

## Key Design Principles

1. **Modular Monolith**:
   - Business domains are organized into dedicated sub-packages within `backend/app/services/`.
   - Domains maintain loose coupling with well-defined service interfaces, enabling clean evolution without premature distributed-system overhead.

2. **API Versioning**:
   - All public endpoints are scoped under `/api/v1` via router grouping.
   - Root `/health` and `/api/v1/health` provide system readiness and component status.

3. **Database Layer (PostgreSQL Target)**:
   - Target database is PostgreSQL, accessed via SQLAlchemy 2.0 ORM.
   - Migrations are managed deterministically with Alembic.
   - The foundation engine uses connection pooling with health fallback; the service starts up cleanly even if the PostgreSQL instance is temporarily unreachable during early development.

4. **Frontend Architecture**:
   - Modern Single Page Application built with React, TypeScript, and Vite.
   - Tailwind CSS for styling with a modern design system.
   - Strict typing with Vite path aliases (`@/*` pointing to `src/*`).

5. **Testing Strategy**:
   - **Backend**: Pytest with FastAPI `TestClient` for unit and integration testing.
   - **Frontend**: Vitest and React Testing Library for fast component unit tests.
