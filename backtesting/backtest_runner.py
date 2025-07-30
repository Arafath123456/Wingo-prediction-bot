import pandas as pd
from tqdm import tqdm
from datetime import datetime
from ml_engine.prediction import WinGoPredictor
from database.crud import get_latest_rounds
from database.session import get_session
from monitoring.metrics import track_performance
from .performance_report import generate_performance_report
import joblib
import os
from loguru import logger

class BacktestRunner:
    def __init__(self, window_size=500, step_size=30):
        self.window_size = window_size
        self.step_size = step_size
        self.predictor = WinGoPredictor()
        self.results = []
    
    def run_backtest(self):
        session = get_session()
        all_data = get_latest_rounds(session, 10000)
        
        if len(all_data) < self.window_size + self.step_size:
            logger.warning("Insufficient data for backtesting")
            return None
        
        for i in tqdm(range(self.window_size, len(all_data), self.step_size)):
            train_data = all_data.iloc[:i]
            test_data = all_data.iloc[i:i+self.step_size]
            
            # Update models with latest data (simulate real-time retraining)
            self.predictor.load_models()
            
            # Test on next step_size periods
            for j in range(len(test_data)):
                current_data = train_data.iloc[-self.window_size:]
                next_row = test_data.iloc[j]
                
                try:
                    prediction = self.predictor.predict_next(current_data)
                    
                    actual_color = next_row['color']
                    actual_size = next_row['size']
                    
                    result = {
                        'period': next_row['issue_number'],
                        'timestamp': datetime.now(),
                        'predicted_color': prediction['predicted_color'],
                        'actual_color': actual_color,
                        'color_correct': prediction['predicted_color'] == actual_color,
                        'predicted_size': prediction['predicted_size'],
                        'actual_size': actual_size,
                        'size_correct': prediction['predicted_size'] == actual_size,
                        'overall_correct': (prediction['predicted_color'] == actual_color) and 
                                          (prediction['predicted_size'] == actual_size),
                        'confidence': prediction['overall_confidence'],
                        'models_used': list(self.predictor.color_models.keys()) + 
                                      list(self.predictor.size_models.keys())
                    }
                    self.results.append(result)
                    
                    # Add to training data for next prediction
                    train_data = pd.concat([train_data, test_data.iloc[[j]]])
                except Exception as e:
                    logger.error(f"Backtest failed at period {next_row['issue_number']}: {str(e)}")
        
        return pd.DataFrame(self.results)
    
    def save_results(self, results_df):
        os.makedirs("backtesting/results", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backtesting/results/backtest_{timestamp}.pkl"
        joblib.dump(results_df, filename)
        logger.info(f"Backtest results saved to {filename}")
        return filename
    
    def run_and_report(self):
        results_df = self.run_backtest()
        if results_df is not None:
            self.save_results(results_df)
            report = generate_performance_report(results_df)
            
            # Track model performance
            for model in set(results_df['models_used'].explode()):
                model_results = results_df[results_df['models_used'].apply(lambda x: model in x)]
                if not model_results.empty:
                    color_acc = model_results['color_correct'].mean()
                    size_acc = model_results['size_correct'].mean()
                    track_performance(model, 'color', color_acc)
                    track_performance(model, 'size', size_acc)
            
            return report
        return None