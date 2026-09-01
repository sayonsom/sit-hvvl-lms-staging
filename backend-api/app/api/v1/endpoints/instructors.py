from fastapi import APIRouter, HTTPException, Depends
from typing import Dict
from ....crud.instructors import create_instructor, update_instructor_by_email
from ....schemas.schemas import InstructorCreate, InstructorUpdate
from ....db.connection import get_db_connection
from ....core.auth import AuthenticatedActor, require_staff_actor

router = APIRouter()

@router.post("/instructors/", response_model=dict)
async def add_new_instructor(
    instructor: InstructorCreate,
    _actor: AuthenticatedActor = Depends(require_staff_actor),
    conn = Depends(get_db_connection),
):
    try:
        instructor_data = await create_instructor(conn, instructor)
        return instructor_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating instructor: {str(e)}")

@router.put("/instructors/{email}", response_model=dict)
async def update_instructor_by_email_endpoint(
    email: str,
    instructor: InstructorUpdate,
    _actor: AuthenticatedActor = Depends(require_staff_actor),
    conn = Depends(get_db_connection),
):
    try:
        updated_instructor = await update_instructor_by_email(conn, email, instructor)
        return updated_instructor
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error updating instructor: {str(e)}")
