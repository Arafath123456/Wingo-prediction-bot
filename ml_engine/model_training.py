import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from .feature_engineering import create_features, prepare_sequences
from .constants import MODEL_CONFIG
import joblib
import os
from loguru import logger

MODELS_DIR = "ml_engine/models"

def train_lstm_model(X: np.ndarray, y: np.ndarray, n_features: int) -> Sequential:
    """Train LSTM model for time series prediction"""
    model = Sequential([
        LSTM(128, input_shape=(MODEL_CONFIG["sequence_length"], n_features), 
        Dropout(0.3),
        Dense(64, activation='relu'),
        Dense(3 if len(np.unique(y)) > 2 else 1, activation='softmax' if len(np.unique(y)) > 2 else 'sigmoid')
    ])
    
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy' if len(np.unique(y)) > 2 else 'binary_crossentropy',
        metrics=['accuracy']
    )
    
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, 
        test_size=MODEL_CONFIG["validation_split"],
        shuffle=False
    )
    
    model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=50,
        batch_size=32,
        verbose=0
    )
    
    return model

def train_tabular_model(X: np.ndarray, y: np.ndarray, model_type: str):
    """Train tabular model (XGBoost, LightGBM, or RandomForest)"""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=MODEL_CONFIG["test_size"],
        shuffle=False
    )
    
    if model_type == 'xgboost':
        model = XGBClassifier(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.1,
            subsample=0.8,
            use_label_encoder=False,
            eval_metric='logloss'
        )
    elif model_type == 'lightgbm':
        model = LGBMClassifier(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.1,
            subsample=0.8
        )
    else:  # randomforest
        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=5
        )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    logger.info(f"{model_type} accuracy: {accuracy:.2f}")
    
    return model

def train_all_models(data: pd.DataFrame):
    """Train all models for color and size prediction"""
    os.makedirs(MODELS_DIR, exist_ok=True)
    df = create_features(data)
    
    # Color prediction models
    X_color, y_color, n_features = prepare_sequences(df, 'color_encoded')
    lstm_color = train_lstm_model(X_color, y_color, n_features)
    lstm_color.save(f"{MODELS_DIR}/lstm_color.keras")
    
    tabular_color = df.drop(columns=['issue_number', 'draw_time', 'color', 'size'])
    y_color_tab = tabular_color.pop('color_encoded')
    
    for model_type in ['xgboost', 'lightgbm', 'randomforest']:
        model = train_tabular_model(tabular_color.values, y_color_tab.values, model_type)
        joblib.dump(model, f"{MODELS_DIR}/{model_type}_color.pkl")
    
    # Size prediction models
    X_size, y_size, n_features = prepare_sequences(df, 'size_encoded')
    lstm_size = train_lstm_model(X_size, y_size, n_features)
    lstm_size.save(f"{MODELS_DIR}/lstm_size.keras")
    
    tabular_size = df.drop(columns=['issue_number', 'draw_time', 'color', 'size'])
    y_size_tab = tabular_size.pop('size_encoded')
    
    for model_type in ['xgboost', 'lightgbm', 'randomforest']:
        model = train_tabular_model(tabular_size.values, y_size_tab.values, model_type)
        joblib.dump(model, f"{MODELS_DIR}/{model_type}_size.pkl")
    
    logger.success("All models trained and saved")