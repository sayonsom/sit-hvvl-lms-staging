from ..db.connection import get_db_connection
import pandas as pd
from datetime import datetime, timedelta
from uuid import UUID
from io import BytesIO
from ..schemas.schemas import AssignmentCreate, QuestionCreate, Option
from datetime import datetime
import logging
from asyncpg import Connection

logging.basicConfig(level=logging.INFO)




async def create_assignment(conn: Connection, module_id: UUID, description: str, assignment_title: str, due_date: datetime) -> int:
    sql_assignment = """
        INSERT INTO Assignments (module_id, title, due_date)
        VALUES ($1, $2, $3)
        RETURNING assignment_id
    """

    assignment_id = await conn.fetchval(sql_assignment, str(module_id), assignment_title, due_date)
    if assignment_id is None:
        raise Exception("Failed to retrieve the new assignment ID.")
    return assignment_id

async def create_questions_and_options(conn: Connection, assignment_id: int, df: pd.DataFrame):
    for index, row in df.iterrows():
        logging.info(f"Processing row {index}")
        sql_question = """
            INSERT INTO Questions (assignment_id, question_text, question_type)
            VALUES ($1, $2, $3)
            RETURNING question_id
        """
        question_id = await conn.fetchval(sql_question, assignment_id, row['Question'], row['Question_Type'])

        if row['Question_Type'] == 'multiple_choice':
            options = [row['Option_A'], row['Option_B'], row['Option_C'], row['Option_D']]
            correct_option = row['Correct_Answer']
            correct_option_id = None

            for option in options:
                logging.info(f"Inserting option: {option}, while the correct option is: {correct_option}")
                sql_option = """
                    INSERT INTO Options (question_id, option_text)
                    VALUES ($1, $2)
                    RETURNING option_id
                """
                option_id = await conn.fetchval(sql_option, question_id, option)
                logging.info(f"Inserted option with ID: {option_id}")

                if option == correct_option:
                    correct_option_id = option_id
                    logging.info(f"Correct option found: {correct_option} with ID: {correct_option_id}")

            if correct_option_id is None:
                raise ValueError("Correct option not found in the options provided.")

            sql_update_question = """
                UPDATE Questions
                SET correct_option_id = $1
                WHERE question_id = $2
            """
            await conn.execute(sql_update_question, correct_option_id, question_id)


async def create_assignment_and_questions_from_csv(conn: Connection, module_id: UUID, assignment_title: str, due_date: datetime, csv_content: bytes) -> dict:
    sql_assignment = """
        INSERT INTO Assignments (module_id, title, due_date)
        VALUES ($1, $2, $3)
        RETURNING assignment_id
    """
    assignment_id = await conn.fetchval(sql_assignment, str(module_id), assignment_title, due_date)
    if assignment_id is None:
        raise Exception("Failed to retrieve the new assignment ID.")

    df = pd.read_csv(pd.io.common.BytesIO(csv_content))

    for index, row in df.iterrows():
        sql_question = """
            INSERT INTO Questions (assignment_id, question_text, question_type)
            VALUES ($1, $2, $3)
            RETURNING question_id
        """
        question_id = await conn.fetchval(sql_question, assignment_id, row['Question'], row['Question_Type'])

        if row['Question_Type'] == 'multiple_choice':
            options = [row['Option_A'], row['Option_B'], row['Option_C'], row['Option_D']]
            correct_option = row['Correct_Answer']
            correct_option_id = None  # Initialize correct_option_id

            for option in options:
                sql_option = """
                    INSERT INTO Options (question_id, option_text)
                    VALUES ($1, $2)
                    RETURNING option_id
                """
                option_id = await conn.fetchval(sql_option, question_id, option)

                if option == correct_option:
                    correct_option_id = option_id

            if correct_option_id is not None:  # Ensure correct_option_id was assigned
                sql_update_question = """
                    UPDATE Questions
                    SET correct_option_id = $1
                    WHERE question_id = $2
                """
                await conn.execute(sql_update_question, correct_option_id, question_id)
            else:
                raise ValueError(f"Correct option '{correct_option}' not found among the provided options for question '{row['Question']}'.")

    return {
        "assignment_id": assignment_id,
        "module_id": str(module_id),
        "title": assignment_title,
        "due_date": due_date.strftime("%Y-%m-%d"),
        "message": "Assignment and questions created successfully"
    }

# async def create_assignment(conn: Connection, assignment: AssignmentCreate) -> dict:
#     sql_command = """
#         INSERT INTO Assignments (module_id, title, description, due_date)
#         VALUES ($1, $2, $3, $4)
#         RETURNING assignment_id
#     """
#     assignment_id = await conn.fetchval(sql_command, assignment.module_id, assignment.title, assignment.description, assignment.due_date)
#     return {
#         "assignment_id": assignment_id,
#         **assignment.dict(),
#         "due_date": assignment.due_date.strftime("%Y-%m-%d")  # Format date if necessary
#     }

async def get_assignments_for_module(conn: Connection, module_id: int) -> list:
    sql_command = "SELECT * FROM Assignments WHERE module_id = $1"
    rows = await conn.fetch(sql_command, module_id)
    return [dict(row) for row in rows]

async def update_assignment(conn: Connection, assignment_id: int, assignment: AssignmentCreate) -> dict:
    sql_select = "SELECT * FROM Assignments WHERE assignment_id = $1"
    existing_assignment = await conn.fetchrow(sql_select, assignment_id)
    if not existing_assignment:
        raise ValueError("Assignment not found")

    sql_update = """
        UPDATE Assignments
        SET module_id = $1, title = $2, description = $3, due_date = $4
        WHERE assignment_id = $5
    """
    await conn.execute(sql_update, assignment.module_id, assignment.title, assignment.description, assignment.due_date, assignment_id)
    return {
        "assignment_id": assignment_id,
        **assignment.model_dump(),
        "due_date": assignment.due_date.strftime("%Y-%m-%d")  # Format date if necessary
    }

async def delete_assignment(conn: Connection, assignment_id: int) -> dict:
    sql_select = "SELECT * FROM Assignments WHERE assignment_id = $1"
    existing_assignment = await conn.fetchrow(sql_select, assignment_id)
    if not existing_assignment:
        raise ValueError("Assignment not found")

    sql_delete = "DELETE FROM Assignments WHERE assignment_id = $1"
    await conn.execute(sql_delete, assignment_id)
    return dict(existing_assignment)

async def delete_assignment_and_related_questions(conn: Connection, module_id: UUID) -> dict:
    try:
        sql_nullify_correct_option = """
            UPDATE Questions
            SET correct_option_id = NULL
            WHERE assignment_id IN (
                SELECT assignment_id FROM Assignments WHERE module_id = $1
            )
        """
        await conn.execute(sql_nullify_correct_option, str(module_id))

        sql_delete_options = """
            DELETE FROM Options 
            WHERE question_id IN (
                SELECT question_id FROM Questions WHERE assignment_id IN (
                    SELECT assignment_id FROM Assignments WHERE module_id = $1
                )
            )
        """
        await conn.execute(sql_delete_options, str(module_id))

        sql_delete_questions = """
            DELETE FROM Questions 
            WHERE assignment_id IN (
                SELECT assignment_id FROM Assignments WHERE module_id = $1
            )
        """
        await conn.execute(sql_delete_questions, str(module_id))

        sql_delete_assignments = "DELETE FROM Assignments WHERE module_id = $1"
        await conn.execute(sql_delete_assignments, str(module_id))

        return {"message": "Assignment and related questions and options deleted successfully"}
    except Exception as e:
        raise e
