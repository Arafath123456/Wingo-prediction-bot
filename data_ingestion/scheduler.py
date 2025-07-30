from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .fetcher import process_rounds
import os
from loguru import logger

def init_scheduler():
    # Initialize database connection
    engine = create_engine(os.getenv("DATABASE_URL"))
    Session = sessionmaker(bind=engine)
    
    # Configure scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        lambda: process_rounds(Session()),
        'interval',
        seconds=30,
        max_instances=1,
        misfire_grace_time=60
    )
    
    # Initial data load
    process_rounds(Session())
    scheduler.start()
    logger.info("Scheduler started with 30s interval")
    return scheduler