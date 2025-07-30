from data_ingestion.scheduler import init_scheduler as init_data_scheduler
from telegram_bot.bot import run_bot as run_telegram_bot
from ml_engine.model_training import train_all_models
from database import get_session, get_latest_rounds
from threading import Thread
import time
from loguru import logger
from database.session import init_db
from monitoring import init_monitoring
from monitoring.metrics import start_metrics_server
from monitoring.sentry_config import init_sentry
from monitoring.health_server import init_health_monitoring
from backtesting.backtest_runner import BacktestRunner
import schedule
from loguru import logger

def periodic_backtesting():
    """Schedule regular backtesting"""
    def run_backtest():
        logger.info("Starting scheduled backtest...")
        runner = BacktestRunner()
        report = runner.run_and_report()
        if report:
            logger.info(f"Backtest completed: Overall accuracy {report['overall_accuracy']:.2%}")
    
    # Run immediately on startup
    run_backtest()
    
    # Schedule daily backtests at 3 AM
    schedule.every().day.at("03:00").do(run_backtest)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

def main():
    # Initialize monitoring
    init_sentry()
    init_health_monitoring()
    start_metrics_server(port=9100)
    
    # Initialize database
    init_db()
    
    # Start data ingestion
    data_thread = Thread(target=init_data_scheduler, daemon=True)
    data_thread.start()
    
    # Start model training scheduler
    training_thread = Thread(target=train_models_periodically, daemon=True)
    training_thread.start()
    
    # Start backtesting scheduler
    backtest_thread = Thread(target=periodic_backtesting, daemon=True)
    backtest_thread.start()
    
    # Start Telegram bot
    try:
        run_telegram_bot()
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.exception("Critical error in Telegram bot")
        raise

def main():
    # Initialize database
    init_db()
    
    # Initialize logging
    logger.add("app.log", rotation="1 week", retention="30 days", level="DEBUG")
    
    # ... rest of the main function ...

def main():
    init_monitoring() 
    init_db()

def train_models_periodically():
    """Periodically retrain ML models"""
    import schedule
    from datetime import time as time_obj
    
    def train_job():
        try:
            session = get_session()
            data = get_latest_rounds(session, 500)
            train_all_models(data)
            logger.success("Models retrained successfully")
        except Exception as e:
            logger.error(f"Model training failed: {str(e)}")
    
    # Train immediately on startup
    train_job()
    
    # Schedule daily retraining at 2 AM UTC
    schedule.every().day.at("02:00").do(train_job)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

def main():
    # Initialize logging
    logger.add("app.log", rotation="1 week", retention="30 days", level="DEBUG")
    
    # Start data ingestion
    data_thread = Thread(target=init_data_scheduler, daemon=True)
    data_thread.start()
    logger.info("Data ingestion scheduler started")
    
    # Start model training scheduler
    training_thread = Thread(target=train_models_periodically, daemon=True)
    training_thread.start()
    logger.info("Model training scheduler started")
    
    # Start Telegram bot
    try:
        run_telegram_bot()
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.exception("Critical error in Telegram bot")

if __name__ == "__main__":
    main()