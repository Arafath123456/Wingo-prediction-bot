import os
from dotenv import load_dotenv

load_dotenv()

def is_user_whitelisted(user_id: int) -> bool:
    """Check if user is in whitelist"""
    whitelist = os.getenv("USER_WHITELIST", "")
    if not whitelist:
        return True  # Allow all if no whitelist
    
    allowed_ids = [int(x.strip()) for x in whitelist.split(",")]
    return user_id in allowed_ids

def rate_limit_user(user_id: int) -> bool:
    """Simple rate limiting mechanism"""
    # TODO: Implement proper rate limiting with Redis
    return False  # No rate limiting for now