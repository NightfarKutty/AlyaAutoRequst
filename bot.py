import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ChatJoinRequestHandler,
    CallbackContext,
)

# Bot token aur admin ID environment variables se lenge
BOT_TOKEN = os.getenv("BOT_TOKEN", "7546733528:AAHdvZlHjJxWg-Pxz-SmfUy1nU5GBzrF1NU")
ADMIN_ID = int(os.getenv("ADMIN_ID", "7561026494"))

async def start(update: Update, context: CallbackContext) -> None:
    """Bot start command"""
    await update.message.reply_text(
        "Namaste! Main ek auto request accept bot hoon. Mujhe apke channel ya group mein admin banaye aur join requests apne aap accept honge!"
    )

async def handle_join_request(update: Update, context: CallbackContext) -> None:
    """Naye join requests ko handle karta hai"""
    join_request = update.chat_join_request
    chat = join_request.chat
    user = join_request.from_user

    try:
        # Request ko approve karo
        await context.bot.approve_chat_join_request(
            chat_id=chat.id,
            user_id=user.id
        )
        
        # Welcome message bhejo (optional)
        welcome_msg = f"Namaste {user.first_name}! {chat.title} mein swagat hai!"
        await context.bot.send_message(
            chat_id=user.id,
            text=welcome_msg
        )
        
        # Admin ko notification bhejo
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"New member: {user.first_name} (ID: {user.id}) joined {chat.title}"
        )
        
    except Exception as e:
        # Error logging
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"Error approving join request: {str(e)}"
        )

async def stats(update: Update, context: CallbackContext) -> None:
    """Admin ke liye stats command"""
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("Ye command sirf admin ke liye hai!")
        return
        
    # Basic stats (is example mein static hai, aap database ya counter add kar sakte hain)
    await update.message.reply_text(
        "Bot Stats:\n- Active Channels: 1\n- Total Approved Requests: N/A\nStats abhi basic hain, aur features jaldi add honge!"
    )

def main() -> None:
    """Bot ko run karne ka main function"""
    # Application initialize karo
    application = Application.builder().token(BOT_TOKEN).build()

    # Handlers add karo
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(ChatJoinRequestHandler(handle_join_request))

    # Bot start karo
    print("Bot shuru ho raha hai...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
