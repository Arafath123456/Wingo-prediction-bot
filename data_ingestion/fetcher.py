import httpx
from loguru import logger
from sqlalchemy.orm import Session
from datetime import datetime
from .models import WingoRound
from prediction_logger import update_prediction_with_result

API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_30S/GetHistoryIssuePage.json"

def fetch_rounds() -> list[dict]:
    try:
        response = httpx.get(API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("success") and data.get("data", {}).get("list"):
            return data["data"]["list"]
        logger.error("Invalid API response structure")
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        logger.error(f"API request failed: {str(e)}")
    return []

def process_rounds(session: Session):
    try:
        # Fetch and process new rounds
        new_rounds = 0
        for item in fetch_rounds():
            if not session.get(WingoRound, item["issueNumber"]):
                # Convert draw_time to UTC timestamp
                draw_time = datetime.strptime(
                    item["drawTime"], "%Y-%m-%d %H:%M:%S"
                ).replace(tzinfo=timezone.utc)
                
                session.add(WingoRound(
                    issue_number=item["issueNumber"],
                    winning_number=item["winningNumber"],
                    draw_time=draw_time
                ))
                new_rounds += 1
        
        session.commit()
        logger.info(f"Added {new_rounds} new rounds")
        
        # Maintain only last 500 rounds
        total_rounds = session.query(WingoRound).count()
        if total_rounds > 500:
            oldest = session.query(WingoRound.issue_number)\
                .order_by(WingoRound.draw_time.desc())\
                .offset(500)\
                .subquery()
                
            session.query(WingoRound)\
                .filter(WingoRound.issue_number.in_(oldest))\
                .delete(synchronize_session=False)
            session.commit()
            logger.info(f"Cleaned {total_rounds - 500} old records")
            
    except Exception as e:
        session.rollback()
        logger.exception("Data processing failed")


def process_rounds(session: Session):
    try:
        # ... existing processing logic ...
        
        # After adding new rounds, update predictions with results
        for item in rounds_data:
            issue_number = item["issueNumber"]
            winning_number = item["winningNumber"]
            
            # Check if we have a prediction for this round
            update_prediction_with_result(session, issue_number, winning_number)
            
    except Exception as e:
        session.rollback()
        logger.exception("Data processing failed")