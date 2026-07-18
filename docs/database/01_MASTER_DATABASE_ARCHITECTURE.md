# ApexFlow AI: Master Database Architecture

This document defines the conceptual master database architecture for ApexFlow AI. It is a documentation-only target design; it does not add models, tables, migrations, APIs, or application code.

## 1. Database Philosophy

The database is a durable system of record for institutional structure, academic delivery, people, permissions, work, workflows, and AI evidence. Its design prioritizes:

- clear ownership of data by domain;
- referential integrity and auditable history;
- context-aware authorization boundaries;
- stable identifiers for integration and AI provenance;
- normalized transactional records with purpose-built read models where needed; and
- incremental, backward-compatible evolution.

Operational facts are stored once. Derived summaries, AI predictions, and search indexes must reference the source facts and must not silently replace them.

## 2. Domain-Driven Database Design

Each bounded domain owns its tables, lifecycle rules, validation, and write operations. Cross-domain relationships use stable identifiers and explicit foreign keys where the relationship is transactional; asynchronous projections, search indexes, and analytical models use source identifiers and versioning.

| Domain | Owns |
| --- | --- |
| Identity and Access | users, sessions, roles, permissions, role assignments, authentication evidence. |
| Organization | organizations, departments, programs, positions, reporting relationships, coordinator assignments. |
| Academic | academic years/periods, batches, sections, subjects, faculty assignments, outcomes, assessments. |
| Work Management | work requests, AI extraction results, tasks, participants, comments, dependencies, attachments, activity events. |
| Workflow | definitions, versions, instances, states, transitions, approvals, timers, delegations, notifications. |
| Communication and AI | source records, connector sync state, email/thread metadata, calendar/Drive references, AI outputs, knowledge-graph relationships. |
| Shared Reference | controlled lookups, classifications, lifecycle states, templates, and metadata policies. |

## 3. Domain Boundaries

- A domain can read another domain's published identifiers and approved read projections, but it must not update another domain's tables directly.
- Shared concepts such as `user_id`, `organization_id`, `department_id`, `program_id`, and `academic_session_id` are canonical references, not duplicated attributes.
- Work and workflow domains store the organizational scope needed for authorization at the time of action and retain historical evidence when source organization records change.
- Communication and AI domains retain source provenance and may create proposed work, but permissions, workflow decisions, and final authority remain owned by their respective domains.
- Lookup/reference data is centrally governed but consumed as read-only values by business domains.

## 4. Conceptual Data Layers

| Layer | Purpose |
| --- | --- |
| Transactional core | Normalized source-of-truth tables for current and historical business facts. |
| Reference data | Small controlled-value tables or enums with lifecycle and governance. |
| Audit and event history | Append-only events for material state, authority, and data changes. |
| Integration staging | Idempotent connector receipts, external identifiers, sync cursors, and error records. |
| Read and search projections | Denormalized, rebuildable views for dashboards, inboxes, search, and AI retrieval. |
| Analytics | Aggregated, privacy-governed reporting and workload data, separated from transactional writes. |

## 5. Audit Fields Standard

Every mutable business table includes the standard audit fields described in [05_DATABASE_STANDARDS.md](05_DATABASE_STANDARDS.md): `created_at`, `created_by_user_id`, `updated_at`, `updated_by_user_id`, and soft-delete fields when the table is eligible. Material decisions additionally store authority basis, source reference, and version or correlation identifiers.

## 6. Primary and Foreign Key Strategy

All core entities use UUID primary keys. UUIDs support secure external references, distributed creation, connector idempotency, and data movement across environments. Integer sequences may be used only as internal performance aids or human-facing sequence numbers; they are never the sole integration identity.

Foreign keys use `<referenced_entity>_id`, point to the canonical table, and are indexed when used in joins or filters. Mandatory ownership relationships are `NOT NULL`; optional relationships use `SET NULL` only when the historic record remains meaningful without the parent. Cascading deletes are limited to private dependent rows that have no independent audit, retention, or legal value.

## 7. Indexing Strategy

- Index primary keys, foreign keys used in joins, unique business keys, and high-selectivity filtering fields.
- Add composite indexes in the same order as common query predicates, for example `(organization_id, status, due_at)` for scoped task queues.
- Index active-record queries using partial indexes where the database supports them, for example rows with `deleted_at IS NULL`.
- Use full-text/search indexes only on approved, classified content and keep them rebuildable from source data.
- Measure query plans and write rates before adding indexes; every index has a write and storage cost.

## 8. Soft Delete Policy

Business records that require history use soft delete (`deleted_at`, `deleted_by_user_id`, `delete_reason`) rather than physical deletion. Normal queries exclude deleted rows. Restoration is authorized, audited, and valid only when referential integrity can be preserved.

Physical deletion is reserved for expired sessions, transient sync staging, derived projections, and data removed under an approved retention or legal policy. Audit events and retained source evidence are not silently removed by a soft-delete action.

## 9. Multi-Tenancy Considerations

The current foundation has organizations; the target design treats `organization_id` as the tenancy and top-level authorization boundary. Every tenant-owned business table includes a non-null `organization_id`, even when it can be inferred through a parent, to support scoped authorization, partitioning, and safety checks.

Tenant isolation is enforced by application policy, database constraints, and—where adopted—row-level security. Cross-tenant relationships are prohibited except for explicitly governed platform-administration or integration records. Unique keys are tenant-scoped unless the value is globally unique by design, such as a canonical external identity provider subject.

## 10. UUID vs Integer Strategy

| Use UUID for | Use integer/sequence for |
| --- | --- |
| Primary entity identifiers, external references, foreign keys, integration idempotency, event identifiers, and multi-tenant data movement. | Display sequence numbers, local ordering, counters, reporting aggregates, and database-internal surrogate optimization where not exposed as identity. |

UUIDs must be generated by a trusted application or database mechanism and stored in the native UUID type when supported. Human-readable codes such as department codes, program codes, batch codes, and document numbers are separate alternate keys with explicit uniqueness rules.

## 11. Lookup Table Strategy

Use lookup tables when values are governed, displayable, configurable, localizable, effective-dated, or have metadata beyond a code. Use database enums only for small, stable technical states whose deployment coupling is acceptable. Free text is not used for controlled categories such as task type, coordinator type, academic status, workflow state, or classification.

Lookup rows use stable UUIDs plus a unique code, display name, sort order, active status, and effective dates where needed. Deactivation preserves history; lookup values referenced by historical records are not physically deleted.

## 12. Common Metadata Fields

In addition to audit fields, applicable tables use:

- `organization_id` for tenant scope;
- `status` for lifecycle state;
- `effective_from` and `effective_to` for time-bound facts;
- `external_source` and `external_id` for connector identity;
- `source_version` and `source_captured_at` for synchronization;
- `classification_code` for sensitivity and handling;
- `correlation_id` for cross-domain operation tracing; and
- `metadata` only for bounded, validated extension data that does not replace relational columns.

## 13. ERD Overview

The master ERD groups the system into Organization, Academic, Identity/Authority, Work/Workflow, and Communication/AI domains. See [03_MASTER_ERD.md](03_MASTER_ERD.md) for the conceptual relationship overview and [02_DATABASE_DICTIONARY.md](02_DATABASE_DICTIONARY.md) for entity-level definitions.

## 14. Future Scalability

- Partition high-volume append-only tables such as activity events, connector receipts, notifications, and AI audit records by tenant and time.
- Separate read/search projections and analytical workloads from transactional writes.
- Use idempotency keys and outbox/event patterns for connector and cross-domain reliability.
- Introduce archival tiers for old source attachments and large communication bodies while preserving metadata and audit references.
- Add read replicas, tenant-aware sharding, and independently scalable search/vector services only after measured demand requires them.
