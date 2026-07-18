# ApexFlow AI: Database Standards

This document defines required standards for future database implementation. It complements the master architecture and naming conventions and does not itself create schema changes.

## Audit and Common Metadata

Mutable tenant-owned business tables must include:

| Column | Standard |
| --- | --- |
| `id` | Native UUID primary key, non-null and immutable. |
| `organization_id` | Non-null tenant key unless the table is explicitly platform-global. |
| `created_at` | UTC timestamp with time zone, set once. |
| `created_by_user_id` | Actor identity where known; system actor is represented explicitly. |
| `updated_at` | UTC timestamp with time zone, updated on material mutation. |
| `updated_by_user_id` | Last mutating actor where known. |
| `deleted_at` | UTC soft-delete timestamp where the entity is soft-deletable. |
| `deleted_by_user_id` | Authorized deleting actor. |
| `delete_reason` | Required for policy-controlled deletion. |

Append-only event tables use `occurred_at`, `actor_user_id`, `event_type`, `correlation_id`, and an authority or source reference. They are not updated in place.

## Data Types and Validation

- Use `uuid` for entity identifiers, `timestamptz` for timestamps, `date` for calendar dates, and `numeric(p,s)` for marks, credits, money, and measured values that require exact precision.
- Store all timestamp instants in UTC. Convert only at presentation boundaries.
- Use `text` for unbounded content; use bounded `varchar` only when a validated business limit has meaning.
- Enforce value ranges and temporal consistency with check constraints, for example `ends_on > starts_on`.
- Normalize email for uniqueness and preserve the original display value only when needed for evidence.

## Primary Keys, Foreign Keys, and Integrity

- UUID `id` is the canonical primary key for every entity.
- Every foreign key must have an explicit delete behavior and corresponding index when queried or joined.
- Use `RESTRICT` for governed parents, `SET NULL` for optional historical associations, and `CASCADE` only for private dependents with no independent retention/audit value.
- Use unique constraints for business keys, scoped by `organization_id` where applicable.
- Enforce one primary reporting manager, primary position, or primary task owner with a partial unique constraint where supported.

## Indexing and Query Standards

- Index foreign keys, tenant keys, active lifecycle filters, and documented query paths.
- Prefer composite tenant-first indexes for tenant-isolated queries.
- Review indexes for selectivity, write cost, and query-plan evidence; remove redundant indexes.
- Use pagination based on deterministic indexed sort keys for large operational queues.
- Keep search/vector indexes derived and rebuildable; do not use them as the sole source of business truth.

## Soft Delete, Archival, and Retention

- Soft deletion is the default for business records whose history matters.
- Every repository/query must exclude `deleted_at IS NOT NULL` by default unless the caller has explicit restore/audit permission.
- Archival is a business lifecycle state and does not imply deletion.
- Physical deletion follows a documented retention policy, legal hold, and audit process.
- Attachments and communication content have classification-aware retention policies independent of task status.

## Multi-Tenancy and Security

- Tenant-owned records require `organization_id`; writes validate that every related entity belongs to the same organization.
- Tenant context is mandatory for application queries except controlled platform administration.
- Database-level row isolation may be introduced for defense in depth; it supplements, not replaces, application authorization.
- Secrets, tokens, raw refresh tokens, and sensitive connector credentials are never stored in plaintext. Store hashes or encrypted secret references as appropriate.
- Sensitive email, BCC, document, and AI content requires classification and permission-filtered retrieval.

## Lookup and Status Standards

- Use governed lookup tables for configurable or metadata-rich values.
- Lookup values use immutable codes, display names, sort order, active flag, and effective dates when required.
- Never delete a referenced lookup value; deactivate it.
- Status changes that affect business workflow are recorded in event history, not inferred only from `updated_at`.

## Change Management and Scalability

- Database changes are additive and backward compatible by default; destructive changes require a reviewed migration and data-retention plan.
- Every migration has rollback or forward-remediation guidance, validation steps, and a performance assessment.
- Use idempotency keys for connector ingestion and asynchronous writes.
- Use outbox/event publication for reliable cross-domain integration when asynchronous processing is introduced.
- Partition high-volume append-only tables by time and tenant only when measured volume justifies it.
- Backups, restore testing, retention, monitoring, and access reviews are operational requirements, not optional features.
