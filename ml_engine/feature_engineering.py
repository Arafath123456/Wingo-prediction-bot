import numpy as np
import pandas as pd
from .constants import COLOR_MAPPING, SIZE_MAPPING, MODEL_CONFIG

def create_features(data: pd.DataFrame) -> pd.DataFrame:
    """Generate features from historical game data"""
    df = data.copy()
    
    # Basic features
    df['color'] = df['winning_number'].map(COLOR_MAPPING)
    df['size'] = df['winning_number'].map(SIZE_MAPPING)
    
    # Encoding
    df['color_encoded'] = df['color'].map({'Green': 0, 'Red': 1, 'Violet': 2})
    df['size_encoded'] = df['size'].map({'Small': 0, 'Big': 1})
    
    # Lag features
    for lag in range(1, MODEL_CONFIG["n_lags"] + 1):
        df[f'lag_{lag}'] = df['winning_number'].shift(lag)
    
    # Rolling statistics
    for window in MODEL_CONFIG["rolling_windows"]:
        df[f'rolling_mean_{window}'] = df['winning_number'].rolling(window).mean()
        df[f'rolling_std_{window}'] = df['winning_number'].rolling(window).std()
        df[f'color_ratio_red_{window}'] = df['color'].rolling(window).apply(lambda x: (x == 'Red').mean())
        df[f'color_ratio_green_{window}'] = df['color'].rolling(window).apply(lambda x: (x == 'Green').mean())
        df[f'size_ratio_big_{window}'] = df['size'].rolling(window).apply(lambda x: (x == 'Big').mean())
    
    # Streak features
    df['color_streak'] = df['color'].ne(df['color'].shift()).cumsum()
    df['size_streak'] = df['size'].ne(df['size'].shift()).cumsum()
    
    # Frequency features
    df['prev_color'] = df['color'].shift(1)
    df['prev_size'] = df['size'].shift(1)
    
    # Time-based features
    df['draw_time'] = pd.to_datetime(df['draw_time'])
    df['hour'] = df['draw_time'].dt.hour
    df['minute'] = df['draw_time'].dt.minute
    df['day_part'] = (df['hour'] % 24) // 6
    
    # Drop initial null rows
    df = df.dropna()
    
    return df

def prepare_sequences(df: pd.DataFrame, target: str) -> tuple:
    """Prepare LSTM sequences"""
    from tensorflow.keras.preprocessing.sequence import TimeseriesGenerator
    
    features = df.drop(columns=[target, 'issue_number', 'draw_time', 'color', 'size'], errors='ignore')
    target_col = df[target]
    
    n_features = len(features.columns)
    seq_length = MODEL_CONFIG["sequence_length"]
    
    generator = TimeseriesGenerator(
        features.values,
        target_col.values,
        length=seq_length,
        batch_size=len(features) - seq_length
    )
    
    X, y = generator[0]
    return X, y, n_features