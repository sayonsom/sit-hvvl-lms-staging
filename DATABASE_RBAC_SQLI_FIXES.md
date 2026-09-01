# HVVL LMS Database Security Fix List

Date: 2026-06-09

This checklist is based on the current schema in `backend-api/sql/CreateInitialTables.sql` and the VAPT findings around RBAC, IDOR, and SQL injection retesting.

Concrete starter migration: `backend-api/sql/2026-06-09-rbac-security-hardening.sql`.

Database changes alone will not fix authorization unless the backend also validates the user and passes a trusted identity/role/course context into every query. Treat the database work below as the data model and enforcement foundation for the API changes.

## 1. Normalize Identities

Current tables split users into `Students` and `Instructors`, with no shared account table or role mapping. Add a canonical account table tied to the identity provider subject.

Required tables:

- `users`: one row per authenticated human or service identity.
- `roles`: stable role definitions such as `student`, `teacher`, `admin`, `service`.
- `user_roles`: many-to-many role assignments.
- `identity_providers`: optional lookup for `brightspace_lti`, `entra_id`, and service accounts.

Required columns:

- `users.id uuid primary key`
- `users.email citext unique not null`
- `users.idp_subject text unique not null`
- `users.idp text not null`
- `users.is_active boolean not null default true`
- `users.created_at timestamptz not null default now()`
- `users.updated_at timestamptz not null default now()`

Map existing records:

- `Students.user_id -> users.id`
- `Instructors.user_id -> users.id`

Why:

- The backend currently trusts student IDs and staff state supplied from the browser.
- A canonical user table lets all object access be tied to a trusted authenticated identity.

## 2. Add Course-Scoped Staff Assignment

Current `Courses.instructor_id` supports one instructor, but RBAC needs explicit staff-to-course membership and role assignment.

Required table:

- `course_staff`

Required columns:

- `course_staff.course_id references Courses(course_id) on delete cascade`
- `course_staff.user_id references users(id) on delete cascade`
- `course_staff.role text not null check (role in ('teacher', 'ta', 'admin'))`
- `course_staff.created_at timestamptz not null default now()`
- Primary key on `(course_id, user_id, role)`

Why:

- Teachers must only access courses they teach unless they are admins.
- Course-wide result endpoints need this table for authorization filters.

## 3. Harden Enrollments

Current `Enrollments` does not prevent duplicate enrollment rows and does not enforce active enrollment windows.

Required changes:

- Add `not null` to `student_id`, `course_id`, and `enrollment_date`.
- Add unique constraint on `(student_id, course_id)`.
- Add `status text not null default 'active' check (status in ('active', 'inactive', 'withdrawn', 'completed'))`.
- Add indexes on `Enrollments(student_id)`, `Enrollments(course_id)`, and `(student_id, course_id)`.
- Add `on delete cascade` or controlled restrict behavior for student/course foreign keys.

Why:

- Student course visibility and module access must be enforceable by enrollment.
- Duplicate rows can create ambiguous access decisions.

## 4. Constrain Student Responses

Current `studentresponses` allows multiple responses for the same student/question and does not prove the question belongs to a course the student is enrolled in.

Required changes:

- Add unique constraint on `(student_id, question_id)`.
- Add `not null` to `student_id`, `question_id`, and `response`.
- Add `created_at`, `updated_at`, and `submitted_by_user_id`.
- Add indexes on `studentresponses(student_id)` and `studentresponses(question_id)`.
- Add an authorization-safe write path that checks enrollment before insert/update.

Recommended database function:

- `submit_student_response(p_actor_user_id uuid, p_question_id int, p_response text)`

The function should:

- Resolve `p_actor_user_id` to exactly one active student.
- Join `Questions -> Assignments -> Modules -> Courses -> Enrollments`.
- Confirm the student is actively enrolled in the course containing the question.
- Upsert only that student's own response.

Why:

- The current API accepts `student_id` from the request body, which enables IDOR-style tampering.

## 5. Add Result-Read Authorization Views

Do not let the API query raw result tables directly for user-facing endpoints.

Recommended views or security-definer functions:

- `student_visible_responses(actor_user_id uuid)`
- `teacher_visible_course_results(actor_user_id uuid, course_id int)`
- `admin_course_results(actor_user_id uuid, course_id int)`

Required checks:

- Student can only see their own responses.
- Teacher can only see results for assigned courses.
- Admin can see all course results.

Why:

- Authorization filters should be part of the data access query, not a frontend filter after broad data retrieval.

## 6. Add Row-Level Security Where Feasible

If the backend uses PostgreSQL, enable RLS on sensitive tables after introducing `users`, `course_staff`, and trusted DB session variables.

Candidate tables:

- `Students`
- `Instructors`
- `Courses`
- `Enrollments`
- `Modules`
- `Assignments`
- `Questions`
- `Options`
- `studentresponses`

Required backend contract:

- On every request transaction, set trusted session variables such as:
  - `app.user_id`
  - `app.roles`
  - `app.auth_method`

Example:

```sql
SELECT set_config('app.user_id', :trusted_user_id, true);
SELECT set_config('app.roles', :trusted_roles_csv, true);
```

Why:

- RLS provides defense in depth if an API route forgets an authorization filter.

## 7. Add Audit Logging

Required table:

- `audit_events`

Recommended columns:

- `event_id uuid primary key default gen_random_uuid()`
- `actor_user_id uuid`
- `actor_email citext`
- `actor_roles text[]`
- `action text not null`
- `entity_type text not null`
- `entity_id text`
- `course_id int`
- `student_id int`
- `request_id text`
- `source_ip inet`
- `user_agent text`
- `success boolean not null`
- `error_code text`
- `created_at timestamptz not null default now()`

Log at minimum:

- Student response submit/update.
- Course-wide results read.
- Student results read.
- Student/course enrollment changes.
- Content upload/download URL generation.
- Staff/admin login and denied access decisions.

Why:

- RBAC fixes need evidence. Audit trails are also useful for detecting attempted IDOR and SQLi probing.

## 8. Add Data Integrity Constraints

Recommended constraints:

- `Students.email citext unique not null`
- `Instructors.email citext unique not null`
- `Courses.instructor_id not null` until replaced by `course_staff`
- `Modules.course_id not null`
- `Assignments.module_id not null`
- `Questions.assignment_id not null`
- `Options.question_id not null`
- `Questions.question_type check (question_type in ('multiple_choice', 'long_text', 'short_text', 'numeric'))`
- `Courses.enrollment_status check (...)`
- Foreign keys should include explicit `on delete` behavior.

Why:

- Null or duplicate ownership records weaken RBAC decisions and make secure query filters unreliable.

## 9. Lock Down Database Roles

Use separate database roles instead of one all-powerful application user.

Recommended roles:

- `hvvl_app_runtime`: API runtime, least privilege.
- `hvvl_migration`: schema migration only.
- `hvvl_reporting_readonly`: read-only reporting.
- `hvvl_service_sync`: Brightspace/LTI sync operations only.

Required grants:

- Runtime role should not own tables.
- Runtime role should not have unrestricted `delete`, schema changes, or superuser privileges.
- Prefer execute grants on security-definer functions for sensitive writes/reads.

Why:

- If an API bug is exploited, least-privilege DB roles limit blast radius.

## 10. SQL Injection Hardening

The reviewed asyncpg CRUD paths mostly use bind parameters, which is good. Preserve this with database and CI controls.

Required changes:

- Keep parameterized queries only; no string interpolation for SQL with user-controlled values.
- Add a SQL review test that fails on `f"SELECT`, `f"INSERT`, `f"UPDATE`, `f"DELETE`, `.format(...)` SQL, and `%` SQL formatting.
- Use allowlisted sort/filter values for any future dynamic query builder.
- Store SQL functions for sensitive workflows and pass parameters, not interpolated SQL.

Why:

- SQLi was not confirmed from reviewed active CRUD paths, but dynamic testing could not complete while UAT was unavailable.

## 11. Content/File Access Data Model

Current file URL generation and file serving are not backed by a course/user authorization model.

Required table:

- `content_assets`

Recommended columns:

- `asset_id uuid primary key`
- `course_id int not null references Courses(course_id)`
- `module_id uuid references Modules(module_id)`
- `storage_key text not null unique`
- `original_filename text not null`
- `mime_type text not null`
- `uploaded_by_user_id uuid references users(id)`
- `visibility text not null check (visibility in ('course', 'staff_only', 'admin_only'))`
- `created_at timestamptz not null default now()`

Why:

- File URL generation should check enrollment or course staff assignment before returning a link.

## 12. Deployment Order

1. Create `users`, `roles`, `user_roles`, and `course_staff`.
2. Backfill users from existing `Students` and `Instructors`.
3. Add `Students.user_id` and `Instructors.user_id`, then enforce uniqueness/not-null after backfill.
4. Add enrollment and student response constraints.
5. Add authorization-safe result views/functions.
6. Update API code to use trusted `actor_user_id` and stop accepting `student_id` for self-service writes.
7. Add audit logging.
8. Enable RLS after the API is setting trusted DB session variables correctly.
9. Reduce runtime database grants.
10. Run the RBAC/IDOR/SQLi retest suite through Caido/Burp.

## 13. Acceptance Criteria

- Anonymous API calls cannot read `Students`, `studentresponses`, course results, or content assets.
- Student A cannot read or modify Student B records.
- A teacher cannot read results for an unassigned course.
- Course-wide results are only available to assigned teachers/admins.
- Student response writes derive student identity from the authenticated session, not from a request body `student_id`.
- Duplicate enrollments and duplicate student/question responses are impossible at the database level.
- Audit records exist for privileged reads and writes.
- SQLi regression tests pass and no user-controlled SQL string interpolation remains.
