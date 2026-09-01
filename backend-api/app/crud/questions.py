from ..schemas.schemas import QuestionCreate
from ..db.connection import get_db_connection

def create_question(question: QuestionCreate):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Insert the question into the Questions table without options
    sql_command = "INSERT INTO Questions (assignment_id, question_text, question_type) VALUES (?, ?, ?)"
    cursor.execute(sql_command, (question.assignment_id, question.question_text, question.question_type))
    question_id = cursor.execute("SELECT @@IDENTITY AS 'Identity';").fetchval()
    
    # Insert options into the Options table if there are any
    if question.options:
        options_values = [(question_id, option_text) for option_text in question.options]
        cursor.executemany("INSERT INTO Options (question_id, option_text) VALUES (?, ?)", options_values)
        
        # Update the Questions table with the correct_option_id
        if question.correct_option_index is not None and 0 <= question.correct_option_index < len(question.options):
            correct_option_id = cursor.execute("""
                SELECT option_id FROM Options 
                WHERE question_id = ? AND option_text = ?""",
                (question_id, question.options[question.correct_option_index])
            ).fetchval()
            cursor.execute("UPDATE Questions SET correct_option_id = ? WHERE question_id = ?", (correct_option_id, question_id))
    
    connection.commit()
    cursor.close()
    return {"question_id": question_id, **question.model_dump()}

def get_questions_for_assignment(assignment_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT q.*, o.option_text, o.option_id 
        FROM Questions q
        LEFT JOIN Options o ON q.question_id = o.question_id
        WHERE q.assignment_id = ?""", (assignment_id,))
    
    rows = cursor.fetchall()
    cursor.close()
    
    # Group options by question
    questions = {}
    for row in rows:
        question_id = row['question_id']
        if question_id not in questions:
            questions[question_id] = {
                "question_id": question_id,
                "assignment_id": row['assignment_id'],
                "question_text": row['question_text'],
                "question_type": row['question_type'],
                "correct_option_id": row['correct_option_id'],
                "options": []
            }
        if row['option_text']:
            questions[question_id]['options'].append(row['option_text'])

    return list(questions.values())



