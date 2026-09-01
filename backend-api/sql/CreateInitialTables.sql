-- Create the Students table first
CREATE TABLE Students (
    student_id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    date_of_birth DATE,
    profile_picture TEXT,
    location VARCHAR(255),
    number_of_logins INTEGER DEFAULT 0,
    last_login TIMESTAMP
);

CREATE TABLE Instructors (
    instructor_id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    organization VARCHAR(255),
    city VARCHAR(255),
    profile_picture TEXT,
    linkedin TEXT,
    website TEXT,
    biography TEXT
);

CREATE TABLE Courses (
    course_id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    description TEXT,
    course_image TEXT,
    enrollment_status VARCHAR(50),
    enrollment_begin_date DATE,
    enrollment_end_date DATE,
    session_start_date DATE,
    session_end_date DATE,
    course_webpage TEXT,
    syllabus_pdf_link TEXT,
    instructor_id INT,
    FOREIGN KEY (instructor_id) REFERENCES Instructors(instructor_id)
);

CREATE TABLE Enrollments (
    enrollment_id SERIAL PRIMARY KEY,
    student_id INT,
    course_id INT,
    enrollment_date DATE,
    expiration_date DATE,
    FOREIGN KEY (student_id) REFERENCES Students(student_id),
    FOREIGN KEY (course_id) REFERENCES Courses(course_id)
);

CREATE TABLE Modules (
    module_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id INT,
    title VARCHAR(255),
    description TEXT,
    theory TEXT,
    concept TEXT,
    fun_fact TEXT,
    interactive_file TEXT,
    attachment_1_link TEXT,
    attachment_2_link TEXT,
    attachment_3_link TEXT,
    video_link_1 TEXT,
    video_link_2 TEXT,
    plottingexperimentconfig TEXT,
    InteractiveConfig TEXT,
    FOREIGN KEY (course_id) REFERENCES Courses(course_id)
);

CREATE TABLE Assignments (
    assignment_id SERIAL PRIMARY KEY,
    module_id UUID,
    title VARCHAR(255),
    description TEXT,
    due_date DATE,
    FOREIGN KEY (module_id) REFERENCES Modules(module_id)
);

CREATE TABLE Questions (
    question_id SERIAL PRIMARY KEY,
    assignment_id INT,
    question_text TEXT,
    question_type VARCHAR(50),
    correct_option_id INT,
    FOREIGN KEY (assignment_id) REFERENCES Assignments(assignment_id)
);

CREATE TABLE Options (
    option_id SERIAL PRIMARY KEY,
    question_id INT,
    option_text TEXT,
    FOREIGN KEY (question_id) REFERENCES Questions(question_id)
);

CREATE TABLE studentresponses (
    response_id SERIAL PRIMARY KEY,
    question_id INT,
    student_id INT,
    response TEXT,
    FOREIGN KEY (question_id) REFERENCES Questions(question_id),
    FOREIGN KEY (student_id) REFERENCES Students(student_id)
);

CREATE TABLE Teams (
    team_id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    description TEXT
);

CREATE TABLE TeamMembers (
    team_member_id SERIAL PRIMARY KEY,
    team_id INT,
    student_id INT,
    role VARCHAR(255),
    FOREIGN KEY (team_id) REFERENCES Teams(team_id),
    FOREIGN KEY (student_id) REFERENCES Students(student_id)
);

CREATE TABLE TeamAssignments (
    team_assignment_id SERIAL PRIMARY KEY,
    assignment_id INT,
    team_id INT,
    due_date DATE,
    FOREIGN KEY (assignment_id) REFERENCES Assignments(assignment_id),
    FOREIGN KEY (team_id) REFERENCES Teams(team_id)
);

CREATE TABLE TeamAssignmentSubmissions (
    submission_id SERIAL PRIMARY KEY,
    team_assignment_id INT,
    team_id INT,
    submission_date DATE,
    submission_link TEXT,
    grade VARCHAR(255),
    FOREIGN KEY (team_assignment_id) REFERENCES TeamAssignments(team_assignment_id),
    FOREIGN KEY (team_id) REFERENCES Teams(team_id)
);
