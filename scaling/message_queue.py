from celery import Celery
from ml_engine.prediction import WinGoPredictor
from database.crud import get_latest_rounds
from database.session import get_session
import os
from loguru import logger

# Initialize Celery
celery = Celery(
    'wingo_tasks',
    broker=os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1")
)

@celery.task(name="generate_prediction")
def generate_prediction_task():
    """Background task for prediction generation"""
    try:
        session = get_session()
        historical_data = get_latest_rounds(session, 500)
        
        predictor = WinGoPredictor()
        prediction = predictor.predict_next(historical_data)
        
        logger.info(f"Generated prediction for {prediction['next_period']}")
        return prediction
    except Exception as e:
        logger.error(f"Prediction task failed: {str(e)}")
        raise

@celery.task(name="train_models")
def train_models_task():
    """Background task for model training"""
    try:
        session = get_session()
        historical_data = get_latest_rounds(session, 500)
        
        from ml_engine.model_training import train_all_models
        train_all_models(historical_data)
        
        logger.success("Models trained successfully")
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Model training failed: {str(e)}")
        raise