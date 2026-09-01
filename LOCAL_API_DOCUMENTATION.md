# 🚀 Align Backend - Local API Documentation

## 📋 Table of Contents
- [Getting Started](#getting-started)
- [Base Configuration](#base-configuration)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
  - [Health Check](#health-check)
  - [Students](#students)
  - [Instructors](#instructors)
  - [Courses](#courses)
  - [Modules](#modules)
  - [Assignments](#assignments)
  - [Questions](#questions)
  - [Responses](#responses)
  - [File Storage](#file-storage)
- [Error Handling](#error-handling)
- [Testing the API](#testing-the-api)

---

## 🎯 Getting Started

### Prerequisites
- Docker Desktop must be running
- Backend services must be started using `./start_local.sh`

### Starting the Local Backend
```bash
cd /path/to/alignbackendapis
./start_local.sh
```

Wait for the success message confirming both PostgreSQL and FastAPI are running.

---

## ⚙️ Base Configuration

### Environment Variables for Frontend

```javascript
// .env.local or .env.development
REACT_APP_API_BASE_URL=http://localhost:8080
REACT_APP_API_VERSION=v1
```

### Base URLs
- **API Base URL**: `http://localhost:8080`
- **API v1 Endpoints**: `http://localhost:8080/api/v1`
- **Interactive API Docs**: `http://localhost:8080/docs`
- **Alternative API Docs**: `http://localhost:8080/redoc`

### CORS Configuration
The backend is configured to accept requests from:
- `http://localhost:3000` (default React/Next.js)
- `http://localhost:3100` (alternative port)
- Any origin (`*` - configured for development)

---

## 🔐 Authentication

Most endpoints are currently **open** for local development. Some endpoints check for JWT tokens:

```javascript
// Example: Adding auth header (if needed)
headers: {
  'Authorization': `Bearer ${yourJwtToken}`,
  'Content-Type': 'application/json'
}
```

---

## 📚 API Endpoints

### Health Check

#### Check API Health
```
GET /health
```

**Response:**
```json
{
  "status": "200 ok"
}
```

**Example:**
```javascript
fetch('http://localhost:8080/health')
  .then(res => res.json())
  .then(data => console.log(data));
```

---

### 👨‍🎓 Students

#### 1. Get All Students
```
GET /api/v1/students/
```

**Response:**
```json
[
  {
    "student_id": 7,
    "name": "testuser123@plexflo.com",
    "email": "testuser123@plexflo.com",
    "date_of_birth": "1999-01-01",
    "profile_picture": "https://...",
    "location": "Somewhere on Earth",
    "number_of_logins": 0
  }
]
```

#### 2. Get Student by Email
```
GET /api/v1/students/{email}
```

**Example:**
```javascript
fetch('http://localhost:8080/api/v1/students/testuser123@plexflo.com')
  .then(res => res.json())
  .then(student => console.log(student));
```

#### 3. Create New Student
```
POST /api/v1/students/
```

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "date_of_birth": "2000-01-15",
  "profile_picture": "https://example.com/avatar.jpg",
  "location": "Singapore"
}
```

**Example:**
```javascript
fetch('http://localhost:8080/api/v1/students/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: "John Doe",
    email: "john.doe@example.com",
    date_of_birth: "2000-01-15",
    profile_picture: "https://example.com/avatar.jpg",
    location: "Singapore"
  })
})
.then(res => res.json())
.then(data => console.log(data));
```

#### 4. Update Student Login Info
```
PUT /api/v1/students/{email}/login
```

Updates the login count for a student.

#### 5. Get Student Login Count
```
GET /api/v1/students/logins/{email}
```

**Response:**
```json
{
  "email": "testuser123@plexflo.com",
  "number_of_logins": 5
}
```

#### 6. Delete Student
```
DELETE /api/v1/students/{email}
```

#### 7. Get Student's Courses
```
GET /api/v1/students/{email}/courses
```

Returns all courses the student is enrolled in.

#### 8. Get Student ID by Email
```
GET /api/v1/student-id/{email}
```

**Response:**
```json
7
```

#### 9. Enroll Students in Course
```
POST /api/v1/enroll-in-course/{course_id}/enroll/
```

**Request Body:**
```json
["student1@example.com", "student2@example.com"]
```

#### 10. Unenroll Students from Course
```
POST /api/v1/unenroll-from-course/{course_id}/unenroll/
```

**Request Body:**
```json
["student1@example.com", "student2@example.com"]
```

---

### 👨‍🏫 Instructors

#### 1. Create New Instructor
```
POST /api/v1/instructors/
```

**Request Body:**
```json
{
  "name": "Dr. John Smith",
  "email": "john.smith@university.edu",
  "organization": "Singapore Institute of Technology",
  "city": "Singapore",
  "profile_picture": "https://example.com/profile.jpg",
  "linkedin": "https://linkedin.com/in/johnsmith",
  "website": "https://johnsmith.com",
  "biography": "Professor of Electrical Engineering"
}
```

#### 2. Update Instructor by Email
```
PUT /api/v1/instructors/{email}
```

**Request Body:**
```json
{
  "name": "Dr. John Smith Updated",
  "biography": "Updated biography"
}
```

---

### 📚 Courses

#### 1. Get All Courses
```
GET /api/v1/courses
```

**Response:**
```json
[
  {
    "course_id": 2,
    "title": "High Voltage Engineering",
    "description": "6-Credit Core Course...",
    "course_image": "https://...",
    "enrollment_status": "By Invite Only",
    "enrollment_begin_date": "2024-06-01",
    "enrollment_end_date": "2024-12-31",
    "session_start_date": "2024-06-01",
    "session_end_date": "2024-12-31",
    "course_webpage": "https://...",
    "syllabus_pdf_link": "https://...",
    "instructor_id": 1
  }
]
```

#### 2. Create New Course
```
POST /api/v1/courses/
```

**Request Body:**
```json
{
  "title": "Introduction to Power Systems",
  "description": "Fundamentals of electrical power systems",
  "course_image": "https://example.com/course.jpg",
  "enrollment_status": "Open",
  "enrollment_begin_date": "2025-01-01",
  "enrollment_end_date": "2025-12-31",
  "session_start_date": "2025-01-15",
  "session_end_date": "2025-05-15",
  "course_webpage": "https://university.edu/course",
  "syllabus_pdf_link": "https://university.edu/syllabus.pdf",
  "instructor_id": 1
}
```

#### 3. Get Course by Internal URL
```
GET /api/v1/courses/{internal_url}
```

#### 4. Get Enrolled Students in Course
```
GET /api/v1/courses/{course_id}/students
```

Returns a list of all students enrolled in the course.

---

### 📖 Modules

#### 1. Create New Module
```
POST /api/v1/modules/?course_id={course_id}
```

**Request Body:**
```json
{
  "title": "AC Circuits",
  "description": "Introduction to alternating current circuits",
  "order": 1,
  "content": "Module content here..."
}
```

#### 2. Get All Modules for a Course
```
GET /api/v1/courses/{course_id}/modules
```

**Response:**
```json
[
  {
    "module_id": "95ae078a-b69a-416c-bdf5-ee744bcf3b79",
    "course_id": 2,
    "title": "AC Circuits",
    "description": "...",
    "order": 1,
    "content": "..."
  }
]
```

#### 3. Get Module by ID
```
GET /api/v1/modules/{module_id}
```

**Note:** `module_id` is a UUID.

#### 4. Update Module
```
PUT /api/v1/modules/{module_id}
```

**Request Body:**
```json
{
  "title": "Updated Module Title",
  "description": "Updated description",
  "content": "Updated content"
}
```

#### 5. Delete Module
```
DELETE /api/v1/modules/{module_id}
```

#### 6. Get Module Assignments with Questions
```
GET /api/v1/modules/{module_id}/assignments
```

Returns all assignments for the module with their questions and options.

#### 7. AI-Powered Text Rephrasing
```
POST /api/v1/rephrase/?text={text_to_rephrase}
```

Uses OpenAI to rephrase text with analogies/metaphors.

**Response:**
```json
{
  "rephrased_text": "Rephrased version..."
}
```

#### 8. AI-Powered Fun Facts
```
POST /api/v1/funfact/?text={topic}
```

Generates interesting facts about a topic.

**Response:**
```json
{
  "fun_fact": "Did you know..."
}
```

---

### 📝 Assignments

#### 1. Get All Assignments for Module
```
GET /api/v1/modules/{module_id}/assignments/
```

**Response:**
```json
[
  {
    "assignment_id": 11,
    "module_id": "95ae078a-b69a-416c-bdf5-ee744bcf3b79",
    "title": "Default Assignment",
    "description": "",
    "due_date": "2024-09-02"
  }
]
```

#### 2. Create New Assignment
```
POST /api/v1/modules/{module_id}/assignments/
```

**Request Body:**
```json
{
  "title": "Week 1 Quiz",
  "description": "Basic understanding questions",
  "due_date": "2025-02-15"
}
```

#### 3. Upload Questions via CSV
```
POST /api/v1/upload_csv/?module_id={module_id}
```

**Form Data:**
- `file`: CSV file containing questions

**CSV Format:**
```csv
question_text,option_1,option_2,option_3,option_4,correct_option
"What is Ohm's Law?","V=IR","P=VI","E=MC²","F=MA",1
```

#### 4. Delete Assignment
```
DELETE /api/v1/modules/{module_id}/assignments/
```

---

### ❓ Questions

#### Create Question for Assignment
```
POST /api/v1/assignments/{assignment_id}/questions
```

**Request Body:**
```json
{
  "assignment_id": 11,
  "question_text": "What is the speed of light?",
  "question_type": "multiple_choice"
}
```

---

### ✍️ Responses

#### 1. Save Student Response
```
POST /api/v1/modules/{module_id}/assignments/{assignment_id}/questions/{question_id}/responses
```

**Request Body:**
```json
{
  "student_id": 7,
  "response_text": "3 x 10^8 m/s"
}
```

**Example:**
```javascript
fetch('http://localhost:8080/api/v1/modules/95ae078a.../assignments/11/questions/44/responses', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    student_id: 7,
    response_text: "3 x 10^8 m/s"
  })
})
.then(res => res.json())
.then(data => console.log(data));
```

#### 2. Get Student's Assignment Responses
```
GET /api/v1/students/{student_id}/assignments/responses
```

Returns all responses submitted by the student across all assignments.

---

### 📁 File Storage

#### 1. Generate Signed URL
```
GET /api/v1/generate-signed-url/?blob_name={file_path}
```

Generates a local signed URL for accessing files in local storage.

**Response:**
```json
{
  "url": "http://localhost:8080/api/v1/local-storage/encoded_path_here"
}
```

#### 2. Serve Local File
```
GET /api/v1/local-storage/{encoded_path}
```

Serves files from local storage (replacement for Google Cloud Storage).

---

## 🧪 Testing the API

### Using cURL

```bash
# Test health endpoint
curl http://localhost:8080/health

# Get all students
curl http://localhost:8080/api/v1/students/

# Get specific student
curl http://localhost:8080/api/v1/students/testuser123@plexflo.com

# Create a new student
curl -X POST http://localhost:8080/api/v1/students/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "date_of_birth": "2000-01-01",
    "profile_picture": "https://example.com/pic.jpg",
    "location": "Singapore"
  }'
```

### Using JavaScript/TypeScript

```typescript
// api.service.ts
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8080';
const API_V1 = `${API_BASE_URL}/api/v1`;

export const apiService = {
  // Students
  async getAllStudents() {
    const response = await fetch(`${API_V1}/students/`);
    return response.json();
  },

  async getStudentByEmail(email: string) {
    const response = await fetch(`${API_V1}/students/${email}`);
    return response.json();
  },

  async createStudent(studentData: any) {
    const response = await fetch(`${API_V1}/students/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(studentData)
    });
    return response.json();
  },

  // Courses
  async getAllCourses() {
    const response = await fetch(`${API_V1}/courses`);
    return response.json();
  },

  async getModulesForCourse(courseId: number) {
    const response = await fetch(`${API_V1}/courses/${courseId}/modules`);
    return response.json();
  },

  // Assignments
  async getAssignmentsForModule(moduleId: string) {
    const response = await fetch(`${API_V1}/modules/${moduleId}/assignments/`);
    return response.json();
  },

  async submitResponse(moduleId: string, assignmentId: number, questionId: number, studentId: number, responseText: string) {
    const response = await fetch(
      `${API_V1}/modules/${moduleId}/assignments/${assignmentId}/questions/${questionId}/responses`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_id: studentId,
          response_text: responseText
        })
      }
    );
    return response.json();
  }
};
```

### Using Axios

```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8080/api/v1',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Get all students
const students = await api.get('/students/');

// Create student
const newStudent = await api.post('/students/', {
  name: "John Doe",
  email: "john@example.com",
  date_of_birth: "2000-01-01",
  profile_picture: "https://example.com/pic.jpg",
  location: "Singapore"
});
```

---

## ⚠️ Error Handling

### Standard Error Response Format

```json
{
  "detail": "Error message here"
}
```

### Common HTTP Status Codes

- **200**: Success
- **201**: Created
- **400**: Bad Request (validation error, missing fields)
- **404**: Not Found (resource doesn't exist)
- **500**: Internal Server Error

### Error Handling Example

```javascript
async function fetchStudent(email) {
  try {
    const response = await fetch(`http://localhost:8080/api/v1/students/${email}`);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'An error occurred');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching student:', error.message);
    // Handle error in UI
  }
}
```

---

## 🔧 Troubleshooting

### Backend Not Responding

1. Check if Docker is running:
   ```bash
   docker ps
   ```

2. Verify services are up:
   ```bash
   docker ps | grep alignbackendapis
   ```

3. Check logs:
   ```bash
   docker-compose -f docker-compose.local.yml logs -f
   ```

### CORS Errors

If you see CORS errors in the browser console, ensure your frontend is running on one of these ports:
- `http://localhost:3000`
- `http://localhost:3100`

Or update `origins` in `main.py` to include your frontend URL.

### Database Connection Issues

Check PostgreSQL is running:
```bash
docker exec alignbackendapis-postgres-1 pg_isready -U alignuser -d aligndb
```

---

## 📊 Sample Data Available

Your local database currently has:
- **1 instructor**: Dr. Anurag Sharma, Dr. Dhivya Sampath Kumar
- **1 course**: High Voltage Engineering
- **5 modules** with various topics
- **5 assignments**
- **170 students**
- **170 enrollments**
- **44 questions**
- **176 options**
- **322 student responses**

---

## 🎯 Quick Reference

| Resource | Endpoint | Method |
|----------|----------|--------|
| All Students | `/api/v1/students/` | GET |
| Student by Email | `/api/v1/students/{email}` | GET |
| Create Student | `/api/v1/students/` | POST |
| All Courses | `/api/v1/courses` | GET |
| Course Modules | `/api/v1/courses/{course_id}/modules` | GET |
| Module Assignments | `/api/v1/modules/{module_id}/assignments/` | GET |
| Submit Response | `/api/v1/modules/{module_id}/assignments/{assignment_id}/questions/{question_id}/responses` | POST |

---

## 📞 Support

- **API Documentation (Interactive)**: http://localhost:8080/docs
- **Health Check**: http://localhost:8080/health
- **Stop Services**: `./stop_local.sh`
- **View Logs**: `docker-compose -f docker-compose.local.yml logs -f`

---

**Last Updated**: October 1, 2025  
**API Version**: v1  
**Backend Port**: 8080  
**Database Port**: 5432
