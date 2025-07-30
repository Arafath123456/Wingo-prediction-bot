from .scheduler import init_scheduler
from dotenv import load_dotenv
from loguru import logger
import time

load_dotenv()

if __name__ == "__main__":
    logger.add("data_ingest.log", rotation="1 week", retention="30 days")
    scheduler = init_scheduler()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.shutdown()
        logger.info("Scheduler stopped")