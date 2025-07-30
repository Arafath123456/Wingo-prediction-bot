from sqlalchemy.orm import Session
from sqlalchemy import Column, String, Integer, Float, TIMESTAMP
from datetime import datetime, timezone
from database.session import Base
import pandas as pd

class PredictionLog(Base):
    __tablename__ = 'prediction_logs'
    
    id = Column(Integer, primary_key=True)
    issue_number = Column(String(20), nullable=False)
    predicted_color = Column(String(10), nullable=False)
    predicted_size = Column(String(5), nullable=False)
    confidence = Column(Float, nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    actual_number = Column(Integer)
    actual_color = Column(String(10))
    actual_size = Column(String(5))
    is_correct_color = Column(Boolean)
    is_correct_size = Column(Boolean)
    is_correct_overall = Column(Boolean)

def log_prediction(session: Session, prediction: dict):
    """Log a prediction to the database"""
    log_entry = PredictionLog(
        issue_number=prediction['next_period'],
        predicted_color=prediction['predicted_color'],
        predicted_size=prediction['predicted_size'],
        confidence=prediction['overall_confidence']
    )
    session.add(log_entry)
    session.commit()
    return log_entry

def update_prediction_with_result(session: Session, issue_number: str, winning_number: int):
    """Update prediction log with actual result"""
    from ml_engine.constants import COLOR_MAPPING, SIZE_MAPPING
    
    log_entry = session.query(PredictionLog).filter_by(
        issue_number=issue_number,
        actual_number=None
    ).first()
    
    if log_entry:
        actual_color = COLOR_MAPPING[winning_number]
        actual_size = SIZE_MAPPING[winning_number]
        
        log_entry.actual_number = winning_number
        log_entry.actual_color = actual_color
        log_entry.actual_size = actual_size
        log_entry.is_correct_color = (log_entry.predicted_color == actual_color)
        log_entry.is_correct_size = (log_entry.predicted_size == actual_size)
        log_entry.is_correct_overall = (
            log_entry.is_correct_color and log_entry.is_correct_size
        )
        
        session.commit()
        return log_entry
    return None