from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    jd_id = Column(Integer, ForeignKey("job_descriptions.id", ondelete="SET NULL"), nullable=True)
    
    # AI generated text content
    summary = Column(Text, nullable=True)
    suggestions = Column(JSON, nullable=True)     # Detailed suggestions list
    roadmap = Column(JSON, nullable=True)         # Custom structured roadmap
    career_fit = Column(JSON, nullable=True)      # Recommended vs Non-recommended roles
    cover_letter = Column(Text, nullable=True)     # Generated cover letter
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    resume = relationship("Resume", back_populates="analyses")
    jd = relationship("JobDescription", back_populates="analyses")
    
    # One-to-one relationship with ATSResult
    ats_result = relationship("ATSResult", uselist=False, back_populates="analysis", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="analysis", cascade="all, delete-orphan")
