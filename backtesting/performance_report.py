import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from loguru import logger

def generate_performance_report(results_df: pd.DataFrame) -> dict:
    """Generate comprehensive performance report"""
    report = {}
    
    # Basic metrics
    report['total_predictions'] = len(results_df)
    report['color_accuracy'] = results_df['color_correct'].mean()
    report['size_accuracy'] = results_df['size_correct'].mean()
    report['overall_accuracy'] = results_df['overall_correct'].mean()
    report['avg_confidence'] = results_df['confidence'].mean()
    
    # Confidence analysis
    results_df['confidence_bucket'] = pd.cut(
        results_df['confidence'], 
        bins=[0, 50, 60, 70, 80, 90, 100],
        labels=['<50', '50-60', '60-70', '70-80', '80-90', '90-100']
    )
    confidence_accuracy = results_df.groupby('confidence_bucket')['overall_correct'].mean()
    report['confidence_accuracy'] = confidence_accuracy.to_dict()
    
    # Generate plots
    report['plots'] = {}
    report['plots']['accuracy_trend'] = plot_accuracy_trend(results_df)
    report['plots']['confusion_matrix'] = plot_confusion_matrix(results_df)
    
    logger.success(f"Backtest report generated: {report['overall_accuracy']:.2%} accuracy")
    return report

def plot_accuracy_trend(results_df: pd.DataFrame) -> bytes:
    """Plot accuracy over time"""
    plt.figure(figsize=(12, 6))
    results_df.set_index('timestamp')['overall_correct'].rolling(50).mean().plot()
    plt.title('50-Prediction Rolling Accuracy')
    plt.ylabel('Accuracy')
    plt.xlabel('Time')
    plt.grid(True)
    
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return buf.getvalue()

def plot_confusion_matrix(results_df: pd.DataFrame) -> bytes:
    """Plot color confusion matrix"""
    from sklearn.metrics import confusion_matrix
    import seaborn as sns
    
    cm = confusion_matrix(
        results_df['actual_color'],
        results_df['predicted_color'],
        labels=['Green', 'Red', 'Violet']
    )
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Green', 'Red', 'Violet'],
                yticklabels=['Green', 'Red', 'Violet'])
    plt.title('Color Prediction Confusion Matrix')
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return buf.getvalue()