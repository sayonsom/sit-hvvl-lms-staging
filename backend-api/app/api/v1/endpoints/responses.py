from fastapi import APIRouter, HTTPException, Path, Body, Depends
from typing import List, Dict, Any, Optional
from ....schemas.schemas import ResponseCreate
from ....crud.responses import create_student_response, get_student_assignments_responses, get_course_student_results
from uuid import UUID
from ....db.connection import get_db_connection
from ....core.auth import AuthenticatedActor, require_authenticated_user, require_staff_actor
from ....core.rbac import (
    get_course_id_for_question,
    require_course_staff_access,
    require_student_id_access,
    resolve_student_response_writer,
)

router = APIRouter()

@router.post("/modules/{module_id}/assignments/{assignment_id}/questions/{question_id}/responses", response_model=Dict)
async def save_student_response(
    module_id: UUID = Path(..., title="The ID of the module"),
    assignment_id: int = Path(..., title="The ID of the assignment"),
    question_id: int = Path(..., title="The ID of the question"),
    student_id: Optional[int] = Body(None, embed=True, title="The ID of the student"),
    response_text: str = Body(..., embed=True, title="The student's response"),
    actor: AuthenticatedActor = Depends(require_authenticated_user),
    conn = Depends(get_db_connection),
):
    try:
        course_id = await get_course_id_for_question(conn, module_id, assignment_id, question_id)
        resolved_student_id = await resolve_student_response_writer(
            conn,
            actor,
            student_id,
            course_id,
        )
        response = await create_student_response(conn, resolved_student_id, question_id, response_text)
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    

@router.get("/courses/{course_id}/student-results", response_model=List[Dict[str, Any]])
async def read_course_student_results(
    course_id: int = Path(..., title="The ID of the course"),
    actor: AuthenticatedActor = Depends(require_staff_actor),
    conn = Depends(get_db_connection),
):
    try:
        await require_course_staff_access(conn, actor, course_id)
        results = await get_course_student_results(conn, course_id)
        return results
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.get("/students/{student_id}/assignments/responses", response_model=List[Dict[str, Any]])
async def read_student_assignments_responses(
    student_id: int = Path(..., title="The ID of the student"),
    actor: AuthenticatedActor = Depends(require_authenticated_user),
    conn = Depends(get_db_connection),
):
    try:
        await require_student_id_access(conn, actor, student_id)
        student_data = await get_student_assignments_responses(conn, student_id)
        if not student_data:
            raise HTTPException(status_code=404, detail="No assignment responses found for the student")
        return student_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
