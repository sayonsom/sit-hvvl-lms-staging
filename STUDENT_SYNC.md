# Automatic Student Synchronization

## Overview
When a user logs in via Brightspace LTI, the system automatically creates or updates their student record in the PostgreSQL database (alignbackendapis).

## How It Works

### Flow
1. User clicks LTI link in Brightspace
2. Brightspace sends user to `/lti/login`
3. Backend redirects to Brightspace auth
4. Brightspace sends JWT to `/lti/launch`
5. Backend validates JWT and extracts user data
6. **🆕 Backend syncs student to PostgreSQL database**
7. Backend creates session and redirects to frontend
8. Frontend validates session and loads app

### Student Sync Logic

The `sync_student_to_backend()` function:

1. **Check if student exists** (`GET /api/v1/students/{email}`)
   - If exists: Update login info (`PUT /api/v1/students/{email}/login`)
   - If not: Create new student

2. **Create new student** (`POST /api/v1/students/`)
   - Name: From LTI user data
   - Email: From LTI user data
   - Profile Picture: From LTI user data (if available)
   - Date of Birth: null
   - Location: null
   - **Auto-enrolls in Course ID 2** (hardcoded in alignbackendapis)

## Configuration

### backend-lti/.env
```bash
BACKEND_API_URL=http://localhost:8080/api/v1
```

### Key Files Modified

**backend-lti/app/main.py:**
- Added `import httpx`
- Added `sync_student_to_backend()` function
- Calls sync after successful JWT validation

## Testing

### 1. Check Current Students
```bash
curl http://localhost:8080/api/v1/students/ | python3 -m json.tool
```

### 2. Login via Brightspace
Click your LTI link in Brightspace

### 3. Check Backend Logs
```bash
tail -50 logs/backend.log | grep -E "(Creating new student|Student.*exists|Successfully created)"
```

### 4. Verify Student Was Created
```bash
curl http://localhost:8080/api/v1/students/YOUR_EMAIL | python3 -m json.tool
```

## Logs

When a student logs in, you'll see logs like:

**New Student:**
```
INFO: Creating new student: sc@gridleaf.org
INFO: Successfully created student sc@gridleaf.org
INFO: Session created for user: sc@gridleaf.org
```

**Existing Student:**
```
INFO: Student sc@gridleaf.org exists, updating login info
INFO: Updated login info for sc@gridleaf.org
INFO: Session created for user: sc@gridleaf.org
```

**Error (non-blocking):**
```
ERROR: Error syncing student to backend: [error details]
WARNING: Failed to sync student, but continuing with session creation
```

## Error Handling

The sync is **non-blocking**:
- If the sync fails, the user can still log in
- Error is logged but doesn't prevent session creation
- This ensures Brightspace users aren't blocked if the backend API is temporarily down

## Student Data Mapping

| LTI Field | Database Field | Notes |
|-----------|---------------|-------|
| `name` | `name` | Full name from Brightspace |
| `email` | `email` | Primary key for matching |
| `picture` | `profile_picture` | Avatar URL if available |
| - | `date_of_birth` | Set to null |
| - | `location` | Set to null |
| - | `number_of_logins` | Auto-incremented on each login |
| - | `last_login` | Auto-updated on each login |

## Default Course Enrollment

**Hardcoded in alignbackendapis:**
```python
# From app/crud/students.py line 36
await enroll_students_in_course(conn, 2, [email])
```

All new students are automatically enrolled in **Course ID 2**.

To change this, edit:
`/Users/sayon/Documents/Codes/Backend/alignbackendapis/app/crud/students.py`

## Troubleshooting

### Student Not Created
1. Check backend API is running: `curl http://localhost:8080/health`
2. Check logs: `tail -100 logs/backend.log`
3. Verify API endpoint: `curl http://localhost:8080/api/v1/students/`

### Login Info Not Updating
Check the PUT endpoint works:
```bash
curl -X PUT http://localhost:8080/api/v1/students/YOUR_EMAIL/login
```

### Student Created But No Courses
Check enrollments:
```bash
curl http://localhost:8080/api/v1/students/YOUR_EMAIL/courses
```

If empty, manually enroll:
```bash
curl -X POST http://localhost:8080/api/v1/enroll-in-course/2/enroll/ \
  -H "Content-Type: application/json" \
  -d '["YOUR_EMAIL"]'
```

## Future Enhancements

Potential improvements:
- [ ] Make default course ID configurable via environment variable
- [ ] Sync more user data (roles, course context)
- [ ] Batch sync for efficiency
- [ ] Retry logic for failed syncs
- [ ] Webhook to notify alignbackendapis of new users
