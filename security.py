import re
from telegram.ext import ContextTypes
from telegram import Update
from loguru import logger

def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent injection attacks"""
    return re.sub(r'[^a-zA-Z0-9_\-/ ]', '', text)

def rate_limit_user(user_id: int, command: str) -> bool:
    """Implement rate limiting using Redis"""
    # TODO: Implement with Redis
    return False

def secure_command(handler):
    """Decorator to add security to command handlers"""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Input sanitization
        if update.message and update.message.text:
            update.message.text = sanitize_input(update.message.text)
        
        # Rate limiting
        user_id = update.effective_user.id
        if rate_limit_user(user_id, handler.__name__):
            await update.message.reply_text(
                "⚠️ Too many requests. Please try again later."
            )
            logger.warning(f"Rate limit exceeded for user {user_id}")
            return
        
        # Execute command
        return await handler(update, context)
    return wrapper