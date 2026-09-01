from typing import List, Dict, Any
from asyncpg import Connection
from ..db.connection import get_db_connection
from ..schemas.schemas import CourseCreate

# Add a new course
async def create_course(conn: Connection, course: CourseCreate) -> Dict[str, Any]:
    sql_command = """
        INSERT INTO Courses (title, description, instructor_id, course_image, enrollment_status, enrollment_begin_date, enrollment_end_date, session_start_date, session_end_date, course_webpage, syllabus_pdf_link) 
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        RETURNING course_id
    """
    course_id = await conn.fetchval(sql_command, course.title, course.description, course.instructor_id, course.course_image, course.enrollment_status, course.enrollment_begin_date, course.enrollment_end_date, course.session_start_date, course.session_end_date, course.course_webpage, course.syllabus_pdf_link)

    return {
        "course_id": course_id,
        "title": course.title,
        "description": course.description,
        "course_image": course.course_image,
        "enrollment_status": course.enrollment_status,
        "enrollment_begin_date": course.enrollment_begin_date,
        "enrollment_end_date": course.enrollment_end_date,
        "session_start_date": course.session_start_date,
        "session_end_date": course.session_end_date,
        "course_webpage": course.course_webpage,
        "syllabus_pdf_link": course.syllabus_pdf_link
    }

# Get all courses for a given instructor
async def get_courses_for_instructor(conn: Connection, instructor_id: int) -> List[Dict[str, Any]]:
    sql_command = "SELECT * FROM Courses WHERE instructor_id = $1"
    rows = await conn.fetch(sql_command, instructor_id)
    return [dict(row) for row in rows]

# Get all courses a student is enrolled in by the student's email address
async def get_courses_for_student(conn: Connection, email: str) -> List[Dict[str, Any]]:
    sql_command = """
        SELECT * FROM Courses 
        WHERE course_id IN (
            SELECT course_id FROM Enrollments 
            WHERE student_id = (
                SELECT student_id FROM Students WHERE email = $1
            )
        )
    """
    rows = await conn.fetch(sql_command, email)
    return [dict(row) for row in rows]

# Get enrolled students by course ID
async def get_enrolled_students(conn: Connection, course_id: int) -> List[Dict[str, Any]]:
    sql_command = """
        SELECT * FROM Students 
        WHERE student_id IN (
            SELECT student_id FROM Enrollments WHERE course_id = $1
        )
    """
    rows = await conn.fetch(sql_command, course_id)
    return [dict(row) for row in rows]

# List all courses
async def get_courses(conn: Connection) -> List[Dict[str, Any]]:
    sql_command = "SELECT * FROM Courses"
    rows = await conn.fetch(sql_command)
    return [dict(row) for row in rows]

# Get a course by internal URL
async def get_course_by_internal_url(conn: Connection, internal_url) -> Dict[str, Any]:
    sql_command = "SELECT * FROM courses WHERE course_id = $1"
    row = await conn.fetchrow(sql_command, internal_url)
    if row:
        return dict(row)
    else:
        raise ValueError("Course not found")
