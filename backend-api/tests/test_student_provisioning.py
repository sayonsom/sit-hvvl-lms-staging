"""Regressions for the UAT incident where a launched student saw no courses.

Root causes covered here:
  * addresses were stored/queried case-sensitively while RBAC compared them
    case-insensitively, so a launch could pass authorization then 404;
  * enrolment only ever happened inside student creation, so a student who
    already existed without one could never be repaired.
"""
import unittest

from app.crud.students import (
    DEFAULT_COURSE_ID,
    _ensure_enrollment,
    get_courses_for_student,
    get_student_id_by_email,
    normalize_email,
    provision_student,
)

MIXED_CASE = "  A88272@SingaporeTech.EDU.sg  "
NORMALIZED = "a88272@singaporetech.edu.sg"


class FakeTransaction:
    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


class FakeConnection:
    """Dispatches by query text so each call can be asserted on."""

    def __init__(self, course_exists=True, existing_student=None, enrollment_written=True):
        self.course_exists = course_exists
        self.existing_student = existing_student
        self.enrollment_written = enrollment_written
        self.calls = []

    def transaction(self):
        self.calls.append(("BEGIN", ()))
        return FakeTransaction()

    async def fetchval(self, query, *args):
        self.calls.append((query, args))
        if "FROM courses" in query:
            return 1 if self.course_exists else None
        if "SELECT student_id FROM students" in query:
            return self.existing_student["student_id"] if self.existing_student else None
        return None

    async def fetchrow(self, query, *args):
        self.calls.append((query, args))
        if "SELECT * FROM students" in query:
            return self.existing_student
        if "INSERT INTO students" in query:
            return {"student_id": 77, "email": args[1], "name": args[0]}
        return None

    async def fetch(self, query, *args):
        self.calls.append((query, args))
        return []

    async def execute(self, query, *args):
        self.calls.append((query, args))
        if "INSERT INTO enrollments" in query:
            return "INSERT 0 1" if self.enrollment_written else "INSERT 0 0"
        return "OK"

    def args_for(self, needle):
        return next(args for query, args in self.calls if needle in query)


class EmailNormalizationTests(unittest.IsolatedAsyncioTestCase):
    def test_normalize_email_trims_and_lowercases(self):
        self.assertEqual(normalize_email(MIXED_CASE), NORMALIZED)

    def test_normalize_email_rejects_blank(self):
        for value in (None, "", "   ", 42):
            self.assertIsNone(normalize_email(value))

    async def test_student_id_lookup_is_case_insensitive(self):
        conn = FakeConnection(existing_student={"student_id": 12})
        self.assertEqual(await get_student_id_by_email(conn, MIXED_CASE), 12)
        query, args = conn.calls[0]
        self.assertIn("lower(btrim(email)) = $1", query)
        self.assertEqual(args, (NORMALIZED,))

    async def test_course_lookup_is_case_insensitive(self):
        conn = FakeConnection()
        await get_courses_for_student(conn, MIXED_CASE)
        query, args = conn.calls[0]
        self.assertIn("lower(btrim(email)) = $1", query)
        self.assertEqual(args, (NORMALIZED,))


class ProvisioningTests(unittest.IsolatedAsyncioTestCase):
    async def test_new_student_is_created_and_enrolled(self):
        conn = FakeConnection(existing_student=None)
        result = await provision_student(conn, "A88272 Name .", MIXED_CASE)
        self.assertTrue(result["created"])
        self.assertTrue(result["enrolled"])
        self.assertEqual(result["course_id"], DEFAULT_COURSE_ID)
        # The address is stored normalized, not as Brightspace sent it.
        self.assertEqual(conn.args_for("INSERT INTO students")[1], NORMALIZED)

    async def test_existing_student_missing_enrollment_is_repaired(self):
        """The returning-student path previously only bumped the login counter."""
        conn = FakeConnection(existing_student={"student_id": 31}, enrollment_written=True)
        result = await provision_student(conn, "A88272 Name .", MIXED_CASE)
        self.assertFalse(result["created"])
        self.assertTrue(result["enrolled"])
        self.assertEqual(result["student_id"], 31)
        self.assertEqual(conn.args_for("INSERT INTO enrollments")[:2], (31, DEFAULT_COURSE_ID))

    async def test_already_enrolled_student_is_a_no_op(self):
        conn = FakeConnection(existing_student={"student_id": 31}, enrollment_written=False)
        result = await provision_student(conn, "A88272 Name .", MIXED_CASE)
        self.assertFalse(result["created"])
        self.assertFalse(result["enrolled"])

    async def test_enrollment_insert_is_guarded_against_duplicates(self):
        conn = FakeConnection()
        await _ensure_enrollment(conn, 5, 2)
        query, _ = conn.calls[0]
        self.assertIn("WHERE NOT EXISTS", query)

    async def test_unknown_course_is_rejected(self):
        conn = FakeConnection(course_exists=False)
        with self.assertRaises(LookupError):
            await provision_student(conn, "A88272 Name .", MIXED_CASE, course_id=999)

    async def test_blank_email_is_rejected(self):
        with self.assertRaises(ValueError):
            await provision_student(FakeConnection(), "A88272 Name .", "   ")

    async def test_provisioning_runs_in_a_transaction(self):
        conn = FakeConnection(existing_student=None)
        await provision_student(conn, "A88272 Name .", MIXED_CASE)
        self.assertEqual(conn.calls[0][0], "BEGIN")


if __name__ == "__main__":
    unittest.main()
