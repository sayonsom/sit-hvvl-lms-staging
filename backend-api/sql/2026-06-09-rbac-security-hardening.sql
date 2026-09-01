-- HVVL LMS RBAC/IDOR/SQLi database hardening migration skeleton.
-- Date: 2026-06-09
--
-- This is intentionally additive and non-destructive. Run the preflight queries,
-- clean duplicate/null data, then enable the final UNIQUE/NOT NULL/RLS steps.
-- Existing table names in CreateInitialTables.sql are unquoted, so PostgreSQL
-- stores them as lowercase identifiers.

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS citext;

-- ---------------------------------------------------------------------------
-- 1. Canonical identities and roles
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS identity_providers (
    provider_key TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

INSERT INTO identity_providers (provider_key, display_name)
VALUES
    ('brightspace_lti', 'Brightspace LTI'),
    ('entra_id', 'Microsoft Entra ID'),
    ('service', 'Service Account')
ON CONFLICT (provider_key) DO NOTHING;

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email CITEXT UNIQUE NOT NULL,
    display_name TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS user_identities (
    provider_key TEXT NOT NULL REFERENCES identity_providers(provider_key),
    provider_subject TEXT NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (provider_key, provider_subject),
    UNIQUE (user_id, provider_key)
);

CREATE TABLE IF NOT EXISTS roles (
    role_key TEXT PRIMARY KEY,
    description TEXT NOT NULL
);

INSERT INTO roles (role_key, description)
VALUES
    ('student', 'Learner authenticated through Brightspace LTI'),
    ('teacher', 'Course staff authenticated through Entra ID'),
    ('admin', 'Privileged LMS administrator'),
    ('service', 'Backend service integration identity')
ON CONFLICT (role_key) DO UPDATE
SET description = EXCLUDED.description;

CREATE TABLE IF NOT EXISTS user_roles (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_key TEXT NOT NULL REFERENCES roles(role_key),
    granted_by_user_id UUID REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (user_id, role_key)
);

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS users_set_updated_at ON users;
CREATE TRIGGER users_set_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

-- Add links from legacy student/instructor records to canonical users.
ALTER TABLE students ADD COLUMN IF NOT EXISTS user_id UUID;
ALTER TABLE instructors ADD COLUMN IF NOT EXISTS user_id UUID;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'students'::regclass
          AND conname = 'students_user_id_fk'
    ) THEN
        ALTER TABLE students
        ADD CONSTRAINT students_user_id_fk
        FOREIGN KEY (user_id) REFERENCES users(id);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'instructors'::regclass
          AND conname = 'instructors_user_id_fk'
    ) THEN
        ALTER TABLE instructors
        ADD CONSTRAINT instructors_user_id_fk
        FOREIGN KEY (user_id) REFERENCES users(id);
    END IF;
END $$;

CREATE UNIQUE INDEX IF NOT EXISTS students_user_id_uidx
ON students(user_id)
WHERE user_id IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS instructors_user_id_uidx
ON instructors(user_id)
WHERE user_id IS NOT NULL;

-- Preflight: duplicate legacy emails need human cleanup. The provisional
-- backfill below maps only the first row per email and leaves duplicates unlinked.
SELECT lower(trim(email)) AS email, COUNT(*) AS duplicate_count
FROM students
WHERE email IS NOT NULL AND trim(email) <> ''
GROUP BY lower(trim(email))
HAVING COUNT(*) > 1;

SELECT lower(trim(email)) AS email, COUNT(*) AS duplicate_count
FROM instructors
WHERE email IS NOT NULL AND trim(email) <> ''
GROUP BY lower(trim(email))
HAVING COUNT(*) > 1;

-- Provisional backfill for staging data only. Replace provider_subject with the
-- actual Brightspace/Entra immutable subject during the production migration.
INSERT INTO users (email, display_name)
SELECT DISTINCT ON (lower(trim(email)))
       lower(trim(email))::CITEXT,
       NULLIF(trim(name), '')
FROM students
WHERE email IS NOT NULL AND trim(email) <> ''
ORDER BY lower(trim(email)), student_id
ON CONFLICT (email) DO UPDATE
SET display_name = COALESCE(users.display_name, EXCLUDED.display_name),
    updated_at = now();

INSERT INTO users (email, display_name)
SELECT DISTINCT ON (lower(trim(email)))
       lower(trim(email))::CITEXT,
       NULLIF(trim(name), '')
FROM instructors
WHERE email IS NOT NULL AND trim(email) <> ''
ORDER BY lower(trim(email)), instructor_id
ON CONFLICT (email) DO UPDATE
SET display_name = COALESCE(users.display_name, EXCLUDED.display_name),
    updated_at = now();

UPDATE students s
SET user_id = u.id
FROM users u,
     (
         SELECT student_id,
                lower(trim(email))::CITEXT AS normalized_email,
                ROW_NUMBER() OVER (
                    PARTITION BY lower(trim(email))
                    ORDER BY student_id
                ) AS email_rank
         FROM students
         WHERE email IS NOT NULL AND trim(email) <> ''
     ) ranked_students
WHERE s.user_id IS NULL
  AND s.student_id = ranked_students.student_id
  AND ranked_students.email_rank = 1
  AND ranked_students.normalized_email = u.email;

UPDATE instructors i
SET user_id = u.id
FROM users u,
     (
         SELECT instructor_id,
                lower(trim(email))::CITEXT AS normalized_email,
                ROW_NUMBER() OVER (
                    PARTITION BY lower(trim(email))
                    ORDER BY instructor_id
                ) AS email_rank
         FROM instructors
         WHERE email IS NOT NULL AND trim(email) <> ''
     ) ranked_instructors
WHERE i.user_id IS NULL
  AND i.instructor_id = ranked_instructors.instructor_id
  AND ranked_instructors.email_rank = 1
  AND ranked_instructors.normalized_email = u.email;

INSERT INTO user_identities (provider_key, provider_subject, user_id)
SELECT 'brightspace_lti', 'legacy-student:' || s.student_id::TEXT, s.user_id
FROM students s
WHERE s.user_id IS NOT NULL
ON CONFLICT (provider_key, provider_subject) DO NOTHING;

INSERT INTO user_identities (provider_key, provider_subject, user_id)
SELECT 'entra_id', 'legacy-instructor:' || i.instructor_id::TEXT, i.user_id
FROM instructors i
WHERE i.user_id IS NOT NULL
ON CONFLICT (provider_key, provider_subject) DO NOTHING;

INSERT INTO user_roles (user_id, role_key)
SELECT DISTINCT user_id, 'student'
FROM students
WHERE user_id IS NOT NULL
ON CONFLICT (user_id, role_key) DO NOTHING;

INSERT INTO user_roles (user_id, role_key)
SELECT DISTINCT user_id, 'teacher'
FROM instructors
WHERE user_id IS NOT NULL
ON CONFLICT (user_id, role_key) DO NOTHING;

-- ---------------------------------------------------------------------------
-- 2. Course-scoped staff assignment
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS course_staff (
    course_id INT NOT NULL REFERENCES courses(course_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('teacher', 'ta', 'admin')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (course_id, user_id, role)
);

CREATE INDEX IF NOT EXISTS course_staff_user_course_idx
ON course_staff(user_id, course_id);

INSERT INTO course_staff (course_id, user_id, role)
SELECT c.course_id, i.user_id, 'teacher'
FROM courses c
JOIN instructors i ON i.instructor_id = c.instructor_id
WHERE i.user_id IS NOT NULL
ON CONFLICT (course_id, user_id, role) DO NOTHING;

-- ---------------------------------------------------------------------------
-- 3. Enrollment hardening
-- ---------------------------------------------------------------------------

ALTER TABLE enrollments ADD COLUMN IF NOT EXISTS status TEXT NOT NULL DEFAULT 'active';

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'enrollments'::regclass
          AND conname = 'enrollments_status_check'
    ) THEN
        ALTER TABLE enrollments
        ADD CONSTRAINT enrollments_status_check
        CHECK (status IN ('active', 'inactive', 'withdrawn', 'completed')) NOT VALID;
    END IF;
END $$;

ALTER TABLE enrollments VALIDATE CONSTRAINT enrollments_status_check;

CREATE INDEX IF NOT EXISTS enrollments_student_id_idx ON enrollments(student_id);
CREATE INDEX IF NOT EXISTS enrollments_course_id_idx ON enrollments(course_id);
CREATE INDEX IF NOT EXISTS enrollments_student_course_idx ON enrollments(student_id, course_id);

-- Preflight: these queries must return zero rows before enforcing uniqueness
-- and NOT NULL constraints.
SELECT student_id, course_id, COUNT(*) AS duplicate_count
FROM enrollments
WHERE student_id IS NOT NULL AND course_id IS NOT NULL
GROUP BY student_id, course_id
HAVING COUNT(*) > 1;

SELECT COUNT(*) AS enrollments_with_null_required_fields
FROM enrollments
WHERE student_id IS NULL OR course_id IS NULL OR enrollment_date IS NULL;

-- Enable after duplicate/null cleanup:
-- CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS enrollments_student_course_uidx
-- ON enrollments(student_id, course_id);
-- ALTER TABLE enrollments ALTER COLUMN student_id SET NOT NULL;
-- ALTER TABLE enrollments ALTER COLUMN course_id SET NOT NULL;
-- ALTER TABLE enrollments ALTER COLUMN enrollment_date SET NOT NULL;

-- ---------------------------------------------------------------------------
-- 4. Student response hardening
-- ---------------------------------------------------------------------------

ALTER TABLE studentresponses ADD COLUMN IF NOT EXISTS submitted_by_user_id UUID;
ALTER TABLE studentresponses ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT now();
ALTER TABLE studentresponses ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT now();

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'studentresponses'::regclass
          AND conname = 'studentresponses_submitted_by_user_fk'
    ) THEN
        ALTER TABLE studentresponses
        ADD CONSTRAINT studentresponses_submitted_by_user_fk
        FOREIGN KEY (submitted_by_user_id) REFERENCES users(id);
    END IF;
END $$;

DROP TRIGGER IF EXISTS studentresponses_set_updated_at ON studentresponses;
CREATE TRIGGER studentresponses_set_updated_at
BEFORE UPDATE ON studentresponses
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE INDEX IF NOT EXISTS studentresponses_student_id_idx ON studentresponses(student_id);
CREATE INDEX IF NOT EXISTS studentresponses_question_id_idx ON studentresponses(question_id);
CREATE INDEX IF NOT EXISTS studentresponses_submitted_by_user_idx ON studentresponses(submitted_by_user_id);

-- Preflight: these queries must return zero rows before enforcing uniqueness
-- and NOT NULL constraints.
SELECT student_id, question_id, COUNT(*) AS duplicate_count
FROM studentresponses
WHERE student_id IS NOT NULL AND question_id IS NOT NULL
GROUP BY student_id, question_id
HAVING COUNT(*) > 1;

SELECT COUNT(*) AS studentresponses_with_null_required_fields
FROM studentresponses
WHERE student_id IS NULL OR question_id IS NULL OR response IS NULL;

-- Enable after duplicate/null cleanup:
-- CREATE UNIQUE INDEX CONCURRENTLY IF NOT EXISTS studentresponses_student_question_uidx
-- ON studentresponses(student_id, question_id);
-- ALTER TABLE studentresponses ALTER COLUMN student_id SET NOT NULL;
-- ALTER TABLE studentresponses ALTER COLUMN question_id SET NOT NULL;
-- ALTER TABLE studentresponses ALTER COLUMN response SET NOT NULL;

CREATE OR REPLACE FUNCTION submit_student_response(
    p_actor_user_id UUID,
    p_question_id INT,
    p_response TEXT
)
RETURNS INT
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_student_id INT;
    v_course_id INT;
    v_response_id INT;
    v_existing_count BIGINT;
BEGIN
    SELECT s.student_id
    INTO v_student_id
    FROM students s
    JOIN users u ON u.id = s.user_id
    WHERE s.user_id = p_actor_user_id
      AND u.is_active = TRUE;

    IF v_student_id IS NULL THEN
        RAISE EXCEPTION 'actor is not an active student'
            USING ERRCODE = '42501';
    END IF;

    SELECT c.course_id
    INTO v_course_id
    FROM questions q
    JOIN assignments a ON a.assignment_id = q.assignment_id
    JOIN modules m ON m.module_id = a.module_id
    JOIN courses c ON c.course_id = m.course_id
    JOIN enrollments e ON e.course_id = c.course_id
                      AND e.student_id = v_student_id
                      AND e.status = 'active'
    WHERE q.question_id = p_question_id;

    IF v_course_id IS NULL THEN
        RAISE EXCEPTION 'student is not enrolled for this question'
            USING ERRCODE = '42501';
    END IF;

    SELECT COUNT(*), MIN(response_id)
    INTO v_existing_count, v_response_id
    FROM studentresponses
    WHERE student_id = v_student_id
      AND question_id = p_question_id;

    IF v_existing_count > 1 THEN
        RAISE EXCEPTION 'duplicate student responses must be cleaned before secure upsert'
            USING ERRCODE = '23505';
    ELSIF v_existing_count = 1 THEN
        UPDATE studentresponses
        SET response = p_response,
            submitted_by_user_id = p_actor_user_id,
            updated_at = now()
        WHERE response_id = v_response_id
        RETURNING response_id INTO v_response_id;
    ELSE
        INSERT INTO studentresponses (
            question_id,
            student_id,
            response,
            submitted_by_user_id,
            created_at,
            updated_at
        )
        VALUES (
            p_question_id,
            v_student_id,
            p_response,
            p_actor_user_id,
            now(),
            now()
        )
        RETURNING response_id INTO v_response_id;
    END IF;

    RETURN v_response_id;
END;
$$;

-- ---------------------------------------------------------------------------
-- 5. Authorization-safe result read functions
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION student_visible_responses(p_actor_user_id UUID)
RETURNS TABLE (
    response_id INT,
    question_id INT,
    student_id INT,
    response TEXT,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
)
LANGUAGE sql
SECURITY DEFINER
SET search_path = public
AS $$
    SELECT sr.response_id,
           sr.question_id,
           sr.student_id,
           sr.response,
           sr.created_at,
           sr.updated_at
    FROM studentresponses sr
    JOIN students s ON s.student_id = sr.student_id
    JOIN users u ON u.id = s.user_id
    WHERE s.user_id = p_actor_user_id
      AND u.is_active = TRUE;
$$;

CREATE OR REPLACE FUNCTION teacher_visible_course_results(
    p_actor_user_id UUID,
    p_course_id INT
)
RETURNS TABLE (
    course_id INT,
    student_id INT,
    student_name TEXT,
    question_id INT,
    response_id INT,
    response TEXT,
    submitted_at TIMESTAMPTZ
)
LANGUAGE sql
SECURITY DEFINER
SET search_path = public
AS $$
    SELECT c.course_id,
           s.student_id,
           s.name::TEXT AS student_name,
           q.question_id,
           sr.response_id,
           sr.response,
           sr.updated_at AS submitted_at
    FROM courses c
    JOIN modules m ON m.course_id = c.course_id
    JOIN assignments a ON a.module_id = m.module_id
    JOIN questions q ON q.assignment_id = a.assignment_id
    JOIN studentresponses sr ON sr.question_id = q.question_id
    JOIN students s ON s.student_id = sr.student_id
    WHERE c.course_id = p_course_id
      AND (
          EXISTS (
              SELECT 1
              FROM course_staff cs
              WHERE cs.course_id = c.course_id
                AND cs.user_id = p_actor_user_id
                AND cs.role IN ('teacher', 'ta', 'admin')
          )
          OR EXISTS (
              SELECT 1
              FROM user_roles ur
              WHERE ur.user_id = p_actor_user_id
                AND ur.role_key = 'admin'
          )
      );
$$;

-- ---------------------------------------------------------------------------
-- 6. Content/file access model
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS content_assets (
    asset_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id INT NOT NULL REFERENCES courses(course_id) ON DELETE CASCADE,
    module_id UUID REFERENCES modules(module_id) ON DELETE SET NULL,
    storage_key TEXT NOT NULL UNIQUE,
    original_filename TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    uploaded_by_user_id UUID REFERENCES users(id),
    visibility TEXT NOT NULL CHECK (visibility IN ('course', 'staff_only', 'admin_only')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS content_assets_course_visibility_idx
ON content_assets(course_id, visibility);

CREATE INDEX IF NOT EXISTS content_assets_module_idx
ON content_assets(module_id);

-- ---------------------------------------------------------------------------
-- 7. Audit events
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS audit_events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    actor_user_id UUID REFERENCES users(id),
    actor_email CITEXT,
    actor_roles TEXT[],
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT,
    course_id INT,
    student_id INT,
    request_id TEXT,
    source_ip INET,
    user_agent TEXT,
    success BOOLEAN NOT NULL,
    error_code TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS audit_events_actor_created_idx
ON audit_events(actor_user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS audit_events_entity_created_idx
ON audit_events(entity_type, entity_id, created_at DESC);

CREATE INDEX IF NOT EXISTS audit_events_course_created_idx
ON audit_events(course_id, created_at DESC);

-- ---------------------------------------------------------------------------
-- 8. RLS helper functions and deferred enablement
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION app_current_user_id()
RETURNS UUID
LANGUAGE sql
STABLE
AS $$
    SELECT NULLIF(current_setting('app.user_id', TRUE), '')::UUID;
$$;

CREATE OR REPLACE FUNCTION app_has_role(p_role_key TEXT)
RETURNS BOOLEAN
LANGUAGE sql
STABLE
AS $$
    SELECT EXISTS (
        SELECT 1
        FROM user_roles ur
        WHERE ur.user_id = app_current_user_id()
          AND ur.role_key = p_role_key
    );
$$;

-- Enable only after the API sets app.user_id inside every request transaction:
--
-- ALTER TABLE studentresponses ENABLE ROW LEVEL SECURITY;
--
-- CREATE POLICY studentresponses_student_read
-- ON studentresponses
-- FOR SELECT
-- USING (
--     student_id IN (
--         SELECT s.student_id
--         FROM students s
--         WHERE s.user_id = app_current_user_id()
--     )
--     OR app_has_role('admin')
-- );
--
-- CREATE POLICY studentresponses_teacher_read
-- ON studentresponses
-- FOR SELECT
-- USING (
--     EXISTS (
--         SELECT 1
--         FROM questions q
--         JOIN assignments a ON a.assignment_id = q.assignment_id
--         JOIN modules m ON m.module_id = a.module_id
--         JOIN course_staff cs ON cs.course_id = m.course_id
--         WHERE q.question_id = studentresponses.question_id
--           AND cs.user_id = app_current_user_id()
--     )
-- );

-- ---------------------------------------------------------------------------
-- 9. Least-privilege grant model
-- ---------------------------------------------------------------------------

-- Execute as a privileged migration role, then adapt role names to Cloud SQL:
--
-- CREATE ROLE hvvl_app_runtime NOINHERIT LOGIN;
-- CREATE ROLE hvvl_migration NOINHERIT LOGIN;
-- CREATE ROLE hvvl_reporting_readonly NOINHERIT LOGIN;
-- CREATE ROLE hvvl_service_sync NOINHERIT LOGIN;
--
-- REVOKE ALL ON SCHEMA public FROM PUBLIC;
-- GRANT USAGE ON SCHEMA public TO hvvl_app_runtime;
-- GRANT SELECT ON users, user_roles, roles, course_staff TO hvvl_app_runtime;
-- GRANT EXECUTE ON FUNCTION submit_student_response(UUID, INT, TEXT) TO hvvl_app_runtime;
-- GRANT EXECUTE ON FUNCTION student_visible_responses(UUID) TO hvvl_app_runtime;
-- GRANT EXECUTE ON FUNCTION teacher_visible_course_results(UUID, INT) TO hvvl_app_runtime;
-- GRANT INSERT ON audit_events TO hvvl_app_runtime;
