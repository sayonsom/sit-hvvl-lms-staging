from typing import List, Dict, Any, Optional
import asyncpg
from datetime import datetime
from ..db.connection import get_db_connection


# Get all students
async def get_students(conn) -> List[Dict[str, Any]]:
    # connection = get_db_connection()
    # cursor = connection.cursor()
    # cursor.execute("SELECT * FROM Students")
    # students = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    # cursor.close()
    # connection.close()
    # return students
    students = await conn.fetch("SELECT * FROM Students")
    return [dict(record) for record in students]




async def get_student_by_email(conn: asyncpg.Connection, email: str) -> Optional[Dict[str, Any]]:
    student = await conn.fetchrow("SELECT * FROM students WHERE email = $1", email)
    if student:
        return dict(student)
    return None

async def create_student(conn: asyncpg.Connection, name: str, email: str, date_of_birth: Optional[str], profile_picture: Optional[str], location: Optional[str]) -> Dict[str, Any]:
    query = """
        INSERT INTO students (name, email, date_of_birth, profile_picture, location) VALUES ($1, $2, $3, $4, $5)
        RETURNING *
    """
    student = await conn.fetchrow(query, name, email, date_of_birth, profile_picture, location)
    
    # Enroll in course ID 1 by default
    await enroll_students_in_course(conn, 2, [email])
    
    return dict(student)

async def update_student_login_info(conn: asyncpg.Connection, email: str) -> Optional[Dict[str, Any]]:
    query = """
        UPDATE students
        SET number_of_logins = number_of_logins + 1,
            last_login = CURRENT_TIMESTAMP
        WHERE email = $1
        RETURNING number_of_logins, last_login
    """
    login_info = await conn.fetchrow(query, email)
    if login_info:
        return dict(login_info)
    return None

async def get_number_of_logins_by_email(conn: asyncpg.Connection, email: str) -> Optional[int]:
    query = """
        SELECT number_of_logins
        FROM students
        WHERE email = $1
    """
    login_count = await conn.fetchval(query, email)
    return login_count

async def delete_student_by_email(conn: asyncpg.Connection, email: str) -> Dict[str, Any]:
    query_select = "SELECT * FROM students WHERE email = $1"
    student = await conn.fetchrow(query_select, email)
    if not student:
        raise ValueError("Student not found")
    
    query_delete = "DELETE FROM students WHERE email = $1 RETURNING *"
    deleted_student = await conn.fetchrow(query_delete, email)
    return dict(deleted_student)

async def enroll_students_in_course(conn: asyncpg.Connection, course_id: int, emails: List[str]) -> List[Dict[str, Any]]:
    enrolled_students = []
    for email in emails:
        student_id = await conn.fetchval("SELECT student_id FROM students WHERE email = $1", email)
        if student_id:
            enrollment_exists = await conn.fetchrow("SELECT * FROM enrollments WHERE student_id = $1 AND course_id = $2", student_id, course_id)
            if not enrollment_exists:
                await conn.execute("INSERT INTO enrollments (student_id, course_id, enrollment_date) VALUES ($1, $2, $3)", student_id, course_id, datetime.now())
                enrolled_students.append({"student_id": student_id, "email": email, "status": "enrolled"})
            else:
                enrolled_students.append({"student_id": student_id, "email": email, "status": "already_enrolled"})
        else:
            enrolled_students.append({"email": email, "status": "not_found"})
    return enrolled_students

async def unenroll_students_from_course(conn: asyncpg.Connection, course_id: int, emails: List[str]) -> List[Dict[str, Any]]:
    unenrolled_students = []
    for email in emails:
        student_id = await conn.fetchval("SELECT student_id FROM students WHERE email = $1", email)
        if student_id:
            enrollment_exists = await conn.fetchrow("SELECT * FROM enrollments WHERE student_id = $1 AND course_id = $2", student_id, course_id)
            if enrollment_exists:
                await conn.execute("DELETE FROM enrollments WHERE student_id = $1 AND course_id = $2", student_id, course_id)
                unenrolled_students.append({"student_id": student_id, "email": email, "status": "unenrolled"})
            else:
                unenrolled_students.append({"student_id": student_id, "email": email, "status": "not_enrolled"})
        else:
            unenrolled_students.append({"email": email, "status": "not_found"})
    return unenrolled_students

async def get_courses_for_student(conn: asyncpg.Connection, email: str) -> List[Dict[str, Any]]:
    query = """
        SELECT * FROM courses
        WHERE course_id IN (
            SELECT course_id
            FROM enrollments
            WHERE student_id = (SELECT student_id FROM students WHERE email = $1)
        )
    """
    courses = await conn.fetch(query, email)
    return [dict(course) for course in courses]

async def get_student_id_by_email(conn: asyncpg.Connection, email: str) -> Optional[int]:
    student_id = await conn.fetchval("SELECT student_id FROM students WHERE email = $1", email)
    if student_id is None:
        return None
    return student_id



# # Get a student by email
# def get_student_by_email(email: str) -> Optional[Dict[str, Any]]:
#     connection = get_db_connection()
#     cursor = connection.cursor()
#     cursor.execute("SELECT * FROM Students WHERE email = ?", (email,))
#     student_row = cursor.fetchone()
#     # Save the description before closing the cursor
#     description = cursor.description
#     cursor.close()
#     connection.close()
    
#     if student_row:
#         student = dict(zip([column[0] for column in description], student_row))
#         return student
#     return None


# # Create a new student
# def create_student(name: str, email: str, date_of_birth: Optional[str], profile_picture: Optional[str], location: Optional[str]) -> dict:
#     connection = get_db_connection()
#     cursor = connection.cursor()
#     # Assuming you have an INSERT stored procedure or just use a plain SQL INSERT command
#     sql_command = """
#         INSERT INTO Students (name, email, date_of_birth, profile_picture, city) VALUES (?, ?, ?, ?, ?)
#     """
#     cursor.execute(sql_command, (name, email, date_of_birth, profile_picture, location))
#     connection.commit()
    
#     # Retrieve the new student's ID if necessary, using @@IDENTITY or SCOPE_IDENTITY()
#     student_id = cursor.execute("SELECT @@IDENTITY AS 'Identity';").fetchval()
    
#     cursor.close()
#     connection.close()

#     # TEMPORARY: Enroll in course ID 1 by default

#     enroll_students_in_course(1, [email])
    
#     return {
#         "student_id": student_id,
#         "name": name,
#         "email": email,
#         "date_of_birth": date_of_birth,
#         "profile_picture": profile_picture,
#         "location": location
#     }

# # Update a student login information
# def update_student_login_info(email: str) -> dict:
#     connection = get_db_connection()
#     cursor = connection.cursor()
#     # Update the last login to the current time and increment the login count
#     sql_command = """
#         UPDATE Students
#         SET Number_of_Logins = Number_of_Logins + 1,
#             Last_Login = CURRENT_TIMESTAMP
#         WHERE email = ?
#     """
#     cursor.execute(sql_command, (email,))
#     connection.commit()

#     # Retrieve the updated login info
#     cursor.execute("SELECT Number_of_Logins, Last_Login FROM Students WHERE email = ?", (email,))
#     login_info = cursor.fetchone()
#     cursor.close()
#     connection.close()

#     return {
#         "email": email,
#         "number_of_logins": login_info[0],
#         "last_login": login_info[1]
#     }

# # Get the number of times a student has logged in by their email address
# def get_number_of_logins_by_email(email: str) -> int:
#     connection = get_db_connection()
#     cursor = connection.cursor()
#     cursor.execute("SELECT Number_of_Logins FROM Students WHERE email = ?", (email,))
#     login_count = cursor.fetchone()
#     cursor.close()
#     connection.close()
    
#     if login_count:
#         return login_count[0]
#     else:
#         return None


# # Delete a student by Email
# def delete_student_by_email(email: str) -> dict:
#     connection = get_db_connection()
#     cursor = connection.cursor()
#     cursor.execute("SELECT * FROM Students WHERE email = ?", (email,))
#     student = cursor.fetchone()
#     if not student:
#         raise Exception("Student not found")
#     cursor.execute("DELETE FROM Students WHERE email = ?", (email,))
#     connection.commit()
#     cursor.close()
#     connection.close()
#     return student

# # Enroll students in a course by their email address    
# def enroll_students_in_course(course_id: int, emails: List[str]) -> List[Dict[str, Any]]:
#     connection = get_db_connection()
#     cursor = connection.cursor()
#     enrolled_students = []
#     for email in emails:
#         # Get the student's ID
#         cursor.execute("SELECT student_id FROM Students WHERE email = ?", (email,))
#         student = cursor.fetchone()
#         if student:
#             student_id = student[0]
#             # Check if the student is already enrolled in the course
#             cursor.execute("SELECT * FROM Enrollments WHERE student_id = ? AND course_id = ?", (student_id, course_id))
#             enrollment = cursor.fetchone()
#             if not enrollment:
#                 # Enroll the student since they are not enrolled yet
#                 cursor.execute("INSERT INTO Enrollments (student_id, course_id, enrollment_date) VALUES (?, ?, ?)", (student_id, course_id, datetime.now()))
#                 connection.commit()
#                 enrolled_students.append({"student_id": student_id, "email": email, "status": "enrolled"})
#             else:
#                 # Student is already enrolled
#                 enrolled_students.append({"student_id": student_id, "email": email, "status": "already_enrolled"})
#         else:
#             # Student not found
#             enrolled_students.append({"email": email, "status": "not_found"})
#     cursor.close()
#     connection.close()
#     return enrolled_students

# #Un-enroll students from a course by their email address
# def unenroll_students_from_course(course_id: int, emails: List[str]) -> List[Dict[str, Any]]:
#     connection = get_db_connection()
#     cursor = connection.cursor()
#     unenrolled_students = []
#     for email in emails:
#         # Get the student's ID
#         cursor.execute("SELECT student_id FROM Students WHERE email = ?", (email,))
#         student = cursor.fetchone()
#         if student:
#             student_id = student[0]
#             # Check if the student is already enrolled in the course
#             cursor.execute("SELECT * FROM Enrollments WHERE student_id = ? AND course_id = ?", (student_id, course_id))
#             enrollment = cursor.fetchone()
#             if enrollment:
#                 # Un-enroll the student since they are enrolled
#                 cursor.execute("DELETE FROM Enrollments WHERE student_id = ? AND course_id = ?", (student_id, course_id))
#                 connection.commit()
#                 unenrolled_students.append({"student_id": student_id, "email": email, "status": "unenrolled"})
#             else:
#                 # Student is not enrolled
#                 unenrolled_students.append({"student_id": student_id, "email": email, "status": "not_enrolled"})
#         else:
#             # Student not found
#             unenrolled_students.append({"email": email, "status": "not_found"})
#     cursor.close()
#     connection.close()
#     return unenrolled_students


# # Get all courses a student is enrolled in by the students email address
# def get_courses_for_student(email: str) -> List[Dict[str, Any]]:
#     connection = get_db_connection()
#     cursor = connection.cursor()
#     cursor.execute("SELECT * FROM Courses WHERE course_id IN (SELECT course_id FROM Enrollments WHERE student_id = (SELECT student_id FROM Students WHERE email = ?))", (email,))
#     courses = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
#     cursor.close()
#     connection.close()
#     return courses


# def get_student_id_by_email(email: str) -> int:
#     connection = get_db_connection()
#     cursor = connection.cursor()
#     cursor.execute("SELECT student_id FROM Students WHERE email = ?", (email,))
#     student_row = cursor.fetchone()
#     cursor.close()
#     connection.close()

#     if student_row:
#         return student_row[0]  # Assuming student_id is the first column
#     else:
#         return None  # Or raise an exception if preferred