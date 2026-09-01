from fastapi import APIRouter, HTTPException, Depends, Path, Body
from typing import List, Dict, Any, Optional
from ....schemas.schemas import QuestionCreate
from ....crud.questions import create_question, get_questions_for_assignment
from ....core.auth import AuthenticatedActor, require_staff_actor

router = APIRouter()

@router.post("/assignments/{assignment_id}/questions", response_model=dict)
def create_question_endpoint(
    assignment_id: int = Path(..., description="The ID of the assignment"),
    question_data: QuestionCreate = Body(...),
    _actor: AuthenticatedActor = Depends(require_staff_actor),
):
    if question_data.assignment_id != assignment_id:
        raise HTTPException(
            status_code=400,
            detail=f"Mismatched assignment_id: {question_data.assignment_id} in body, {assignment_id} in path"
        )
    try:
        # Pass the `question_data` to your `create_question` function
        return create_question(question=question_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating question: {str(e)}")
