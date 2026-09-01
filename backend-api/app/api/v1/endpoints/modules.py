from fastapi import APIRouter, HTTPException, Depends, Path, UploadFile, File, Form
from uuid import UUID
import openai
from openai import AsyncOpenAI
import asyncio
from typing import List, Dict
from ....schemas.schemas import ModuleCreate, ModuleInDBBase
from ....crud.modules import create_module, get_modules_for_course, get_module_by_id, get_module_assignments, update_module, delete_module, get_questions_and_options_by_module
from ....db.connection import get_db_connection
from ....storage.local_storage import get_local_storage
from ....core.auth import AuthenticatedActor, require_authenticated_user, require_staff_actor
from ....core.rbac import get_course_id_for_module, require_course_read_access, require_course_staff_access
import random
import os
from pathlib import PurePosixPath

router = APIRouter()
MAX_CONTENT_UPLOAD_BYTES = int(os.getenv("MAX_CONTENT_UPLOAD_BYTES", "26214400"))
ALLOWED_CONTENT_EXTENSIONS = {".md", ".json", ".js", ".glb", ".gltf", ".png", ".jpg", ".jpeg", ".pdf", ".csv"}

def get_openai_client() -> AsyncOpenAI:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(status_code=503, detail="AI text service is not configured")
    return AsyncOpenAI(api_key=api_key)

async def rephrase_text_with_openai(text: str) -> str:
    async_openai_client = get_openai_client()
    list_of_prompts = ["analogy", "example", "metaphor", "simile"]
    chat_completion = await async_openai_client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Add some {random.choice(list_of_prompts)} related to every day world that a young person living in Singapore can relate to, and then rewrite this in a different way: \"{text}\". Keep it between 500-700 characters max."}
        ],
        model="gpt-3.5-turbo",  # Use an appropriate model
    )
    # Assuming the response structure, adjust if necessary based on the actual response
    response_message = chat_completion.choices[0].message.content.strip() if chat_completion.choices else "Could not generate alternative text."
    return response_message

async def fun_fact_finding_with_openai(text: str) -> str:
    async_openai_client = get_openai_client()
    list_of_prompts = ["Who invented discovered the concept", "The origin story", "Make it relevant to Singapore and tell something ", "Do you something about the worlds largest or smallest example", "Tell something interesting", "From when did people start using"]
    chat_completion = await async_openai_client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a professor teaching undergraduate electrical engineering students."},
            {"role": "user", "content": f"{random.choice(list_of_prompts)} about \"{text}\". Keep it under 600 characters."}
        ],
        model="gpt-3.5-turbo",  # Use an appropriate model
    )
    # Assuming the response structure, adjust if necessary based on the actual response
    response_message = chat_completion.choices[0].message.content.strip() if chat_completion.choices else "Could not generate fun fact."
    return response_message

@router.post("/rephrase/")
async def rephrase(
    text: str,
    _actor: AuthenticatedActor = Depends(require_authenticated_user),
):
    try:
        # Since FastAPI supports asynchronous functions, you can await the rephrasing function directly
        rephrased_text = await rephrase_text_with_openai(text)
        return {"rephrased_text": rephrased_text}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not generate rephrased text")
    

@router.post("/funfact/")
async def funfact(
    text: str,
    _actor: AuthenticatedActor = Depends(require_authenticated_user),
):
    try:
        # Since FastAPI supports asynchronous functions, you can await the fun fact function directly
        fun_fact = await fun_fact_finding_with_openai(text)
        return {"fun_fact": fun_fact}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not generate fun fact")


# Endpoint to create a new module
@router.post("/modules/", response_model=dict)
async def add_new_module(
    course_id: int,
    module: ModuleCreate,
    actor: AuthenticatedActor = Depends(require_staff_actor),
    conn = Depends(get_db_connection),
):
    try:
        await require_course_staff_access(conn, actor, course_id)
        return await create_module(conn, course_id, module)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating module: {str(e)}")

# Endpoint to list all the modules for a course
@router.get("/courses/{course_id}/modules", response_model=List[Dict])
async def list_modules_for_course(
    course_id: int,
    actor: AuthenticatedActor = Depends(require_authenticated_user),
    conn = Depends(get_db_connection),
):
    try:
        await require_course_read_access(conn, actor, course_id)
        modules = await get_modules_for_course(conn, course_id)
        return modules
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# Endpoint to get a module by id
@router.get("/modules/{module_id}", response_model=ModuleInDBBase)
async def read_module(
    module_id: UUID = Path(..., title="The ID of the module to get"),
    actor: AuthenticatedActor = Depends(require_authenticated_user),
    conn = Depends(get_db_connection),
):
    try:
        course_id = await get_course_id_for_module(conn, module_id)
        await require_course_read_access(conn, actor, course_id)
        db_module = await get_module_by_id(conn, module_id)
        return db_module
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# Endpoint to update a module
@router.put("/modules/{module_id}", response_model=Dict)
async def update_module_endpoint(
    module_id: UUID,
    module: ModuleCreate,
    actor: AuthenticatedActor = Depends(require_staff_actor),
    conn = Depends(get_db_connection),
):
    try:
        course_id = await get_course_id_for_module(conn, module_id)
        await require_course_staff_access(conn, actor, course_id)
        updated_module = await update_module(conn, module_id, module)
        return updated_module
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# Endpoint to delete a module
@router.delete("/modules/{module_id}")
async def delete_module_endpoint(
    module_id: UUID,
    actor: AuthenticatedActor = Depends(require_staff_actor),
    conn = Depends(get_db_connection),
):
    try:
        course_id = await get_course_id_for_module(conn, module_id)
        await require_course_staff_access(conn, actor, course_id)
        deleted_module = await delete_module(conn, module_id)
        return deleted_module
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# Endpoint to get all the assignments and their Q&A for a module
@router.get("/modules/{module_id}/assignments", response_model=List[Dict])
async def get_questions_endpoint(
    module_id: UUID = Path(..., title="The UUID of the module to retrieve questions for"),
    actor: AuthenticatedActor = Depends(require_authenticated_user),
    conn = Depends(get_db_connection),
):
    try:
        course_id = await get_course_id_for_module(conn, module_id)
        await require_course_read_access(conn, actor, course_id)
        questions_and_options = await get_questions_and_options_by_module(conn, module_id)
        return questions_and_options
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# Endpoint to upload content files (markdown, JSON configs, JS compute scripts, 3D models)
@router.post("/upload-content/")
async def upload_content_file(
    file: UploadFile = File(...),
    folder: str = Form(...),
    _actor: AuthenticatedActor = Depends(require_staff_actor),
):
    try:
        safe_folder = PurePosixPath(folder.replace("\\", "/"))
        if safe_folder.is_absolute() or ".." in safe_folder.parts:
            raise HTTPException(status_code=400, detail="Invalid folder path")
        safe_name = PurePosixPath(file.filename or "").name
        suffix = PurePosixPath(safe_name).suffix.lower()
        if not safe_name or suffix not in ALLOWED_CONTENT_EXTENSIONS:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        storage = get_local_storage()
        bucket_name = os.environ.get("STORAGE_BUCKET_NAME", "align-hvl-2024-release1")
        file_data = await file.read()
        if len(file_data) > MAX_CONTENT_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail="File too large")
        blob_name = f"{safe_folder.as_posix().strip('/')}/{safe_name}"
        storage.upload_file(bucket_name, blob_name, file_data)
        return {"path": blob_name, "filename": file.filename}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")
