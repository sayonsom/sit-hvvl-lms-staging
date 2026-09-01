"""
Pydantic Models for LTI Backend API
Defines request/response schemas
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional


class SessionResponse(BaseModel):
    """Response model for session validation"""
    user: Dict[str, Any]
    course: Dict[str, Any]
    api_token: Optional[str] = None


class LoginCodeExchangeRequest(BaseModel):
    """One-time browser handoff code from a completed LTI launch."""
    login_code: str = Field(min_length=32, max_length=256)


class LoginCodeExchangeResponse(SessionResponse):
    """Session material returned after consuming a one-time login code."""
    session_token: str


class LogoutRequest(BaseModel):
    """Request model for logout (can be empty)"""
    pass


class UserInfo(BaseModel):
    """User information model"""
    user_id: str
    name: str
    given_name: str
    family_name: str
    email: str
    picture: Optional[str] = ""
    roles: List[str]
    sub: str


class CourseInfo(BaseModel):
    """Course information model"""
    course_id: str
    course_code: str
    course_title: str
    course_section: str
    course_offering_sourcedid: Optional[str] = ""
    context_type: List[str] = []


class StaffCodeExchangeRequest(BaseModel):
    """Request model for staff code exchange"""
    code: str
    state: str


class StaffCodeExchangeResponse(BaseModel):
    """Response model for staff code exchange"""
    user: Dict[str, Any]
    claims: Dict[str, Any]
    api_token: Optional[str] = None
