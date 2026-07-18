# ApexFlow AI: Database Dictionary

This dictionary is a conceptual catalog for the target database architecture. Names are proposed table names, not implemented schema changes. All tenant-owned rows include `organization_id`, UUID primary keys, standard audit fields, and soft-delete metadata where applicable.

## Shared Standard Columns

| Column | Meaning |
| --- | --- |
| `id` | UUID primary key. |
| `organization_id` | Tenant/organization scope for tenant-owned records. |
| `created_at`, `created_by_user_id` | Creation audit. |
| `updated_at`, `updated_by_user_id` | Latest update audit. |
| `deleted_at`, `deleted_by_user_id`, `delete_reason` | Soft-delete audit when permitted. |
| `status` | Lifecycle status using a governed lookup or stable enum. |

## Identity and Access

| Table | Purpose | Principal columns |
| --- | --- | --- |
| `users` | One durable identity per person. | `email`, `full_name`, `employee_code`, `login_status`, `employment_status`, `availability_status` |
| `sessions` | Refresh-token/session lifecycle. | `user_id`, `refresh_token_hash`, `expires_at`, `revoked_at` |
| `roles` | Reusable permission bundles. | `key`, `name`, `is_system` |
| `permissions` | Canonical permission codes. | `code`, `name`, `description` |
| `role_permissions` | Role-to-permission membership. | `role_id`, `permission_id` |
| `user_roles` | Scoped role assignments. | `user_id`, `role_id`, `organization_id`, `effective_from`, `effective_to` |
| `authorization_delegations` | Time-bound delegated authority. | `delegator_user_id`, `delegate_user_id`, `scope_type`, `scope_id`, `actions`, `effective_from`, `effective_to` |

## Organization and Authority

| Table | Purpose | Principal columns |
| --- | --- | --- |
| `organizations` | Tenant/institute record. | `name`, `slug` |
| `departments` | Organizational department. | `parent_department_id`, `name`, `code` |
| `programs` | Academic program owned by a department. | `department_id`, `name`, `code` |
| `positions` | Position catalog and authority ceiling. | `code`, `name`, `authority_level` |
| `position_assignments` | Effective-dated user-to-position record. | `user_id`, `position_id`, `is_primary`, `effective_from`, `effective_to` |
| `program_memberships` | User participation in one or more programs. | `user_id`, `program_id`, `participation_type`, `effective_from`, `effective_to` |
| `coordinator_assignments` | Time-bound coordinator responsibility. | `user_id`, `coordinator_type_id`, `department_id`, `program_id`, `academic_period_id`, `effective_from`, `effective_to` |
| `reporting_relationships` | Primary, secondary, and escalation relationships. | `report_user_id`, `manager_user_id`, `relationship_type`, `effective_from`, `effective_to` |

## Academic

| Table | Purpose | Principal columns |
| --- | --- | --- |
| `academic_years` | Annual academic calendar. | `code`, `starts_on`, `ends_on`, `status` |
| `academic_periods` | Semester or future trimester. | `academic_year_id`, `period_type`, `sequence`, `starts_on`, `ends_on`, `status` |
| `batches` | Program intake cohort. | `program_id`, `code`, `intake_year`, `status` |
| `sections` | Teaching group in a batch. | `batch_id`, `code`, `capacity` |
| `subjects` | Program curriculum subject. | `program_id`, `academic_period_id`, `code`, `name`, `credits`, `theory_hours`, `lab_hours`, `tutorial_hours` |
| `faculty_assignments` | Teaching responsibility. | `user_id`, `program_id`, `batch_id`, `section_id`, `academic_period_id`, `subject_id`, `teaching_hours` |
| `course_outcomes` | Subject-level outcome. | `subject_id`, `code`, `statement`, `bloom_level` |
| `program_outcomes` | Program-level outcome. | `program_id`, `code`, `statement` |
| `program_specific_outcomes` | Program-specific outcome. | `program_id`, `code`, `statement` |
| `assessment_components` | Assessment setup for a subject offering. | `subject_id`, `batch_id`, `academic_period_id`, `assessment_type_id`, `maximum_marks`, `weight` |

## Work and Workflow

| Table | Purpose | Principal columns |
| --- | --- | --- |
| `work_requests` | Immutable intake record. | `source_type`, `external_source`, `external_id`, `original_assigning_authority_id`, `status`, `captured_at` |
| `ai_extractions` | AI proposal and evidence. | `work_request_id`, `model_version`, `confidence`, `intent`, `verification_required`, `verified_by_user_id` |
| `tasks` | Actionable work item. | `work_request_id`, `parent_task_id`, `task_type_id`, `priority_id`, `status`, `soft_deadline_at`, `hard_deadline_at`, `original_assigning_authority_id` |
| `task_participants` | Assignees, reviewers, approvers, watchers. | `task_id`, `user_id`, `participant_role`, `is_primary_owner` |
| `task_dependencies` | Predecessor/successor relationship. | `predecessor_task_id`, `successor_task_id`, `dependency_type`, `status` |
| `task_checklist_items` | Required/optional work checklist. | `task_id`, `sequence`, `text`, `is_required`, `completed_at` |
| `comments` | Discussion on work or workflow. | `task_id`, `author_user_id`, `body`, `visibility_code`, `parent_comment_id` |
| `workflow_definitions` | Configurable workflow template. | `code`, `name`, `resource_type`, `status` |
| `workflow_definition_versions` | Immutable versioned workflow configuration. | `workflow_definition_id`, `version_number`, `definition_json`, `published_at` |
| `workflow_instances` | Runtime workflow state. | `definition_version_id`, `resource_type`, `resource_id`, `current_state`, `started_at`, `completed_at` |
| `workflow_transitions` | Append-only transition evidence. | `workflow_instance_id`, `from_state`, `to_state`, `actor_user_id`, `authority_basis`, `occurred_at` |
| `approval_decisions` | Review/approval decision evidence. | `workflow_instance_id`, `stage_code`, `approver_user_id`, `decision`, `comment`, `decided_at` |
| `activity_events` | Append-only business timeline. | `entity_type`, `entity_id`, `event_type`, `actor_user_id`, `authority_basis`, `correlation_id`, `occurred_at` |

## Communication and AI

| Table | Purpose | Principal columns |
| --- | --- | --- |
| `communication_sources` | Normalized connector/manual source identity. | `source_type`, `external_source`, `external_id`, `source_version`, `owner_user_id`, `classification_code`, `captured_at` |
| `email_threads` | Email-thread metadata. | `communication_source_id`, `external_thread_id`, `subject`, `last_message_at` |
| `email_messages` | Individual email metadata and permitted body reference. | `email_thread_id`, `external_message_id`, `sender_address`, `sent_at`, `importance_code`, `category_code` |
| `calendar_events` | Calendar-event reference. | `communication_source_id`, `external_event_id`, `starts_at`, `ends_at`, `organizer_user_id` |
| `documents` | Drive/knowledge document metadata. | `communication_source_id`, `external_document_id`, `name`, `mime_type`, `classification_code`, `version` |
| `attachments` | Reusable source/task/document file artifact. | `storage_key`, `file_name`, `checksum`, `mime_type`, `classification_code`, `retention_status` |
| `connector_sync_runs` | Connector execution and cursor. | `connector_type`, `started_at`, `completed_at`, `status`, `cursor`, `error_summary` |
| `knowledge_entities` | Governed graph node. | `entity_type`, `source_entity_id`, `display_name`, `visibility_scope` |
| `knowledge_relationships` | Governed graph edge. | `from_entity_id`, `to_entity_id`, `relationship_type`, `source_type`, `confidence`, `effective_from`, `effective_to` |

## Reference and Governance

| Table | Purpose | Principal columns |
| --- | --- | --- |
| `lookup_sets` | Governed controlled-value collection. | `code`, `name`, `scope_type` |
| `lookup_values` | Controlled code/display value. | `lookup_set_id`, `code`, `name`, `sort_order`, `is_active`, `effective_from`, `effective_to` |
| `data_retention_policies` | Retention/deletion rules by classification and entity type. | `entity_type`, `classification_code`, `retention_days`, `disposition_action` |
| `audit_events` | Security and data-change audit. | `entity_type`, `entity_id`, `action`, `actor_user_id`, `before_data`, `after_data`, `occurred_at` |
