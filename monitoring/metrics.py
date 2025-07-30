from prometheus_client import start_http_server, Counter, Gauge, Histogram
import time
from loguru import logger

# Application Metrics
PREDICTION_COUNTER = Counter(
    'wingo_predictions_total',
    'Total predictions made',
    ['color', 'size']
)

CORRECT_PREDICTION_COUNTER = Counter(
    'wingo_correct_predictions_total',
    'Total correct predictions',
    ['type']  # color, size, both
)

PREDICTION_TIME = Histogram(
    'wingo_prediction_duration_seconds',
    'Prediction processing time',
    buckets=[0.05, 0.1, 0.25, 0.5, 1, 2.5, 5]
)

DATABASE_LATENCY = Histogram(
    'wingo_db_query_duration_seconds',
    'Database query latency',
    ['query_type']
)

MODEL_ACCURACY = Gauge(
    'wingo_model_accuracy',
    'Model accuracy metrics',
    ['model', 'target']
)

# System Metrics
MEMORY_USAGE = Gauge(
    'wingo_memory_usage_bytes',
    'Current memory usage'
)

CPU_USAGE = Gauge(
    'wingo_cpu_usage_percent',
    'Current CPU usage'
)

def start_metrics_server(port=9100):
    """Start Prometheus metrics server"""
    start_http_server(port)
    logger.info(f"Metrics server started on port {port}")

def track_performance(model_name: str, target: str, accuracy: float):
    """Track model performance metrics"""
    MODEL_ACCURACY.labels(model=model_name, target=target).set(accuracy)