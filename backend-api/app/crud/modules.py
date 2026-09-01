from ..schemas.schemas import ModuleCreate
from ..schemas.schemas import AssignmentCreate, ModuleAssignments, Assignment, Question, Option
from ..db.connection import get_db_connection
from datetime import datetime, timedelta
from ..crud.assignments import create_assignment
from uuid import UUID, uuid4
from typing import List, Dict, Any
import json
import logging
from asyncpg import Connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("myapp")

async def get_questions_and_options_by_module(conn: Connection, module_id: UUID) -> List[Dict]:
    sql_assignments = "SELECT * FROM assignments WHERE module_id = $1"
    assignments_data = await conn.fetch(sql_assignments, str(module_id))

    all_assignments = []
    for assignment_row in assignments_data:
        assignment_dict = dict(assignment_row)
        assignment_id = assignment_dict['assignment_id']

        sql_questions = "SELECT * FROM questions WHERE assignment_id = $1"
        questions_data = await conn.fetch(sql_questions, assignment_id)
        questions_list = []

        for question_row in questions_data:
            question_dict = dict(question_row)
            question_id = question_dict['question_id']

            if question_dict['question_type'] == 'multiple_choice':
                sql_options = "SELECT * FROM options WHERE question_id = $1"
                options_data = await conn.fetch(sql_options, question_id)
                question_dict['options'] = [dict(option_row) for option_row in options_data]
            else:
                question_dict['options'] = []

            questions_list.append(question_dict)

        assignment_dict['questions'] = questions_list
        all_assignments.append(assignment_dict)

    return all_assignments

async def create_module(conn: Connection, course_id: int, module: ModuleCreate) -> Dict[str, Any]:
    module_id = uuid4()  # Generate a new UUID for the module
    logger.info(f"Generated module_id: {module_id}")
    sql_command = """
        INSERT INTO modules (course_id, title, description, theory, plottingexperimentconfig, InteractiveConfig, concept, fun_fact, interactive_file, attachment_1_link, attachment_2_link, attachment_3_link, video_link_1, video_link_2, module_id)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
    """
    await conn.execute(sql_command, course_id, module.title, module.description, module.theory, module.plottingexperimentconfig, module.InteractiveConfig, module.concept, module.fun_fact, module.interactive_file, module.attachment_1_link, module.attachment_2_link, module.attachment_3_link, module.video_link_1, module.video_link_2, str(module_id))
    duedate = datetime.now().date() + timedelta(days=90)
    # assignment = AssignmentCreate(module_id=module_id, assignment_title="Default Assignment", description="Basic questions to demonstrate fundamental understanding of the topic", due_date=duedate)
    # await create_assignment(conn, module_id=module_id, assignment_title="Default Assignment", description="Basic questions to demonstrate fundamental understanding of the topic", due_date=duedate)
    return {"module_id": str(module_id), "course_id": course_id, **module.model_dump()}

async def get_modules_for_course(conn: Connection, course_id: int) -> List[Dict[str, Any]]:
    sql_command = "SELECT * FROM Modules WHERE course_id = $1"
    rows = await conn.fetch(sql_command, course_id)
    return [dict(row) for row in rows]

async def get_module_by_id(conn: Connection, module_id: UUID) -> Dict[str, Any]:
    sql_command = "SELECT * FROM Modules WHERE module_id = $1"
    row = await conn.fetchrow(sql_command, str(module_id))
    if row:
        return dict(row)
    else:
        raise ValueError("Module not found")

async def get_module_assignments(conn: Connection, module_id: UUID) -> List[Dict]:
    sql_assignments = "SELECT * FROM Assignments WHERE module_id = $1"
    assignments_data = await conn.fetch(sql_assignments, str(module_id))
    
    all_assignments = []
    for assignment_row in assignments_data:
        assignment_dict = dict(assignment_row)
        assignment_id = assignment_dict['assignment_id']

        sql_questions = "SELECT * FROM Questions WHERE assignment_id = $1"
        questions_data = await conn.fetch(sql_questions, assignment_id)
        questions_list = []

        for question_row in questions_data:
            question_dict = dict(question_row)
            if question_dict['question_type'] == 'multiple_choice':
                sql_options = "SELECT * FROM Options WHERE question_id = $1"
                options_data = await conn.fetch(sql_options, question_dict['question_id'])
                question_dict['options'] = [dict(option_row) for option_row in options_data]
            else:
                question_dict['options'] = []
            
            questions_list.append(question_dict)

        assignment_dict['questions'] = questions_list
        all_assignments.append(assignment_dict)
    
    return all_assignments

async def update_module(conn: Connection, module_id: UUID, module: ModuleCreate) -> Dict[str, Any]:
    sql_select = "SELECT * FROM Modules WHERE module_id = $1"
    existing_module = await conn.fetchrow(sql_select, str(module_id))
    if not existing_module:
        raise ValueError("Module not found")

    sql_update = """
        UPDATE Modules
        SET title = $1, description = $2, theory = $3, concept = $4, fun_fact = $5,
            attachment_1_link = $6, attachment_2_link = $7, attachment_3_link = $8,
            video_link_1 = $9, video_link_2 = $10,
            plottingexperimentconfig = $11, InteractiveConfig = $12, interactive_file = $13
        WHERE module_id = $14
    """
    await conn.execute(sql_update, module.title, module.description, module.theory, module.concept, module.fun_fact, module.attachment_1_link, module.attachment_2_link, module.attachment_3_link, module.video_link_1, module.video_link_2, module.plottingexperimentconfig, module.InteractiveConfig, module.interactive_file, str(module_id))
    return {"module_id": module_id, **module.model_dump()}

async def delete_module(conn: Connection, module_id: UUID) -> Dict[str, Any]:
    sql_select = "SELECT * FROM Modules WHERE module_id = $1"
    existing_module = await conn.fetchrow(sql_select, str(module_id))
    if not existing_module:
        raise ValueError("Module not found")

    sql_delete = "DELETE FROM Modules WHERE module_id = $1"
    await conn.execute(sql_delete, str(module_id))
    return dict(existing_module)
