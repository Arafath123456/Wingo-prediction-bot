import numpy as np
import pandas as pd
from tqdm import tqdm
from .prediction import WinGoPredictor
from .constants import MODEL_CONFIG
from loguru import logger

class Backtester:
    def __init__(self, historical_data: pd.DataFrame):
        self.data = historical_data
        self.predictor = WinGoPredictor()
        self.window_size = 100
        self.step_size = 30
        
    def run_backtest(self) -> dict:
        """Run full backtest on historical data"""
        results = []
        total_rounds = len(self.data)
        
        for i in tqdm(range(self.window_size, total_rounds, self.step_size)):
            train_data = self.data.iloc[:i]
            test_data = self.data.iloc[i:i+self.step_size]
            
            # Train models on current window
            # In practice, we'd retrain here, but for demo we'll use existing
            try:
                prediction = self.predictor.predict_next(train_data)
                
                for j, row in test_data.iterrows():
                    actual_color = COLOR_MAPPING[row['winning_number']]
                    actual_size = SIZE_MAPPING[row['winning_number']]
                    
                    result = {
                        'period': row['issue_number'],
                        'predicted_color': prediction['predicted_color'],
                        'actual_color': actual_color,
                        'color_correct': int(prediction['predicted_color'] == actual_color),
                        'predicted_size': prediction['predicted_size'],
                        'actual_size': actual_size,
                        'size_correct': int(prediction['predicted_size'] == actual_size),
                        'overall_correct': int(
                            (prediction['predicted_color'] == actual_color) and 
                            (prediction['predicted_size'] == actual_size)
                        ),
                        'confidence': prediction['overall_confidence']
                    }
                    results.append(result)
            except Exception as e:
                logger.error(f"Backtesting error at period {row['issue_number']}: {str(e)}")
        
        return pd.DataFrame(results)
    
    def calculate_metrics(self, results: pd.DataFrame) -> dict:
        """Calculate performance metrics from backtest results"""
        return {
            'color_accuracy': results['color_correct'].mean(),
            'size_accuracy': results['size_correct'].mean(),
            'overall_accuracy': results['overall_correct'].mean(),
            'total_rounds': len(results),
            'win_rate': results['overall_correct'].mean(),
            'avg_confidence': results['confidence'].mean(),
            'confidence_accuracy_corr': results[['confidence', 'overall_correct']].corr().iloc[0,1]
        }