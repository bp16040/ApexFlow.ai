# Architecture

ApexFlow AI uses a deliberately thin monorepo foundation:

- Next.js provides the browser interface.
- FastAPI exposes HTTP endpoints and shared runtime configuration.
- PostgreSQL is the persistent store, accessed through SQLAlchemy.
- Alembic manages schema revisions once domain models are introduced.

No business domain, authentication, or persistence models have been implemented in this foundation.
