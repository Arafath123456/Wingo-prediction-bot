from sqlalchemy.orm import Session
from data_ingestion.models import WingoRound
from ml_engine.prediction import WinGoPredictor
import pandas as pd
from loguru import logger
from sqlalchemy import func, case
from prediction_logger import PredictionLog
from datetime import datetime, timedelta

def get_latest_rounds(session: Session, limit: int = 500) -> pd.DataFrame:
    """Retrieve latest rounds as DataFrame"""
    results = session.query(
        WingoRound.issue_number,
        WingoRound.winning_number,
        WingoRound.draw_time
    ).order_by(WingoRound.draw_time.desc()).limit(limit).all()
    
    return pd.DataFrame(results, columns=['issue_number', 'winning_number', 'draw_time'])

def get_prediction_history(session: Session, limit: int = 10):
    """Get recent prediction history"""
    # This will be implemented after adding prediction logging
    return []

def get_performance_stats(session: Session):
    """Calculate performance statistics"""
    # This will be implemented after adding prediction logging
    return {}

def get_prediction_history(session: Session, limit: int = 10):
    """Get recent prediction history"""
    return session.query(PredictionLog).order_by(
        PredictionLog.timestamp.desc()
    ).limit(limit).all()

def get_performance_stats(session: Session):
    """Calculate performance statistics"""
    # Overall stats
    total_query = session.query(func.count(PredictionLog.id))
    correct_query = session.query(func.count(PredictionLog.id)).filter(
        PredictionLog.is_correct_overall == True
    )
    color_correct = session.query(func.count(PredictionLog.id)).filter(
        PredictionLog.is_correct_color == True
    )
    size_correct = session.query(func.count(PredictionLog.id)).filter(
        PredictionLog.is_correct_size == True
    )
    
    # Recent stats (last 50)
    recent_query = session.query(PredictionLog).order_by(
        PredictionLog.timestamp.desc()
    ).limit(50).subquery()
    
    recent_correct = session.query(func.count()).select_from(recent_query).filter(
        recent_query.c.is_correct_overall == True
    ).scalar()
    
    # Last prediction time
    last_prediction = session.query(
        func.max(PredictionLog.timestamp)
    ).scalar()
    
    # Execute all queries
    total_predictions = total_query.scalar() or 0
    correct_predictions = correct_query.scalar() or 0
    color_correct_count = color_correct.scalar() or 0
    size_correct_count = size_correct.scalar() or 0
    recent_accuracy = (recent_correct / 50 * 100) if total_predictions >= 50 else 0
    
    return {
        'total_predictions': total_predictions,
        'correct_predictions': correct_predictions,
        'color_correct': color_correct_count,
        'size_correct': size_correct_count,
        'overall_accuracy': (correct_predictions / total_predictions * 100) if total_predictions else 0,
        'color_accuracy': (color_correct_count / total_predictions * 100) if total_predictions else 0,
        'size_accuracy': (size_correct_count / total_predictions * 100) if total_predictions else 0,
        'recent_accuracy': recent_accuracy,
        'last_prediction': last_prediction.strftime("%Y-%m-%d %H:%M UTC") if last_prediction else "Never"
    }