from telegram.ext import Application, CommandHandler
from telegram import Update
from .commands import (
    start_command, 
    generate_command, 
    history_command, 
    stats_command, 
    help_command
)
from dotenv import load_dotenv
import os
import logging
from loguru import logger

# Load environment variables
load_dotenv()

def setup_bot():
    """Initialize and configure the Telegram bot"""
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN environment variable is missing")
    
    # Create application
    application = Application.builder().token(token).build()
    
    # Register command handlers
    command_handlers = [
        ('start', start_command),
        ('generate', generate_command),
        ('history', history_command),
        ('stats', stats_command),
        ('help', help_command)
    ]
    
    for command, handler in command_handlers:
        application.add_handler(CommandHandler(command, handler))
    
    # Add middleware for user whitelisting
    if whitelist := os.getenv("USER_WHITELIST"):
        user_ids = [int(x.strip()) for x in whitelist.split(",")]
        application.add_handler(
            CommandHandler("start", start_command), 
            custom_filters=lambda update: update.effective_user.id in user_ids
        )
    
    return application

def run_bot():
    """Run the Telegram bot"""
    logger.info("Starting Telegram bot...")
    application = setup_bot()
    
    # Start polling
    application.run_polling(
        poll_interval=1,
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES
    )