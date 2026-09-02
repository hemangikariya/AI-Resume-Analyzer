from pydantic import BaseModel, EmailStr, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

# ==========================================
# UNIFIED BASE RESPONSE SCHEMAS
# ==========================================
class ErrorDetail(BaseModel):
    code: str
    message: str

class APIResponse(BaseModel):
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[Dict[str, Any]] = None

class APIErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail

# ==========================================
# AUTH SCHEMAS
# ==========================================
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True

# ==========================================
# RESUME & JD SCHEMAS
# ==========================================
class ResumeResponse(BaseModel):
    id: int
    filename: str
    version: int
    created_at: datetime
    parsed_data: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class JDCreate(BaseModel):
    title: str = Field(..., min_length=1)
    jd_text: str = Field(..., min_length=10)

class JDResponse(BaseModel):
    id: int
    title: str
    jd_text: str
    extracted_skills: Optional[List[str]] = None
    created_at: datetime

    class Config:
        from_attributes = True

# ==========================================
# ATS RESULT SCHEMAS
# ==========================================
class ATSResultResponse(BaseModel):
    ats_score: int
    score_breakdown: Dict[str, int]
    why_explanation: List[Dict[str, Any]]
    resume_health: Dict[str, str]
    checklist: Dict[str, bool]
    missing_skills: List[Dict[str, Any]]

    class Config:
        from_attributes = True

# ==========================================
# ANALYSIS SCHEMAS
# ==========================================
class AnalysisResponse(BaseModel):
    id: int
    resume_id: int
    jd_id: Optional[int] = None
    summary: Optional[str] = None
    suggestions: Optional[List[str]] = None
    roadmap: Optional[List[Dict[str, Any]]] = None
    career_fit: Optional[Dict[str, Any]] = None
    cover_letter: Optional[str] = None
    created_at: datetime
    ats_result: Optional[ATSResultResponse] = None

    class Config:
        from_attributes = True

class ResumeCompareRequest(BaseModel):
    resume_id_1: int
    resume_id_2: int
    jd_id: Optional[int] = None

# ==========================================
# CHAT SCHEMAS
# ==========================================
class ChatRequest(BaseModel):
    resume_id: int
    message: str
    history: List[Dict[str, str]] = []  # [{"role": "user"/"assistant", "content": "..."}]

class ChatResponse(BaseModel):
    reply: str

# ==========================================
# INTERVIEW SCHEMAS
# ==========================================
class InterviewStartRequest(BaseModel):
    resume_id: int
    jd_id: Optional[int] = None
    difficulty: str = "medium"  # easy, medium, hard

class InterviewStartResponse(BaseModel):
    session_id: str
    question: str
    category: str  # HR, Technical, Project, Coding

class InterviewEvaluateRequest(BaseModel):
    session_id: str
    resume_id: int
    jd_id: Optional[int] = None
    question: str
    answer: str
    question_index: int
    difficulty: str
    history: List[Dict[str, Any]] = []  # previous evaluations

class InterviewEvaluateResponse(BaseModel):
    score: int  # out of 10
    feedback: str
    strengths: str
    weaknesses: str
    next_question: Optional[str] = None
    next_category: Optional[str] = None  # HR, Technical, Project, Coding
    is_complete: bool = False

# ==========================================
# REWRITE & PROJECT SCHEMAS
# ==========================================
class RewriteRequest(BaseModel):
    text: str

class RewriteResponse(BaseModel):
    original_text: str
    rewritten_text: str

class ProjectEnhanceRequest(BaseModel):
    title: str
    description: str

class ProjectEnhanceResponse(BaseModel):
    title: str
    description: str
    technologies: List[str]
    impact: str
    bullets: List[str]
