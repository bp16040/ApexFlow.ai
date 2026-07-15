# Authentication and organization foundation

## Authentication

All protected API routes use `Authorization: Bearer <access-token>`. Access tokens are short-lived JWTs. Refresh tokens are opaque random values stored only as SHA-256 hashes in the `sessions` table; every refresh rotates the token and revokes the previous session.

`POST /api/v1/auth/logout` revokes the submitted refresh-token session. Passwordless tokens are single-use, expiring, and stored only as hashes. A transactional-email adapter must deliver the token out of band; the API intentionally never returns it.

Google Workspace OAuth starts at `GET /api/v1/auth/google/login` and returns through the configured callback. Configure `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and an exact redirect URI. Set `ALLOWED_GOOGLE_WORKSPACE_DOMAINS` to a comma-separated allowlist in production.

## Authorization

Permissions are enforced server-side through route guards. The initial migration seeds the `platform_admin` role and these permissions:

- `users.read`
- `roles.read`, `roles.manage`, `roles.assign`
- `organization.read`, `organization.manage`

The first operational administrator must be promoted through a controlled deployment procedure (set `users.is_superuser` or assign `platform_admin`), then can assign roles through the API. User roles can be global or scoped to an organization.

## Organization and directory

The schema separates organization structure (departments, programs, academic sessions, designations, coordinators, and reporting lines) from people. A directory profile links a user to an organization and uses one of these supported directory types: `faculty`, `program_leader`, `office_assistant`, `lab_technician`, `cr`, `executive_director`, `associate_director`, `hod`, or `deputy_hod`.

Apply the schema with `cd backend; alembic upgrade head`.
