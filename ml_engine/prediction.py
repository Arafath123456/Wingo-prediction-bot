import numpy as np
import pandas as pd
import joblib
from tensorflow.keras.models import load_model
from .feature_engineering import create_features
from .constants import COLOR_MAPPING, SIZE_MAPPING, MODEL_CONFIG
from loguru import logger

MODELS_DIR = "ml_engine/models"

class WinGoPredictor:
    def __init__(self):
        self.color_models = {}
        self.size_models = {}
        self.load_models()
        
    def load_models(self):
        """Load all trained models"""
        try:
            # Color prediction models
            self.color_models['lstm'] = load_model(f"{MODELS_DIR}/lstm_color.keras")
            self.color_models['xgboost'] = joblib.load(f"{MODELS_DIR}/xgboost_color.pkl")
            self.color_models['lightgbm'] = joblib.load(f"{MODELS_DIR}/lightgbm_color.pkl")
            self.color_models['randomforest'] = joblib.load(f"{MODELS_DIR}/randomforest_color.pkl")
            
            # Size prediction models
            self.size_models['lstm'] = load_model(f"{MODELS_DIR}/lstm_size.keras")
            self.size_models['xgboost'] = joblib.load(f"{MODELS_DIR}/xgboost_size.pkl")
            self.size_models['lightgbm'] = joblib.load(f"{MODELS_DIR}/lightgbm_size.pkl")
            self.size_models['randomforest'] = joblib.load(f"{MODELS_DIR}/randomforest_size.pkl")
            
            logger.info("All prediction models loaded successfully")
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            raise RuntimeError("Prediction models not available") from e

    def predict_next(self, historical_data: pd.DataFrame) -> dict:
        """Predict next game outcome"""
        df = create_features(historical_data)
        latest = df.iloc[-MODEL_CONFIG["sequence_length"]:]
        
        # Prepare features for prediction
        lstm_features = latest.drop(
            columns=['issue_number', 'draw_time', 'color', 'size'], 
            errors='ignore'
        ).values.reshape(1, MODEL_CONFIG["sequence_length"], -1)
        
        tabular_features = latest.drop(
            columns=['issue_number', 'draw_time', 'color', 'size'], 
            errors='ignore'
        ).iloc[-1].values.reshape(1, -1)
        
        # Make predictions
        color_preds = {}
        size_preds = {}
        
        # LSTM predictions
        color_preds['lstm'] = np.argmax(self.color_models['lstm'].predict(lstm_features, verbose=0))
        size_preds['lstm'] = np.round(self.size_models['lstm'].predict(lstm_features, verbose=0)).astype(int)[0][0]
        
        # Tabular model predictions
        for model_type in ['xgboost', 'lightgbm', 'randomforest']:
            color_preds[model_type] = self.color_models[model_type].predict(tabular_features)[0]
            size_preds[model_type] = self.size_models[model_type].predict(tabular_features)[0]
        
        # Ensemble predictions
        color_ensemble = max(set(list(color_preds.values())), key=list(color_preds.values()).count)
        size_ensemble = max(set(list(size_preds.values())), key=list(size_preds.values()).count)
        
        # Confidence calculation
        color_confidence = sum(1 for v in color_preds.values() if v == color_ensemble) / len(color_preds) * 100
        size_confidence = sum(1 for v in size_preds.values() if v == size_ensemble) / len(size_preds) * 100
        
        # Map to labels
        color_map = {0: 'Green', 1: 'Red', 2: 'Violet'}
        size_map = {0: 'Small', 1: 'Big'}
        
        return {
            'period_number': historical_data['issue_number'].iloc[-1],
            'next_period': str(int(historical_data['issue_number'].iloc[-1]) + 1),
            'predicted_color': color_map[color_ensemble],
            'predicted_size': size_map[size_ensemble],
            'color_confidence': round(color_confidence, 1),
            'size_confidence': round(size_confidence, 1),
            'overall_confidence': round((color_confidence + size_confidence) / 2, 1)
        }