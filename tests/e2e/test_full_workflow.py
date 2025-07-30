import pytest
from main import main
from threading import Thread
import time
from database.crud import get_latest_rounds
from ml_engine.prediction import WinGoPredictor

@pytest.mark.slow
def test_full_workflow(test_session):
    # Start main application components in threads
    from data_ingestion.scheduler import init_data_scheduler
    from telegram_bot.bot import run_telegram_bot
    
    data_thread = Thread(target=init_data_scheduler, daemon=True)
    bot_thread = Thread(target=run_telegram_bot, daemon=True)
    
    data_thread.start()
    bot_thread.start()
    
    # Allow systems to initialize
    time.sleep(5)
    
    # Verify data ingestion
    data = get_latest_rounds(test_session, 10)
    assert len(data) >= 10
    
    # Verify prediction capability
    predictor = WinGoPredictor()
    prediction = predictor.predict_next(data)
    assert 'predicted_color' in prediction
    assert 'predicted_size' in prediction
    
    # TODO: Add Telegram bot interaction tests