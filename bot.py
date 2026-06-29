from os import environ
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, ChatJoinRequest, CallbackQuery
from pyrogram.errors import UserPrivacyRestricted
from os import environ
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

class Keeper(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Alive!")

def run_port():
    server = HTTPServer(('0.0.0.0', int(environ.get("PORT", 8080))), Keeper)
    server.serve_forever()

threading.Thread(target=run_port, daemon=True).start()

# --- Main Bot Code By Alone Kutty ---

pr0fess0r_99 = Client(
    "Auto Approved Bot",
    bot_token = environ["8527654246:AAESrxK56QN9P54k2UE2THMfmh_Y3pTLkPY"],
    api_id = int(environ["34358468"]),
    api_hash = environ["98eae42531ae122648f7cd930c458661"]
)

CHAT_ID = [int(pr0fess0r_99) for pr0fess0r_99 in environ.get("CHAT_ID", None).split()]
TEXT = environ.get("APPROVED_WELCOME_TEXT", "Hello {mention}\nWelcome To {title}\n\nYour Auto Approved")
APPROVED = environ.get("APPROVED_WELCOME", "on").lower()

# 🖼️ URLs for Images
START_IMAGE_URL = "https://graph.org/file/a633dd3e3d423506f2c3a-bd2a06710bc9ad8884.jpg"
ACCEPT_IMAGE_URL = "https://graph.org/file/f96a490cd143e6e11ff1a-7b378174a3d79ff84b.jpg"

ABOUT_TXT = "<b><blockquote>◈ ᴄʀᴇᴀᴛᴏʀ: <a href=https://t.me/KuttyHacker>ɴꜰᴛ ᴋᴜᴛᴛʏ</a>\n◈ ɴɪɢʜᴛꜰᴀʀ ɴᴇᴛᴡᴏʀᴋ : <a href=https://t.me/NightFarBots>ɴꜰᴛ ᴛᴇᴀᴍ</a>\n◈ ᴛᴀᴍɪʟ ᴀɴɪᴍᴇ ᴄʜᴀɴɴᴇʟ : <a href=https://t.me/KuttyAnimes> ᴋᴜᴛᴛʏ ᴀɴɪᴍᴇꜱ</a>\n◈ ᴀɴɪᴍᴇ ʀᴇ𝚀ᴜꜱᴛ ɢʀᴏᴜᴩ : <a href=https://t.me/Pro_KuttyAnimes>ᴛᴀᴍɪʟ ᴄʜᴀᴛ ᴋᴀᴄ</a>\n◈ ᴛᴀᴍɪʟ ᴍᴏᴠɪᴇꜱ : <a href=https://t.me/UnixLinks>ᴜɴɪ𝘹 ʟɪɴᴋꜱ</a>\n◈ ꜰᴜɴ ᴛᴀᴍɪʟ ᴄʜᴀᴛ : <a href=https://t.me/TamilChat_Friendship_47>ʟɪᴛᴛʟᴇ ʜᴇᴀʀᴛꜱ</a></blockquote></b>"

@pr0fess0r_99.on_message(filters.private & filters.command(["start"]))
async def start(client: pr0fess0r_99, message: Message):
    approvedbot = await client.get_me() 
    
    button = [
        [InlineKeyboardButton("· ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ᴄʜᴀᴛ ·", url=f"http://t.me/{approvedbot.username}?startgroup=botstart")],
        [InlineKeyboardButton("· sᴜᴘᴘᴏʀᴛ ·", url="https://t.me/Pro_KuttyAnimes"), InlineKeyboardButton("· ᴏꜰꜰɪᴄᴀʟ ʙᴏᴛ ʙʏ ·", url="https://t.me/NightFarBots")],
        [InlineKeyboardButton("· ᴀʙᴏᴜᴛ ·", callback_data="about_cmd")]
    ]
    
    caption_text = (
        f"👋 **ʜᴇʟʟᴏ {message.from_user.mention}!**\n\n"
        f"🤖 **ɪ ᴀᴍ ᴀɴ ᴀᴜᴛᴏ ᴀᴘᴘʀᴏᴠᴇʀ ᴊᴏɪɴ ʀᴇǫᴜᴇsᴛ ʙᴏᴛ.**\n\n"
        f"❤️ **ᴊᴜsᴛ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴏʀ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴍᴀɴᴀɢᴇ ᴀʟʟ ᴘᴇɴᴅɪɴɢ ᴊᴏɪɴ ʀᴇǫᴜᴇsᴛs ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ɪɴsᴛᴀɴᴛʟʏ!** ✨"
    )
    
    await client.send_photo(
        chat_id=message.chat.id,
        photo=START_IMAGE_URL,
        caption=caption_text,
        reply_markup=InlineKeyboardMarkup(button)
    )

@pr0fess0r_99.on_callback_query(filters.regex("about_cmd"))
async def about_callback(client: pr0fess0r_99, query: CallbackQuery):
    back_button = [[InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="back_start")]]
    await query.message.edit_caption(
        caption=ABOUT_TXT,
        reply_markup=InlineKeyboardMarkup(back_button)
    )

@pr0fess0r_99.on_callback_query(filters.regex("back_start"))
async def back_callback(client: pr0fess0r_99, query: CallbackQuery):
    approvedbot = await client.get_me()
    button = [
        [InlineKeyboardButton("· ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ᴄʜᴀᴛ ·", url=f"http://t.me/{approvedbot.username}?startgroup=botstart")],
        [InlineKeyboardButton("· sᴜᴘᴘᴏʀᴛ ·", url="https://t.me/Pro_KuttyAnimes"), InlineKeyboardButton("· ᴏꜰꜰɪᴄᴀʟ ʙᴏᴛ ʙʏ ·", url="https://t.me/NightFarBots")],
        [InlineKeyboardButton("· ᴀʙᴏᴜᴛ ·", callback_data="about_cmd")]
    ]
    caption_text = (
        f"👋 **ʜᴇʟʟᴏ {query.from_user.mention}!**\n\n"
        f"🤖 **ɪ ᴀᴍ ᴀɴ ᴀᴜᴛᴏ ᴀᴘᴘʀᴏᴠᴇʀ ᴊᴏɪɴ ʀᴇǫᴜᴇsᴛ ʙᴏᴛ.**\n\n"
        f"❤️ **ᴊᴜsᴛ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴏʀ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴍᴀɴᴀɢᴇ ᴀʟʟ ᴘᴇɴᴅɪɴɢ ᴊᴏɪɴ ʀᴇǫᴜᴇsᴛs ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ɪɴsᴛᴀɴᴛʟʏ!** ✨"
    )
    await query.message.edit_caption(
        caption=caption_text,
        reply_markup=InlineKeyboardMarkup(button)
    )

@pr0fess0r_99.on_chat_join_request((filters.group | filters.channel) & filters.chat(CHAT_ID) if CHAT_ID else (filters.group | filters.channel))
async def autoapprove(client: pr0fess0r_99, message: ChatJoinRequest):
    chat = message.chat 
    user = message.from_user 
    approvedbot = await client.get_me()
    
    print(f"{user.first_name} Joined 🤝") 
    await client.approve_chat_join_request(chat_id=chat.id, user_id=user.id)
    
    try:
        pm_caption = (
            f"🎉 **ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ ʜᴀs ʙᴇᴇɴ ᴀᴄᴄᴇᴘᴛᴇᴅ ʙʏ @{approvedbot.username}!**\n\n"
            f"✨ **ᴄʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴏʀ ᴛʏᴘᴇ start ᴛᴏ ᴋɴᴏᴡ ᴍᴏʀᴇ ᴀʙᴏᴜᴛ ᴍᴇ ❤️**"
        )
        pm_button = [[InlineKeyboardButton("ᴛʀʏ ᴛᴏ sᴛᴀʀᴛ", url=f"t.me/{approvedbot.username}?start=true")]]
        
        await client.send_photo(
            chat_id=user.id,
            photo=ACCEPT_IMAGE_URL,
            caption=pm_caption,
            reply_markup=InlineKeyboardMarkup(pm_button)
        )
    except UserPrivacyRestricted:
        print(f"Cannot send PM to {user.first_name} due to privacy settings.")
    except Exception as e:
        print(f"Error sending PM: {e}")

    if APPROVED == "on":
        try:
            await client.send_message(chat_id=chat.id, text=TEXT.format(mention=user.mention, title=chat.title))
        except Exception as e:
            print(f"Error sending group welcome: {e}")

print("Auto Approved Bot Running...")
pr0fess0r_99.run()
