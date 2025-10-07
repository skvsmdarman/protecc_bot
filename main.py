import logging
from telegram import Update
from telegram.constants import ChatType
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- Configuration ---
# Your Bot Token from @BotFather
BOT_TOKEN = "YOUR_BOT_TOKEN" 

# Custom message for users who try to interact with the bot in a private chat
DM_MESSAGE = "This bot is made by: @XCid_Kagenou and is exclusive to the Ashleel X community."

# --- Bot Setup ---
# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Dictionary to store approved chat IDs (chat_id: owner_id)
approved_chats = {}

# --- Command and Message Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message on /start."""
    if update.effective_chat.type == ChatType.PRIVATE:
        await update.message.reply_text(DM_MESSAGE)
        return

    await update.message.reply_text("Hi! I'm your content protection bot. Add me as an admin to a group and use /approve to enable my features.")

async def approve_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Approves the chat for content protection features."""
    if update.effective_chat.type == ChatType.PRIVATE:
        await update.message.reply_text(DM_MESSAGE)
        return

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    try:
        chat_member = await context.bot.get_chat_member(chat_id, user_id)
        if chat_member.status in ['creator', 'administrator']:
            approved_chats[chat_id] = user_id
            logger.info(f"Chat {chat_id} approved by owner/admin {user_id}")
            await update.message.reply_text(
                "✅ This group has been approved! Any member can now use /protect or /pro by replying to an image or video."
            )
        else:
            await update.message.reply_text("❌ Only the group owner or an administrator can approve this chat.")
    except Exception as e:
        logger.error(f"Error checking admin status in chat {chat_id}: {e}")
        await update.message.reply_text("An error occurred. Make sure I am an administrator in this group.")


async def protect_content(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /protect or /pro command to send protected content."""
    if update.effective_chat.type == ChatType.PRIVATE:
        await update.message.reply_text(DM_MESSAGE)
        return

    chat_id = update.effective_chat.id
    if chat_id not in approved_chats:
        await update.message.reply_text(
            "This group is not approved. The group owner/admin needs to use /approve first."
        )
        return

    if not update.message.reply_to_message:
        await update.message.reply_text(
            "Please reply to an image or video with /protect or /pro to make it protected."
        )
        return

    original_message = update.message.reply_to_message
    
    # Check if the replied message contains a photo or video
    if original_message.photo:
        # Get the largest photo file_id
        photo_file_id = original_message.photo[-1].file_id
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=photo_file_id,
            caption=original_message.caption,
            protect_content=True, # This is the modern way to protect content
        )
        await original_message.delete()
        await update.message.delete() # Deletes the "/protect" command message
    elif original_message.video:
        video_file_id = original_message.video.file_id
        await context.bot.send_video(
            chat_id=chat_id,
            video=video_file_id,
            caption=original_message.caption,
            protect_content=True, # This is the modern way to protect content
        )
        await original_message.delete()
        await update.message.delete() # Deletes the "/protect" command message
    else:
        await update.message.reply_text("I can only protect images or videos. Please reply to an image or video.")

async def handle_dm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles any non-command messages received in DMs."""
    if update.effective_chat.type == ChatType.PRIVATE:
        await update.message.reply_text(DM_MESSAGE)

# --- Main Bot Function ---

def main() -> None:
    """Start the bot."""
    print("Bot is starting...")
    application = Application.builder().token(BOT_TOKEN).build()

    # Handlers for commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("approve", approve_chat))
    application.add_handler(CommandHandler(["protect", "pro"], protect_content))

    # Handler for any other message in DMs
    application.add_handler(MessageHandler(filters.ChatType.PRIVATE & ~filters.COMMAND, handle_dm))

    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    print("Bot is running.")

if __name__ == "__main__":
    main()
