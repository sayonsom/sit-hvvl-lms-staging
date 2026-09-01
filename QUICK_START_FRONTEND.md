# 🚀 Quick Start Guide for Frontend Developers

## TL;DR

**Base URL**: `http://localhost:8080/api/v1`  
**Interactive Docs**: http://localhost:8080/docs  
**Health Check**: http://localhost:8080/health

## 🏃‍♂️ Starting the Backend

```bash
cd /path/to/alignbackendapis
./start_local.sh
```

Wait for "[ DONE ]Services are running!" message.

## ⚙️ Frontend Configuration

Add to your `.env.local`:

```env
REACT_APP_API_BASE_URL=http://localhost:8080
```

Or in your code:

```javascript
const API_BASE = 'http://localhost:8080/api/v1';
```

## 🎯 Most Used Endpoints

### Students
```javascript
// Get all students
GET /api/v1/students/

// Get student by email
GET /api/v1/students/{email}

// Create student
POST /api/v1/students/
Body: { name, email, date_of_birth, profile_picture, location }

// Get student's courses
GET /api/v1/students/{email}/courses
```

### Courses
```javascript
// Get all courses
GET /api/v1/courses

// Get course modules
GET /api/v1/courses/{course_id}/modules

// Get enrolled students
GET /api/v1/courses/{course_id}/students
```

### Modules & Assignments
```javascript
// Get module by ID (UUID)
GET /api/v1/modules/{module_id}

// Get assignments for module
GET /api/v1/modules/{module_id}/assignments/

// Get questions for module
GET /api/v1/modules/{module_id}/assignments
```

### Responses
```javascript
// Submit student response
POST /api/v1/modules/{module_id}/assignments/{assignment_id}/questions/{question_id}/responses
Body: { student_id, response_text }

// Get student's all responses
GET /api/v1/students/{student_id}/assignments/responses
```

## 📦 Sample API Service (TypeScript)

```typescript
// services/api.ts
const API_BASE = 'http://localhost:8080/api/v1';

export const api = {
  students: {
    getAll: () => fetch(`${API_BASE}/students/`).then(r => r.json()),
    getByEmail: (email: string) => 
      fetch(`${API_BASE}/students/${email}`).then(r => r.json()),
    getCourses: (email: string) =>
      fetch(`${API_BASE}/students/${email}/courses`).then(r => r.json()),
  },
  
  courses: {
    getAll: () => fetch(`${API_BASE}/courses`).then(r => r.json()),
    getModules: (courseId: number) =>
      fetch(`${API_BASE}/courses/${courseId}/modules`).then(r => r.json()),
  },
  
  modules: {
    getAssignments: (moduleId: string) =>
      fetch(`${API_BASE}/modules/${moduleId}/assignments/`).then(r => r.json()),
  },
  
  responses: {
    submit: (moduleId: string, assignmentId: number, questionId: number, studentId: number, responseText: string) =>
      fetch(`${API_BASE}/modules/${moduleId}/assignments/${assignmentId}/questions/${questionId}/responses`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ student_id: studentId, response_text: responseText })
      }).then(r => r.json()),
  }
};
```

## 🧪 Quick Test

```bash
# Test if backend is running
curl http://localhost:8080/health

# Get all courses
curl http://localhost:8080/api/v1/courses

# Get all students
curl http://localhost:8080/api/v1/students/
```

## 📊 Available Data

- [ DONE ]170 students
- [ DONE ]1 course (High Voltage Engineering)
- [ DONE ]5 modules
- [ DONE ]5 assignments
- [ DONE ]44 questions with 176 options
- [ DONE ]322 student responses

## 🔧 Troubleshooting

**Backend not responding?**
```bash
docker ps | grep alignbackendapis
```

**Check logs:**
```bash
docker-compose -f docker-compose.local.yml logs -f
```

**Stop services:**
```bash
./stop_local.sh
```

## 📚 Full Documentation

For complete API documentation with all endpoints, examples, and error handling:
👉 See `LOCAL_API_DOCUMENTATION.md`

## 🌐 Interactive API Explorer

Open in your browser: http://localhost:8080/docs

You can test all endpoints directly from this interface!

---

**Questions?** Check the full docs or visit http://localhost:8080/docs
