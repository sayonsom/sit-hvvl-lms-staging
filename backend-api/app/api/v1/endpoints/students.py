from fastapi import APIRouter, HTTPException, Body, Depends, Path, Query
from fastapi.responses import FileResponse
from typing import List, Dict, Any, Optional
from asyncpg import Connection
from datetime import timedelta
import os
from ....schemas.schemas import StudentCreate, StudentUpdate
from ....storage.local_storage import get_local_storage
from ....crud.students import get_students, create_student, get_number_of_logins_by_email, delete_student_by_email, enroll_students_in_course,  get_courses_for_student, unenroll_students_from_course, update_student_login_info, get_student_by_email, get_student_id_by_email
from ....core.auth import AuthenticatedActor, get_optional_authenticated_actor, require_authenticated_user, require_service_token, require_staff_actor
from ....core.rbac import require_student_email_access
from ....db.connection import get_db_connection
router = APIRouter()

# Test CORS endpoint
@router.get("/test-cors")
async def test_cors():
    return {"message": "CORS is working!"}

# Ensure Access to Local Storage (replacing Google Storage)
@router.get("/generate-signed-url/")
async def generate_signed_url(
    blob_name: str,
    _actor: AuthenticatedActor = Depends(require_authenticated_user),
):
    try:
        # Use local storage instead of GCS
        local_storage = get_local_storage()
        bucket_name = os.getenv('STORAGE_BUCKET_NAME', 'align-hvl-2024-release1')

        if not local_storage.file_exists(bucket_name, blob_name):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Generate a local signed URL for the blob
        url = local_storage.generate_signed_url(
            bucket_name=bucket_name,
            blob_name=blob_name,
            expiration=timedelta(seconds=3600)
        )

        return {"url": url}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not generate file URL")

# Serve files from local storage
@router.get("/local-storage/{encoded_path}")
async def serve_local_file(
    encoded_path: str,
    expires: Optional[int] = Query(default=None),
    signature: Optional[str] = Query(default=None),
    actor: Optional[AuthenticatedActor] = Depends(get_optional_authenticated_actor),
):
    try:
        local_storage = get_local_storage()
        if actor is None and not local_storage.verify_signed_url(encoded_path, expires, signature):
            raise HTTPException(status_code=401, detail="Missing or invalid file authorization")
        bucket_name, blob_name = local_storage.decode_signed_url_path(encoded_path)
        
        file_path = local_storage.get_file_path(bucket_name, blob_name)
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(path=str(file_path))
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not serve file")

def user_has_role(token_payload: dict, roles: list) -> bool:
    user_roles = token_payload.get("roles", [])
    return any(role in user_roles for role in roles)

@router.get("/students/", response_model=List[Dict[str, Any]])
async def read_students(
    _actor: AuthenticatedActor = Depends(require_staff_actor),
    conn = Depends(get_db_connection),
):
    students = await get_students(conn)
    if not students:
        raise HTTPException(status_code=404, detail="No students found")
    return students

# Create a new student endpoint
@router.post("/students/", response_model=dict)
async def create_student_endpoint(
    student: StudentCreate,
    conn: Connection = Depends(get_db_connection),
    _service=Depends(require_service_token),
):
    try:
        new_student = await create_student(conn, student.name, student.email, student.date_of_birth, student.profile_picture, student.location)
        return new_student
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# API to find a student by Email
@router.get("/students/{email}", response_model=Dict[str, Any])
async def find_student_by_email(
    email: str,
    actor: AuthenticatedActor = Depends(require_authenticated_user),
    conn: Connection = Depends(get_db_connection),
):
    await require_student_email_access(conn, actor, email)
    student = await get_student_by_email(conn, email)
    if student:
        return student
    raise HTTPException(status_code=404, detail="Student not found")

# Endpoint to update login info for a student
@router.put("/students/{email}/login", response_model=dict)
async def update_student_login_endpoint(
    email: str = Path(..., description="The Email ID of the student"),
    conn: Connection = Depends(get_db_connection),
    _service=Depends(require_service_token),
):
    login_info = await update_student_login_info(conn, email)
    if not login_info:
        raise HTTPException(status_code=404, detail="Student not found")
    return login_info

# Endpoint to get the number of logins for a student by email
@router.get("/students/logins/{email}", response_model=Any)
async def get_student_logins_endpoint(
    email: str = Path(..., description="The email of the student"),
    actor: AuthenticatedActor = Depends(require_authenticated_user),
    conn: Connection = Depends(get_db_connection),
):
    await require_student_email_access(conn, actor, email)
    number_of_logins = await get_number_of_logins_by_email(conn, email)
    if number_of_logins is not None:
        return {"email": email, "number_of_logins": number_of_logins}
    else:
        raise HTTPException(status_code=404, detail="Student not found")

# Delete a student by Email
@router.delete("/students/{email}", response_model=Dict[str, Any])
async def delete_student_by_email_endpoint(
    email: str,
    conn: Connection = Depends(get_db_connection),
    _service=Depends(require_service_token),
):
    try:
        student = await delete_student_by_email(conn, email)
        return student
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

# Un-enroll students from a course by their email address
@router.post("/unenroll-from-course/{course_id}/unenroll/", response_model=List[Dict[str, Any]])
async def unenroll_students_from_course_endpoint(
    course_id: int,
    emails: List[str],
    conn: Connection = Depends(get_db_connection),
    _service=Depends(require_service_token),
):
    try:
        unenrolled_students = await unenroll_students_from_course(conn, course_id, emails)
        return unenrolled_students
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# Enroll students in a course by their email address
@router.post("/enroll-in-course/{course_id}/enroll/", response_model=List[Dict[str, Any]])
async def enroll_students_in_course_endpoint(
    course_id: int,
    emails: List[str],
    conn: Connection = Depends(get_db_connection),
    _service=Depends(require_service_token),
):
    try:
        enrolled_students = await enroll_students_in_course(conn, course_id, emails)
        return enrolled_students
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# Get all courses a student is enrolled in by the students email address
@router.get("/students/{email}/courses", response_model=List[Dict[str, Any]])
async def get_courses_for_student_endpoint(
    email: str,
    actor: AuthenticatedActor = Depends(require_authenticated_user),
    conn: Connection = Depends(get_db_connection),
):
    await require_student_email_access(conn, actor, email)
    try:
        courses = await get_courses_for_student(conn, email)
        return courses
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# API to get a student_id by email address of the student
@router.get("/student-id/{email}", response_model=int)
async def read_student_id_by_email(
    email: str = Path(..., title="The email of the student to find"),
    actor: AuthenticatedActor = Depends(require_authenticated_user),
    conn: Connection = Depends(get_db_connection),
):
    await require_student_email_access(conn, actor, email)
    student_id = await get_student_id_by_email(conn, email)
    if student_id:
        return student_id
    else:
        raise HTTPException(status_code=404, detail="Student not found")
