from sqlalchemy import Column, Integer, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base

class ATSResult(Base):
    __tablename__ = "ats_results"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, unique=True)
    ats_score = Column(Integer, nullable=False)
    
    # Custom score breakdowns and explanations
    score_breakdown = Column(JSON, nullable=False)  # Weights and individual category scores
    why_explanation = Column(JSON, nullable=False)  # Explainable AI logs (modifiers: "+15 Python", "-10 Docker")
    resume_health = Column(JSON, nullable=False)    # Health statuses ("Excellent", "Improve") per section
    checklist = Column(JSON, nullable=False)        # Checklist elements boolean dictionary
    missing_skills = Column(JSON, nullable=False)    # Prioritized missing skills list
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    analysis = relationship("Analysis", back_populates="ats_result")
