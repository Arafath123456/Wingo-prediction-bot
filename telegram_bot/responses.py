def generate_response(period_number: str, color: str, size: str, confidence: float) -> str:
    """Format prediction response"""
    return (
        f"🎯 Next Period: #{period_number}\n\n"
        f"✅ Predicted Color: {color}\n"
        f"✅ Predicted Size: {size}\n"
        f"⚡️ Confidence: {confidence:.1f}%\n\n"
        "⚠️ Note: Predictions are probabilistic. Gamble responsibly."
    )

def history_response() -> str:
    """Format history response"""
    # TODO: Replace with actual data from DB
    return (
        "📜 Recent Predictions:\n\n"
        "1. #20240729041: 🔴 Red | Big (Confidence: 76.2%)\n"
        "   ✅ Actual: Red | Big\n\n"
        "2. #20240729040: 🟢 Green | Small (Confidence: 68.9%)\n"
        "   ❌ Actual: Violet | Big\n\n"
        "3. #20240729039: 🔵 Violet | Small (Confidence: 82.1%)\n"
        "   ✅ Actual: Violet | Small\n\n"
        "Last updated: 2024-07-29 14:30 UTC"
    )

def stats_response() -> str:
    """Format stats response"""
    # TODO: Replace with actual stats
    return (
        "📊 Bot Performance Stats:\n\n"
        "• Overall Accuracy: 74.3%\n"
        "• Color Accuracy: 76.8%\n"
        "• Size Accuracy: 71.9%\n"
        "• Last 50 Rounds: 79.2%\n\n"
        "⏱ Last Prediction: 2024-07-29 14:31 UTC\n"
        "🔄 Predictions Made: 1,243"
    )

def help_response() -> str:
    """Format help response"""
    return (
        "ℹ️ *WinGo 30s Bot Help*\n\n"
        "*/start* - Initialize the bot\n"
        "*/generate* - Get next prediction\n"
        "*/history* - Show recent predictions\n"
        "*/stats* - View accuracy statistics\n"
        "*/help* - Show this message\n\n"
        "🔒 *Access Control*\n"
        "This bot is restricted to authorized users only. Contact @AdminUser to request access.\n\n"
        "⚙️ *How It Works*\n"
        "1. I analyze the last 500 rounds\n"
        "2. Use AI models to detect patterns\n"
        "3. Predict the next color/size combination\n"
        "4. Update every 30 seconds with new data\n\n"
        "⚠️ *Disclaimer*\n"
        "Predictions are probabilistic estimates. Past performance doesn't guarantee future results. Gamble responsibly."
    )

def format_history_response(history: list) -> str:
    """Format history response from database records"""
    lines = []
    for i, record in enumerate(history, 1):
        color_emoji = "🟢" if record.predicted_color == "Green" else "🔴" if record.predicted_color == "Red" else "🔵"
        status = ""
        
        if record.actual_color:
            color_match = "✅" if record.predicted_color == record.actual_color else "❌"
            size_match = "✅" if record.predicted_size == record.actual_size else "❌"
            status = f"\n   {color_match} Color | {size_match} Size | Actual: {record.actual_color} | {record.actual_size}"
        
        lines.append(
            f"{i}. #{record.issue_number}: {color_emoji} {record.predicted_color} | "
            f"{record.predicted_size} (Confidence: {record.confidence:.1f}%){status}"
        )
    
    return "📜 Recent Predictions:\n\n" + "\n\n".join(lines)

def format_stats_response(stats: dict) -> str:
    """Format stats response from statistics"""
    return (
        f"📊 Bot Performance Stats:\n\n"
        f"• Overall Accuracy: {stats['overall_accuracy']:.1f}%\n"
        f"• Color Accuracy: {stats['color_accuracy']:.1f}%\n"
        f"• Size Accuracy: {stats['size_accuracy']:.1f}%\n"
        f"• Recent Accuracy (Last 50): {stats['recent_accuracy']:.1f}%\n"
        f"• Total Predictions: {stats['total_predictions']}\n"
        f"• Correct Predictions: {stats['correct_predictions']}\n\n"
        f"⏱ Last Prediction: {stats['last_prediction']}"
    )