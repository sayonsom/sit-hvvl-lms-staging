from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, HttpUrl, Field, UUID4
from datetime import date

# Response Schema
class RephraseRequest(BaseModel):
    text: str

# Student Schema
class StudentBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    name: str
    email: EmailStr
    date_of_birth: Optional[date] = None

class StudentCreate(StudentBase):
    profile_picture: Optional[HttpUrl] = None
    location: Optional[str] = None

class StudentUpdate(StudentBase):
    profile_picture: Optional[HttpUrl] = None
    location: Optional[str] = None

class StudentInDBBase(StudentBase):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    student_id: int = Field(..., alias="id")
    profile_picture: Optional[HttpUrl] = None
    location: Optional[str] = None

class Student(StudentInDBBase):
    pass

# Instructor Schema
class InstructorBase(BaseModel):
    name: str
    email: EmailStr
    organization: Optional[str] = None
    city: Optional[str] = None
    profile_picture: Optional[HttpUrl] = None
    linkedin: Optional[HttpUrl] = None
    website: Optional[HttpUrl] = None
    biography: Optional[str] = None

class InstructorCreate(InstructorBase):
    pass

class InstructorUpdate(InstructorBase):
    pass

class InstructorInDBBase(InstructorBase):
    model_config = ConfigDict(from_attributes=True)

    instructor_id: int = Field(..., alias="id")

class Instructor(InstructorInDBBase):
    pass

# Course Schema
class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    course_image: Optional[HttpUrl] = None
    enrollment_status: Optional[str] = None
    enrollment_begin_date: Optional[date] = None
    enrollment_end_date: Optional[date] = None
    session_start_date: Optional[date] = None
    session_end_date: Optional[date] = None
    course_webpage: Optional[HttpUrl] = None
    syllabus_pdf_link: Optional[HttpUrl] = None

class CourseCreate(CourseBase):
    instructor_id: int

class CourseUpdate(CourseBase):
    instructor_id: Optional[int] = None

class CourseInDBBase(CourseBase):
    model_config = ConfigDict(from_attributes=True)

    course_id: int = Field(..., alias="id")

class Course(CourseInDBBase):
    pass

# Enrollment Schema
class EnrollmentBase(BaseModel):
    student_id: int
    course_id: int
    enrollment_date: date
    expiration_date: Optional[date] = None

class EnrollmentCreate(EnrollmentBase):
    pass

class EnrollmentUpdate(BaseModel):
    expiration_date: Optional[date] = None

class EnrollmentInDBBase(EnrollmentBase):
    model_config = ConfigDict(from_attributes=True)

    enrollment_id: int = Field(..., alias="id")

class Enrollment(EnrollmentInDBBase):
    pass

# Module Schema
class ModuleBase(BaseModel):
    module_id: Optional[UUID4] = None
    course_id: int
    title: str
    description: Optional[str] = None
    theory: Optional[str] = None
    plottingexperimentconfig: Optional[str] = None
    InteractiveConfig: Optional[str] = None
    concept: Optional[str] = None
    fun_fact: Optional[str] = None
    interactive_file: Optional[str] = None
    attachment_1_link: Optional[str] = None
    attachment_2_link: Optional[str] = None
    attachment_3_link: Optional[str] = None
    video_link_1: Optional[str] = None
    video_link_2: Optional[str] = None

class ModuleInDBBase(ModuleBase):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    module_id: UUID = Field(..., alias="id")

class ModuleCreate(ModuleBase):
    pass

class ModuleUpdate(ModuleBase):
    pass

class Module(ModuleInDBBase):
    pass


class Option(BaseModel):
    option_id: int
    option_text: str

class Question(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    question_id: int
    assignment_id: int
    question_text: str
    question_type: str
    correct_option_id: Optional[int] = None
    options: List[Option] = Field(default_factory=list)

class Assignment(BaseModel):
    assignment_id: int
    title: str
    description: Optional[str] = None
    due_date: Optional[date] = None
    questions: List[Question] = Field(default_factory=list)  # Provides an empty list by default

class ModuleAssignments(BaseModel):
    module_id: UUID
    """
    assignments=[Assignment(assignment_id=1, title='Default Assignment', description='Basic questions to demonstrate fundamental understanding of the topic', due_date=datetime.date(2024, 1, 21), questions=[Question(question_id=1, assignment_id=1, question_text='Explain the basic principle behind the operation of an impulse voltage generator. How does it differ from a standard voltage generator?', question_type='long_text', correct_option_id=None, options=[]), Question(question_id=2, assignment_id=1, question_text='Discuss the importance of impulse voltage generators in testing high voltage equipment.', question_type='long_text', correct_option_id=None, options=[]), Question(question_id=1002, assignment_id=1, question_text='What is the primary purpose of an impulse voltage generator?', question_type='multiple_choice', correct_option_id=None, options=[Option(option_id=1, option_text='To generate continuous high voltage'), Option(option_id=2, option_text='To simulate lightning strikes'), Option(option_id=3, option_text='To power large motors'), Option(option_id=4, option_text='To charge batteries')])])]
    """
    assignments: List[Assignment] = Field(default_factory=list)
class QuestionBase(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "assignment_id": 1,
                "question_text": "What is the capital of France?",
                "question_type": "multiple_choice",
                "options": ["Paris", "London", "Berlin", "Madrid"],
                "correct_option_index": 0,
            }
        }
    )

    question_id: int
    assignment_id: int
    question_text: str
    question_type: str
    options: Optional[List[Option]] = Field(default_factory=list)
    correct_option_index: Optional[int] = None

# Assignment Schema
class AssignmentBase(BaseModel):
    assignment_id: int
    module_id: UUID
    title: str
    description: Optional[str] = None
    due_date: date
    questions: Optional[List[QuestionBase]] = Field(default_factory=list)

class AssignmentCreate(BaseModel):
    module_id: UUID
    title: str
    description: Optional[str] = None
    due_date: Optional[date] = None


class AssignmentData(BaseModel):
    module_id: UUID
    assignment_title: str
    due_date: Optional[date] = None

class AssignmentUpdate(Assignment):
    pass

class AssignmentInDBBase(Assignment):
    model_config = ConfigDict(from_attributes=True)

    assignment_id: int = Field(..., alias="id")

# class Assignment(AssignmentInDBBase):
#     pass



# Question Schema


class QuestionCreate(QuestionBase):
    pass

class QuestionUpdate(QuestionBase):
    pass

class QuestionInDBBase(QuestionBase):
    model_config = ConfigDict(from_attributes=True)

    question_id: int = Field(..., alias="id")

# class Question(QuestionInDBBase):
#     pass


# Team Schema
class TeamBase(BaseModel):
    name: str
    description: Optional[str] = None

class TeamCreate(TeamBase):
    pass

class TeamUpdate(TeamBase):
    pass

class TeamInDBBase(TeamBase):
    model_config = ConfigDict(from_attributes=True)

    team_id: int = Field(..., alias="id")

class Team(TeamInDBBase):
    pass

# Team Assignment Schema
class TeamAssignmentBase(BaseModel):
    assignment_id: int
    team_id: int
    due_date: date

class TeamAssignmentCreate(TeamAssignmentBase):
    pass

class TeamAssignmentUpdate(TeamAssignmentBase):
    pass

class TeamAssignmentInDBBase(TeamAssignmentBase):
    model_config = ConfigDict(from_attributes=True)

    team_assignment_id: int = Field(..., alias="id")

class TeamAssignment(TeamAssignmentInDBBase):
    pass

# Team Member Schema
class TeamMemberBase(BaseModel):
    team_id: int
    student_id: int
    role: Optional[str] = None  # Role could be 'leader', 'member', etc.

class TeamMemberCreate(TeamMemberBase):
    pass

class TeamMemberUpdate(TeamMemberBase):
    pass

class TeamMemberInDBBase(TeamMemberBase):
    model_config = ConfigDict(from_attributes=True)

    team_member_id: int = Field(..., alias="id")

class TeamMember(TeamMemberInDBBase):
    pass

# Response Schema
class ResponseBase(BaseModel):
    question_id: int
    student_id: int
    response: str  # Could be an option_id or text

class ResponseCreate(ResponseBase):
    pass

class ResponseUpdate(ResponseBase):
    pass

class ResponseInDBBase(ResponseBase):
    model_config = ConfigDict(from_attributes=True)

    response_id: int = Field(..., alias="id")

class Response(ResponseInDBBase):
    pass
