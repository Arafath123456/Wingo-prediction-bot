from ml_engine.prediction import WinGoPredictor
from database import get_session, get_latest_rounds
from .responses import generate_response
from loguru import logger
from telegram import Update
from telegram.ext import ContextTypes
from database.crud import get_latest_rounds, get_prediction_history, get_performance_stats
from prediction_logger import log_prediction
from ml_engine.prediction import WinGoPredictor
from database.session import get_session
from security import secure_command
from .utils import is_user_whitelisted
import logging
from loguru import logger
from telegram_bot.access_management import register_user, approve_user
from security.rate_limiting import rate_limit_user, clear_rate_limits
from security.input_validation import validate_command
from .responses import (
    generate_response, 
    history_response, 
    stats_response, 
    help_response
)


@secure_command
async def register_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /register command with CAPTCHA"""
    user = update.effective_user
    try:
        session = get_session()
        user_access, captcha = register_user(session, user.id, user.username)
        
        await update.message.reply_text(
            f"📝 Registration initiated!\n\n"
            f"Please solve this CAPTCHA to complete registration:\n"
            f"🔢 `{captcha}`\n\n"
            f"Reply with:\n/captcha [code]"
        )
    except Exception as e:
        await update.message.reply_text("⚠️ Registration failed. Contact admin for help.")

@secure_command
async def captcha_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /captcha [code] command"""
    user = update.effective_user
    try:
        token = context.args[0] if context.args else ""
        session = get_session()
        user_access = session.query(UserAccess).filter_by(telegram_id=str(user.id)).first()
        
        if not user_access:
            await update.message.reply_text("⚠️ Start with /register first")
            return
        
        if user_access.verify_captcha(token):
            await update.message.reply_text(
                "✅ CAPTCHA verified! Your account is pending admin approval.\n\n"
                "You'll receive a notification when approved."
            )
        else:
            await update.message.reply_text("❌ Invalid CAPTCHA. Try again with /register")
    except Exception as e:
        await update.message.reply_text("⚠️ CAPTCHA verification failed")

@secure_command
async def admin_approve_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command: /approve [user_id] [access_level]"""
    user = update.effective_user
    if not is_user_admin(user.id):
        await update.message.reply_text("⛔ Admin access required")
        return
    
    try:
        target_id = context.args[0]
        access_level = context.args[1] if len(context.args) > 1 else "basic"
        
        session = get_session()
        approved_user = approve_user(session, target_id, access_level)
        
        await update.message.reply_text(
            f"✅ Approved user {approved_user.telegram_username or target_id}\n"
            f"Access level: {access_level}"
        )
        
        # Notify the approved user
        await context.bot.send_message(
            chat_id=target_id,
            text="🎉 Your account has been approved! You can now use /generate"
        )
    except Exception as e:
        await update.message.reply_text(f"⚠️ Approval failed: {str(e)}")

@secure_command
async def admin_clear_ratelimit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command: /clear_ratelimit [user_id]"""
    user = update.effective_user
    if not is_user_admin(user.id):
        await update.message.reply_text("⛔ Admin access required")
        return
    
    try:
        target_id = context.args[0]
        clear_rate_limits(target_id)
        await update.message.reply_text(f"✅ Cleared rate limits for user {target_id}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Clear failed: {str(e)}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    
    if not is_user_whitelisted(user.id):
        await update.message.reply_text(
            "⛔ Access Denied. Contact admin for access."
        )
        logger.warning(f"Unauthorized access attempt by user {user.id}")
        return
    
    welcome_msg = (
        "🌟 Welcome to WinGo 30s Prediction Bot!\n\n"
        "I analyze WinGo game patterns to predict the next outcome.\n\n"
        "📋 Available commands:\n"
        "/generate - Get next prediction\n"
        "/history - Show recent predictions\n"
        "/stats - View bot performance\n"
        "/help - Usage instructions"
    )
    await update.message.reply_text(welcome_msg)
    logger.info(f"New session started for user {user.id}")

@secure_command
async def generate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /generate command"""
    if not is_user_whitelisted(update.effective_user.id):
        return
    
    # TODO: Connect to actual prediction engine (Part 4)
    # For now return mock response
    response = generate_response(
        period_number="20240729042",
        color="Red",
        size="Big",
        confidence=78.5
    )
    await update.message.reply_text(response)
    logger.info(f"Prediction generated for user {update.effective_user.id}")

async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /history command"""
    if not is_user_whitelisted(update.effective_user.id):
        return
    
    # TODO: Connect to database (Part 4)
    response = history_response()
    await update.message.reply_text(response)
    logger.info(f"History requested by user {update.effective_user.id}")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command"""
    if not is_user_whitelisted(update.effective_user.id):
        return
    
    # TODO: Connect to stats module (Part 4)
    response = stats_response()
    await update.message.reply_text(response)
    logger.info(f"Stats requested by user {update.effective_user.id}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    response = help_response()
    await update.message.reply_text(response, parse_mode="Markdown")
    logger.info(f"Help requested by user {update.effective_user.id}")


# Initialize predictor
predictor = WinGoPredictor()

async def generate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /generate command"""
    if not is_user_whitelisted(update.effective_user.id):
        return
    
    try:
        # Get latest data
        session = get_session()
        historical_data = get_latest_rounds(session, 500)
        
        # Generate prediction
        prediction = predictor.predict_next(historical_data)
        
        # Format response
        response = generate_response(
            period_number=prediction['next_period'],
            color=prediction['predicted_color'],
            size=prediction['predicted_size'],
            confidence=prediction['overall_confidence']
        )
        
        await update.message.reply_text(response)
        logger.info(f"Prediction generated for {prediction['next_period']}")
        
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        await update.message.reply_text("⚠️ Prediction service unavailable. Try again later.")


# Initialize predictor
predictor = WinGoPredictor()

async def generate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /generate command"""
    if not is_user_whitelisted(update.effective_user.id):
        return
    
    try:
        # Get latest data
        session = get_session()
        historical_data = get_latest_rounds(session, 500)
        
        # Generate prediction
        prediction = predictor.predict_next(historical_data)
        
        # Log prediction
        log_prediction(session, prediction)
        
        # Format response
        response = generate_response(
            period_number=prediction['next_period'],
            color=prediction['predicted_color'],
            size=prediction['predicted_size'],
            confidence=prediction['overall_confidence']
        )
        
        await update.message.reply_text(response)
        logger.info(f"Prediction generated for {prediction['next_period']}")
        
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        await update.message.reply_text("⚠️ Prediction service unavailable. Try again later.")

@secure_command
async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /history command"""
    if not is_user_whitelisted(update.effective_user.id):
        return
    
    try:
        session = get_session()
        history = get_prediction_history(session, 10)
        
        if not history:
            await update.message.reply_text("No prediction history available yet.")
            return
        
        response = format_history_response(history)
        await update.message.reply_text(response)
        
    except Exception as e:
        logger.error(f"History command failed: {str(e)}")
        await update.message.reply_text("⚠️ Failed to retrieve history.")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command"""
    if not is_user_whitelisted(update.effective_user.id):
        return
    
    try:
        session = get_session()
        stats = get_performance_stats(session)
        
        if not stats:
            await update.message.reply_text("Performance statistics not available yet.")
            return
        
        response = format_stats_response(stats)
        await update.message.reply_text(response)
        
    except Exception as e:
        logger.error(f"Stats command failed: {str(e)}")
        await update.message.reply_text("⚠️ Failed to retrieve statistics.")