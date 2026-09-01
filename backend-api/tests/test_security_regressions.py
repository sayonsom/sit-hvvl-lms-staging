import ast
import time
import unittest
from pathlib import Path

import jwt
from fastapi import HTTPException

from app.core import auth
from app.core.auth import AuthenticatedActor
from app.core.config_validation import readiness_configuration_errors
from app.core.rbac import (
    is_student_enrolled,
    require_course_staff_access,
    require_student_email_access,
)


class FakeConnection:
    def __init__(self, fetchrow_result=None):
        self.fetchrow_result = fetchrow_result
        self.calls = []

    async def fetchrow(self, query, *args):
        self.calls.append((query, args))
        return self.fetchrow_result


class RBACRegressionTests(unittest.IsolatedAsyncioTestCase):
    async def test_student_cannot_read_another_student_by_email(self):
        actor = AuthenticatedActor(
            subject="student-a",
            email="student-a@example.edu",
            roles={"student"},
            auth_method="lti",
        )
        with self.assertRaises(HTTPException) as context:
            await require_student_email_access(FakeConnection(), actor, "student-b@example.edu")
        self.assertEqual(context.exception.status_code, 403)

    async def test_student_course_access_uses_parameterized_enrollment_query(self):
        actor = AuthenticatedActor(
            subject="student-a",
            email="student-a@example.edu",
            roles={"student"},
            auth_method="lti",
        )
        conn = FakeConnection(fetchrow_result={"exists": 1})
        self.assertTrue(await is_student_enrolled(conn, actor, 42))
        query, args = conn.calls[0]
        self.assertIn("lower($1)", query)
        self.assertIn("e.course_id = $2", query)
        self.assertEqual(args, ("student-a@example.edu", 42))

    async def test_teacher_cannot_administer_unassigned_course(self):
        actor = AuthenticatedActor(
            subject="teacher-a",
            email="teacher-a@example.edu",
            roles={"teacher"},
            auth_method="staff",
        )
        conn = FakeConnection(fetchrow_result=None)
        with self.assertRaises(HTTPException) as context:
            await require_course_staff_access(conn, actor, 99)
        self.assertEqual(context.exception.status_code, 403)
        query, args = conn.calls[0]
        self.assertIn("c.course_id = $1", query)
        self.assertIn("lower(i.email) = lower($2)", query)
        self.assertEqual(args, (99, "teacher-a@example.edu"))

    async def test_teacher_can_read_results_for_token_scoped_course(self):
        actor = AuthenticatedActor(
            subject="teacher-a",
            email="teacher-a@example.edu",
            roles={"teacher"},
            auth_method="staff",
            course_ids={"2"},
        )
        conn = FakeConnection(fetchrow_result=None)
        await require_course_staff_access(conn, actor, 2)
        self.assertEqual(conn.calls, [])


class JWTRegressionTests(unittest.IsolatedAsyncioTestCase):
    async def test_tampered_backend_token_is_rejected(self):
        original_secret = auth.BACKEND_API_JWT_SECRET
        original_audience = auth.BACKEND_API_JWT_AUDIENCE
        auth.BACKEND_API_JWT_SECRET = "test-secret-with-sufficient-entropy"
        auth.BACKEND_API_JWT_AUDIENCE = "hvvl-test"
        try:
            token = jwt.encode(
                {
                    "sub": "student-a",
                    "email": "student-a@example.edu",
                    "roles": ["student"],
                    "auth_method": "lti",
                    "aud": "hvvl-test",
                    "iat": int(time.time()),
                    "exp": int(time.time()) + 300,
                },
                "different-secret-with-at-least-32-bytes",
                algorithm="HS256",
            )
            with self.assertRaises(HTTPException) as context:
                await auth.get_authenticated_actor(authorization=f"Bearer {token}")
            self.assertEqual(context.exception.status_code, 401)
        finally:
            auth.BACKEND_API_JWT_SECRET = original_secret
            auth.BACKEND_API_JWT_AUDIENCE = original_audience


class SQLInjectionRegressionTests(unittest.TestCase):
    DB_METHODS = {"execute", "executemany", "fetch", "fetchrow", "fetchval"}

    @staticmethod
    def _is_dynamic_string(node):
        return (
            isinstance(node, ast.JoinedStr)
            or isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Mod))
            or isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "format"
        )

    def test_database_calls_do_not_use_interpolated_sql(self):
        app_root = Path(__file__).resolve().parents[1] / "app"
        violations = []

        for source_path in app_root.rglob("*.py"):
            tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
            dynamic_names = {
                target.id
                for node in ast.walk(tree)
                if isinstance(node, ast.Assign) and self._is_dynamic_string(node.value)
                for target in node.targets
                if isinstance(target, ast.Name)
            }
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                    continue
                if node.func.attr not in self.DB_METHODS or not node.args:
                    continue
                query = node.args[0]
                if self._is_dynamic_string(query) or isinstance(query, ast.Name) and query.id in dynamic_names:
                    violations.append(f"{source_path.relative_to(app_root)}:{node.lineno}")

        self.assertEqual(violations, [], f"Interpolated SQL reaches database calls: {violations}")


class ReadinessConfigurationTests(unittest.TestCase):
    def test_rejects_placeholder_and_reused_security_values(self):
        values = {
            "DB_PASSWORD": "<strong-password>",
            "API_SERVICE_TOKEN": "a" * 40,
            "BACKEND_API_JWT_SECRET": "a" * 40,
            "BACKEND_API_JWT_AUDIENCE": "hvvl-backend-api",
            "LOCAL_STORAGE_SIGNING_KEY": "b" * 40,
        }
        errors = readiness_configuration_errors(values)
        self.assertIn("database_password", errors)
        self.assertIn("independent_signing_secrets", errors)

    def test_accepts_independent_strong_security_values(self):
        values = {
            "DB_PASSWORD": "db-password-with-24-chars",
            "API_SERVICE_TOKEN": "s" * 40,
            "BACKEND_API_JWT_SECRET": "j" * 40,
            "BACKEND_API_JWT_AUDIENCE": "hvvl-backend-api",
            "LOCAL_STORAGE_SIGNING_KEY": "l" * 40,
        }
        self.assertEqual(readiness_configuration_errors(values), [])


if __name__ == "__main__":
    unittest.main()
