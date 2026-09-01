from __future__ import annotations

from uuid import UUID

from asyncpg import Connection
from fastapi import HTTPException

from .auth import AuthenticatedActor


def _normalize_email(email: str | None) -> str | None:
    return email.strip().lower() if isinstance(email, str) and email.strip() else None


def _is_privileged(actor: AuthenticatedActor) -> bool:
    return actor.is_service or actor.is_admin


async def get_student_id_for_actor(conn: Connection, actor: AuthenticatedActor) -> int | None:
    email = _normalize_email(actor.email)
    if not email:
        return None
    return await conn.fetchval(
        "SELECT student_id FROM students WHERE lower(email) = lower($1)",
        email,
    )


async def require_student_email_access(
    conn: Connection,
    actor: AuthenticatedActor,
    email: str,
) -> None:
    requested_email = _normalize_email(email)
    if not requested_email:
        raise HTTPException(status_code=400, detail="Invalid email")
    if _is_privileged(actor) or actor.is_teacher:
        return
    if actor.is_student and _normalize_email(actor.email) == requested_email:
        return
    raise HTTPException(status_code=403, detail="Access denied for requested student")


async def require_student_id_access(
    conn: Connection,
    actor: AuthenticatedActor,
    student_id: int,
) -> None:
    if _is_privileged(actor):
        return
    if actor.is_student:
        actor_student_id = await get_student_id_for_actor(conn, actor)
        if actor_student_id == student_id:
            return
        raise HTTPException(status_code=403, detail="Access denied for requested student")
    if actor.is_teacher:
        row = await conn.fetchrow(
            """
            SELECT 1
            FROM students s
            JOIN enrollments e ON e.student_id = s.student_id
            JOIN courses c ON c.course_id = e.course_id
            JOIN instructors i ON i.instructor_id = c.instructor_id
            WHERE s.student_id = $1
              AND lower(i.email) = lower($2)
            LIMIT 1
            """,
            student_id,
            actor.email or "",
        )
        if row:
            return
    raise HTTPException(status_code=403, detail="Access denied for requested student")


async def is_student_enrolled(conn: Connection, actor: AuthenticatedActor, course_id: int) -> bool:
    email = _normalize_email(actor.email)
    if not email:
        return False
    row = await conn.fetchrow(
        """
        SELECT 1
        FROM students s
        JOIN enrollments e ON e.student_id = s.student_id
        WHERE lower(s.email) = lower($1)
          AND e.course_id = $2
        LIMIT 1
        """,
        email,
        course_id,
    )
    return bool(row)


async def is_course_teacher(conn: Connection, actor: AuthenticatedActor, course_id: int) -> bool:
    email = _normalize_email(actor.email)
    if not email:
        return False
    row = await conn.fetchrow(
        """
        SELECT 1
        FROM courses c
        JOIN instructors i ON i.instructor_id = c.instructor_id
        WHERE c.course_id = $1
          AND lower(i.email) = lower($2)
        LIMIT 1
        """,
        course_id,
        email,
    )
    return bool(row)


async def require_course_read_access(
    conn: Connection,
    actor: AuthenticatedActor,
    course_id: int,
) -> None:
    if _is_privileged(actor):
        return
    # Staff who pass the server-side AD allow-list may open course landing
    # pages and course content. Roster/result reads and content mutations still
    # call require_course_staff_access, which remains course-scoped.
    if actor.is_teacher:
        return
    if actor.is_student and await is_student_enrolled(conn, actor, course_id):
        return
    raise HTTPException(status_code=403, detail="Access denied for requested course")


async def require_course_staff_access(
    conn: Connection,
    actor: AuthenticatedActor,
    course_id: int,
) -> None:
    if _is_privileged(actor):
        return
    if actor.is_teacher and str(course_id) in actor.course_ids:
        return
    if actor.is_teacher and await is_course_teacher(conn, actor, course_id):
        return
    raise HTTPException(status_code=403, detail="Staff access denied for requested course")


async def get_course_id_for_module(conn: Connection, module_id: UUID) -> int:
    course_id = await conn.fetchval(
        "SELECT course_id FROM modules WHERE module_id = $1",
        str(module_id),
    )
    if course_id is None:
        raise HTTPException(status_code=404, detail="Module not found")
    return int(course_id)


async def get_course_id_for_assignment(conn: Connection, assignment_id: int) -> int:
    course_id = await conn.fetchval(
        """
        SELECT m.course_id
        FROM assignments a
        JOIN modules m ON m.module_id = a.module_id
        WHERE a.assignment_id = $1
        """,
        assignment_id,
    )
    if course_id is None:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return int(course_id)


async def get_course_id_for_question(
    conn: Connection,
    module_id: UUID,
    assignment_id: int,
    question_id: int,
) -> int:
    course_id = await conn.fetchval(
        """
        SELECT m.course_id
        FROM questions q
        JOIN assignments a ON a.assignment_id = q.assignment_id
        JOIN modules m ON m.module_id = a.module_id
        WHERE q.question_id = $1
          AND a.assignment_id = $2
          AND m.module_id = $3
        """,
        question_id,
        assignment_id,
        str(module_id),
    )
    if course_id is None:
        raise HTTPException(status_code=404, detail="Question not found in requested module/assignment")
    return int(course_id)


async def resolve_student_response_writer(
    conn: Connection,
    actor: AuthenticatedActor,
    requested_student_id: int | None,
    course_id: int,
) -> int:
    if actor.is_service:
        if requested_student_id is None:
            raise HTTPException(status_code=400, detail="student_id is required for service writes")
        return requested_student_id
    if not actor.is_student:
        raise HTTPException(status_code=403, detail="Only students can submit student responses")
    actor_student_id = await get_student_id_for_actor(conn, actor)
    if actor_student_id is None:
        raise HTTPException(status_code=403, detail="Authenticated student is not provisioned")
    if requested_student_id is not None and requested_student_id != actor_student_id:
        raise HTTPException(status_code=403, detail="Cannot submit for another student")
    if not await is_student_enrolled(conn, actor, course_id):
        raise HTTPException(status_code=403, detail="Student is not enrolled in the requested course")
    return actor_student_id
