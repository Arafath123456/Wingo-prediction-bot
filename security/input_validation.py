import re
from telegram import Update

def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent injection attacks"""
    # Remove any non-alphanumeric characters except basic punctuation
    return re.sub(r'[^a-zA-Z0-9_\-/,.!? ]', '', text)[:100]

def validate_period_number(period: str) -> bool:
    """Validate period number format"""
    return bool(re.match(r'^[0-9]{8,12}$', period))

def validate_command(update: Update) -> bool:
    """Validate Telegram command structure"""
    if not update.message or not update.message.text:
        return False
    
    command = update.message.text.split()[0]
    return bool(re.match(r'^/[a-z]+$', command))