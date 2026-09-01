from typing import List, Dict, Any
from asyncpg import Connection
from ..db.connection import get_db_connection
from ..schemas.schemas import InstructorCreate, InstructorUpdate

# Create a new instructor
async def create_instructor(conn: Connection, instructor: InstructorCreate) -> Dict[str, Any]:
    sql_command = """
        INSERT INTO Instructors (name, email, organization, city, profile_picture, linkedin, website, biography) 
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8) 
        RETURNING instructor_id
    """
    instructor_id = await conn.fetchval(sql_command, instructor.name, instructor.email, instructor.organization, instructor.city, instructor.profile_picture, instructor.linkedin, instructor.website, instructor.biography)
    
    return {
        "instructor_id": instructor_id,
        "name": instructor.name,
        "email": instructor.email,
        "organization": instructor.organization,
        "city": instructor.city
    }

# API to modify an instructor field by finding them by email
async def update_instructor_by_email(conn: Connection, email: str, instructor: InstructorUpdate) -> Dict[str, Any]:
    sql_select = "SELECT * FROM Instructors WHERE email = $1"
    existing_instructor = await conn.fetchrow(sql_select, email)
    
    if not existing_instructor:
        raise ValueError("Instructor not found")
    
    sql_update = """
        UPDATE Instructors SET name = $1, email = $2, organization = $3, city = $4, profile_picture = $5, linkedin = $6, website = $7, biography = $8 
        WHERE email = $9
    """
    await conn.execute(sql_update, instructor.name, instructor.email, instructor.organization, instructor.city, instructor.profile_picture, instructor.linkedin, instructor.website, instructor.biography, email)
    
    updated_instructor = await conn.fetchrow(sql_select, email)
    
    return dict(updated_instructor)
