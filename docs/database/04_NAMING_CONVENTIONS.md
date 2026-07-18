# ApexFlow AI: Database Naming Conventions

These conventions apply to future physical database design. Existing foundation names are treated as compatibility constraints and should be aligned only through approved migrations.

## Table Names

- Use lower-case `snake_case` plural nouns: `workflow_instances`, `task_participants`, `academic_periods`.
- Use a domain prefix only when it prevents ambiguity: `email_messages`, `workflow_transitions`, `task_dependencies`.
- Use join-table names that describe the relationship: `role_permissions`, `user_roles`, `program_memberships`.
- Use `*_events` for append-only business timelines and `*_audits` or `audit_events` for audit records.
- Do not use abbreviations unless universally understood and documented; prefer `organization_id` over `org_id`.
- Do not embed database technology, environment, or version in table names.

## Column Names

- Use lower-case `snake_case` names.
- Primary key is always `id`.
- Foreign key is `<singular_referenced_table>_id`: `program_id`, `created_by_user_id`.
- Boolean columns use a readable predicate: `is_active`, `is_primary`, `has_attachments`.
- Timestamps use `_at`: `created_at`, `approved_at`, `expires_at`.
- Dates use `_on`: `starts_on`, `ends_on`.
- Durations include the unit: `grace_period_minutes`, `retention_days`.
- Counts use `_count`; sort values use `_sort_order`; versions use `_version` or `version_number`.
- Controlled codes use `_code`; display labels use `name` or `display_name`.
- Do not use reserved/ambiguous names such as `data`, `value`, `type`, or `status` without domain context when multiple values can coexist; prefer `source_type`, `workflow_status`, or `classification_code`.

## Constraints and Indexes

- Primary-key constraint: `pk_<table>`.
- Foreign-key constraint: `fk_<table>__<column>__<referenced_table>`.
- Unique constraint: `uq_<table>__<column1>__<column2>`.
- Check constraint: `ck_<table>__<rule>`.
- Index: `ix_<table>__<column1>__<column2>`.
- Partial/filtered index: `ix_<table>__active_<column>`.

Examples: `uq_programs__organization_id__code`, `fk_tasks__work_request_id__work_requests`, and `ix_tasks__organization_id__status__hard_deadline_at`.

## Identifiers and External References

- UUID keys use native UUID values, not text columns.
- Human-readable identifiers use `<domain>_code`, such as `department_code`, `batch_code`, or `subject_code` when not already represented by `code` in the entity itself.
- External connector identity uses `external_source`, `external_id`, and `source_version`; uniqueness is normally `(organization_id, external_source, external_id)`.
- Do not expose internal numeric sequence values as stable integration identifiers.

## Relationship and Lifecycle Names

- Use `parent_<entity>_id` for self-reference and `predecessor_`/`successor_` for directed relationships.
- Use `effective_from` and `effective_to` for time-bound responsibility or membership.
- Use `deleted_at`, never `is_deleted`, for soft deletion.
- Use `archived_at` only where archival is a distinct business lifecycle from deletion.
