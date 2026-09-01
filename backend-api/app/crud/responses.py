# crud/responses.py
from typing import List, Dict, Any, Optional
from ..db.connection import get_db_connection
from ..schemas.schemas import ResponseCreate

# CRUD function to save a student's response to a question
async def create_student_response(conn, student_id: int, question_id: int, response_text: str) -> dict:
    # First, check if the response already exists for the given student_id and question_id
    existing_response = await conn.fetchrow(
        "SELECT response_id FROM studentresponses WHERE student_id = $1 AND question_id = $2",
        student_id, question_id
    )

    if existing_response:
        # Update the existing response
        await conn.execute(
            "UPDATE studentresponses SET response = $1 WHERE student_id = $2 AND question_id = $3",
            response_text, student_id, question_id
        )
        response_id = existing_response['response_id']  # Since the response exists, we use the existing id
    else:
        # Insert a new response and get the new id
        response_record = await conn.fetchrow(
            "INSERT INTO studentresponses (student_id, question_id, response) VALUES ($1, $2, $3) RETURNING response_id",
            student_id, question_id, response_text
        )
        response_id = response_record['response_id']  # Fetch the new response id

    return {"response_id": response_id, "student_id": student_id, "question_id": question_id, "response": response_text}


# Get student responses to each assignment question
async def get_student_assignments_responses(conn, student_id: int) -> List[Dict[str, Any]]:
    query = """
        SELECT 
            Modules.title AS module_title,
            Assignments.title AS assignment_title,
            Assignments.description AS assignment_description,
            Questions.question_text,
            CASE 
                WHEN Questions.question_type = 'multiple_choice' AND studentresponses.response IS NOT NULL THEN StudentOption.option_text
                ELSE studentresponses.response
            END AS student_response,
            CorrectOption.option_text AS correct_answer_text
        FROM 
            studentresponses
        LEFT JOIN 
            Questions ON studentresponses.question_id = Questions.question_id
        LEFT JOIN 
            Options AS StudentOption ON studentresponses.response::text = StudentOption.option_id::text AND Questions.question_type = 'multiple_choice'
        LEFT JOIN 
            Options AS CorrectOption ON Questions.correct_option_id::text = CorrectOption.option_id::text AND Questions.correct_option_id IS NOT NULL
        INNER JOIN 
            Assignments ON Questions.assignment_id = Assignments.assignment_id
        INNER JOIN 
            Modules ON Assignments.module_id = Modules.module_id
        WHERE 
            studentresponses.student_id = $1::int
        ORDER BY 
            Modules.title, 
            Assignments.assignment_id,
            Questions.question_id;
    """
    
    results = await conn.fetch(query, student_id)
    
    # Initialize a dictionary to hold the grouped data
    grouped_data = {}
    
    # Iterate over each row in the result set
    for row in results:
        row_data = dict(row)
        
        # Get the module title from the row, which will be used as the key for grouping
        module_title = row_data['module_title']
        
        # If the module title key doesn't exist in the dictionary, create a new list for it
        if module_title not in grouped_data:
            grouped_data[module_title] = {
                'module_title': module_title,
                'assignments': []
            }
        
        # Append the assignment and related response to the correct module group
        grouped_data[module_title]['assignments'].append({
            'assignment_title': row_data['assignment_title'],
            'assignment_description': row_data['assignment_description'],
            'question_text': row_data['question_text'],
            'student_response': row_data['student_response'],
            'correct_answer_text': row_data.get('correct_answer_text')  # .get() handles the case if key is missing
        })
    
    # Return the grouped data as a list of modules
    return list(grouped_data.values())


async def get_course_student_results(conn, course_id: int) -> List[Dict[str, Any]]:
    """Get all student quiz results for a course, grouped by student."""
    query = """
        SELECT
            Students.student_id,
            Students.name AS student_name,
            Students.email AS student_email,
            Modules.title AS module_title,
            Modules.module_id,
            Assignments.title AS assignment_title,
            Questions.question_id,
            Questions.question_text,
            Questions.question_type,
            CASE
                WHEN Questions.question_type = 'multiple_choice' AND studentresponses.response IS NOT NULL
                    THEN StudentOption.option_text
                ELSE studentresponses.response
            END AS student_response,
            CorrectOption.option_text AS correct_answer_text,
            CASE
                WHEN Questions.question_type = 'multiple_choice'
                    AND studentresponses.response IS NOT NULL
                    AND studentresponses.response::text = Questions.correct_option_id::text
                    THEN true
                ELSE false
            END AS is_correct
        FROM
            studentresponses
        INNER JOIN
            Students ON studentresponses.student_id = Students.student_id
        INNER JOIN
            Questions ON studentresponses.question_id = Questions.question_id
        LEFT JOIN
            Options AS StudentOption
            ON studentresponses.response::text = StudentOption.option_id::text
            AND Questions.question_type = 'multiple_choice'
        LEFT JOIN
            Options AS CorrectOption
            ON Questions.correct_option_id::text = CorrectOption.option_id::text
            AND Questions.correct_option_id IS NOT NULL
        INNER JOIN
            Assignments ON Questions.assignment_id = Assignments.assignment_id
        INNER JOIN
            Modules ON Assignments.module_id = Modules.module_id
        WHERE
            Modules.course_id = $1
        ORDER BY
            Students.name,
            Modules.title,
            Questions.question_id
    """
    results = await conn.fetch(query, course_id)

    # Group by student
    students = {}
    for row in results:
        r = dict(row)
        sid = r["student_id"]
        if sid not in students:
            students[sid] = {
                "student_id": sid,
                "student_name": r["student_name"],
                "student_email": r["student_email"],
                "modules": {},
                "total_questions": 0,
                "correct_answers": 0,
            }
        student = students[sid]
        mod_title = r["module_title"]
        if mod_title not in student["modules"]:
            student["modules"][mod_title] = {
                "module_title": mod_title,
                "questions": [],
                "total": 0,
                "correct": 0,
            }
        module = student["modules"][mod_title]
        module["questions"].append({
            "question_text": r["question_text"],
            "student_response": r["student_response"],
            "correct_answer": r["correct_answer_text"],
            "is_correct": r["is_correct"],
        })
        module["total"] += 1
        student["total_questions"] += 1
        if r["is_correct"]:
            module["correct"] += 1
            student["correct_answers"] += 1

    # Convert modules dict to list
    result_list = []
    for student in students.values():
        student["modules"] = list(student["modules"].values())
        result_list.append(student)

    return result_list