from telegram_bot.commands import generate_command
from telegram import Update, User
from unittest.mock import AsyncMock, MagicMock

async def test_generate_command_success():
    # Mock update and context
    update = MagicMock(spec=Update)
    update.effective_user = User(id=123, first_name="Test", is_bot=False)
    update.message = MagicMock()
    context = MagicMock()
    
    # Mock dependencies
    with patch('telegram_bot.commands.is_user_whitelisted', return_value=True), \
         patch('telegram_bot.commands.get_session') as mock_session, \
         patch('ml_engine.prediction.WinGoPredictor.predict_next') as mock_predict:
        
        # Setup mock prediction
        mock_predict.return_value = {
            'next_period': '20230729042',
            'predicted_color': 'Red',
            'predicted_size': 'Big',
            'overall_confidence': 78.5
        }
        
        # Execute command
        await generate_command(update, context)
        
        # Verify response
        update.message.reply_text.assert_called()
        assert "Red" in update.message.reply_text.call_args[0][0]
        assert "Big" in update.message.reply_text.call_args[0][0]