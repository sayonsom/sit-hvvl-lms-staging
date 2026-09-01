from fastapi import APIRouter, Depends

from ....core.auth import AuthenticatedActor, require_authenticated_user

router = APIRouter()


@router.get("/auth/me")
async def read_current_actor(
    actor: AuthenticatedActor = Depends(require_authenticated_user),
):
    return {
        "subject": actor.subject,
        "email": actor.email,
        "roles": sorted(actor.roles),
        "auth_method": actor.auth_method,
        "course_id": actor.course_id,
        "course_ids": sorted(actor.course_ids),
    }
