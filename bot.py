import os
from os import environ
import threading
import re
import asyncio
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, ChatJoinRequest, CallbackQuery, ChatPermissions
from pyrogram.errors import UserPrivacyRestricted, ChatAdminRequired, UserAdminInvalid, FloodWait

# --- Web Service Port Binding ---
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
    bot_token = "8527654246:AAESrxK56QN9P54k2UE2THMfmh_Y3pTLkPY",
    api_id = 34358468,
    api_hash = "98eae42531ae122648f7cd930c458661"
)

# --- Config Variables ---
OWNER_ID = int(environ.get("OWNER_ID", "6657954117")) # உங்கள் Owner ID-ஐ இங்கே மாற்றிக்கொள்ளலாம்.
CHAT_ID = [int(x) for x in environ.get("CHAT_ID", "").split() if x.isdigit()]

# In-memory storage
AUTO_APPROVE_STATUS = {}
CUSTOM_WELCOME_TEXT = {}
CUSTOM_WELCOME_PHOTO = {}
GROUP_FILTERS = {}
WHITELISTED_BIO_USERS = {}
PM_USERS = set() # /start செய்த யூசர்களின் பட்டியல்

START_IMAGE_URL = "https://graph.org/file/a633dd3e3d423506f2c3a-bd2a06710bc9ad8884.jpg"
ACCEPT_IMAGE_URL = "https://graph.org/file/f96a490cd143e6e11ff1a-7b378174a3d79ff84b.jpg"
HELP_IMAGE_URL = "https://graph.org/file/f96a490cd143e6e11ff1a-7b378174a3d79ff84b.jpg"
DEFAULT_WELCOME = "ʜᴇʟʟᴏ {mention}\nᴡᴇʟᴄᴏᴍᴇ ᴛᴏ {title}\n\nʏᴏᴜʀ ᴀᴜᴛᴏ ᴀᴘᴘʀᴏᴠᴇᴅ"

ABOUT_TXT = "<b><blockquote>◈ ᴄʀᴇᴀᴛᴏʀ: <a href=https://t.me/KuttyHacker>ɴꜰᴛ ᴋᴜᴛᴛʏ</a>\n◈ ɴɪɢʜᴛꜰᴀʀ ɴᴇᴛᴡᴏʀᴋ : <a href=https://t.me/NightFarBots>ɴꜰᴛ ᴛᴇᴀᴍ</a>\n◈ ᴛᴀᴍɪʟ ᴀɴɪᴍᴇ ᴄʜᴀɴɴᴇʟ : <a href=https://t.me/KuttyAnimes> ᴋᴜᴛty ᴀɴɪᴍᴇꜱ</a>\n◈ ᴀɴɪᴍᴇ ʀᴇ𝚀ᴜꜱᴛ ɢʀᴏᴜᴩ : <a href=https://t.me/Pro_KuttyAnimes>ᴛᴀᴍɪʟ ᴄʜᴀᴛ ᴋᴀᴄ</a>\n◈ ᴛᴀᴍɪʟ ᴍᴏᴠɪᴇꜱ : <a href=https://t.me/UnixLinks>ᴜɴɪ𝘹 ʟɪɴᴋꜱ</a>\n◈ ꜰᴜɴ ᴛᴀᴍɪʟ ᴄʜᴀᴛ : <a href=https://t.me/TamilChat_Friendship_47>ʟɪᴛᴛʟᴇ ʜᴇᴀʀᴛꜱ</a></blockquote></b>"

# --- Helper Functions ---
async def is_admin(client: Client, chat_id: int, user_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in ["administrator", "creator"]
    except Exception:
        return False

async def extract_user(client: Client, message: Message):
    user_id = None
    user_spec = None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        user_spec = message.text.split(None, 1)[1] if len(message.text.split()) > 1 else None
    else:
        args = message.text.split()
        if len(args) > 1:
            user_spec = args[1]
            if user_spec.isdigit():
                user_id = int(user_spec)
            else:
                try:
                    user = await client.get_users(user_spec)
                    user_id = user.id
                except Exception:
                    return None, None
            user_spec = message.text.split(None, 2)[2] if len(args) > 2 else None
    return user_id, user_spec

def parse_time(time_str: str):
    if not time_str:
        return None
    match = re.match(r"(\d+)([mhdw])", time_str.lower())
    if not match:
        return None
    value, unit = match.groups()
    value = int(value)
    if unit == 'm': return datetime.now() + timedelta(minutes=value)
    if unit == 'h': return datetime.now() + timedelta(hours=value)
    if unit == 'd': return datetime.now() + timedelta(days=value)
    if unit == 'w': return datetime.now() + timedelta(weeks=value)
    return None

# --- Owner Broadcast Feature ---
@pr0fess0r_99.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("❌ **ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ʙʀᴏᴀᴅᴄᴀsᴛ!**")
        return

    reply_msg = message.reply_to_message
    status_msg = await message.reply_text("🔄 **ʙʀᴏᴀᴅᴄᴀsᴛ sᴛᴀʀᴛɪɴɢ...**")
    
    success_users = 0
    success_chats = 0
    
    # 1. Broadcasting to PM Users
    for user_id in list(PM_USERS):
        try:
            await reply_msg.copy(chat_id=user_id)
            success_users += 1
            await asyncio.sleep(0.3)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await reply_msg.copy(chat_id=user_id)
            success_users += 1
        except Exception:
            pass

    # 2. Broadcasting to Configured Groups
    for chat_id in CHAT_ID:
        try:
            await reply_msg.copy(chat_id=chat_id)
            success_chats += 1
            await asyncio.sleep(0.3)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await reply_msg.copy(chat_id=chat_id)
            success_chats += 1
        except Exception:
            pass

    await status_msg.edit_text(
        f"📢 **ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ!**\n\n"
        f"👤 **ᴜsᴇʀs ʀᴇᴀᴄʜᴇᴅ:** `{success_users}`\n"
        f"👥 **ɢʀᴏᴜᴘs ʀᴇᴀᴄʜᴇᴅ:** `{success_chats}`"
    )

# --- Anti-Link, Anti-Bot Username & Bio Link Protector ---
@pr0fess0r_99.on_message(filters.group & ~filters.service, group=-1)
async def security_protector(client: Client, message: Message):
    if not message.from_user:
        return

    chat_id = message.chat.id
    user_id = message.from_user.id

    if await is_admin(client, chat_id, user_id):
        return

    text = message.text or message.caption or ""
    
    has_link = re.search(r"(https?://[^\s]+|t\.me/[^\s]+|telegram\.me/[^\s]+)", text, re.IGNORECASE)
    has_bot_username = re.search(r"@[a-zA-Z0-9_]*bot\b", text, re.IGNORECASE)

    if has_link or has_bot_username:
        try:
            await message.delete()
            await message.reply_text(f"⚠️ {message.from_user.mention} **ʟɪɴᴋ / ʙᴏᴛ ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ!**")
            return
        except Exception as e:
            print(f"Error in Anti-Link: {e}")
            return

    if chat_id in WHITELISTED_BIO_USERS and user_id in WHITELISTED_BIO_USERS[chat_id]:
        return

    try:
        full_user = await client.get_chat_member(chat_id, user_id)
        user_info = full_user.user
        bio = user_info.bio or ""
        
        if bio:
            bio_has_link = re.search(r"(https?://[^\s]+|t\.me/[^\s]+|telegram\.me/[^\s]+)", bio, re.IGNORECASE)
            bio_has_username = re.findall(r"@([a-zA-Z0-9_]{5,32})", bio)
            
            is_violating = False
            if bio_has_link:
                is_violating = True
            elif bio_has_username:
                for uname in bio_has_username:
                    if not user_info.username or uname.lower() != user_info.username.lower():
                        is_violating = True
                        break

            if is_violating:
                await message.delete()
                alert_text = f"⚠️ {message.from_user.mention} **ʏᴏᴜʀ ʙɪᴏ ᴄᴏɴᴛᴀɪɴs ᴀ ʟɪɴᴋ ᴏʀ ᴄʜᴀɴɴᴇʟ/ɢʀᴏᴜᴘ ᴜsᴇʀɴᴀᴍᴇ. ᴘʟᴇᴀsᴇ ʀᴇᴍᴏᴠᴇ ɪᴛ ᴛᴏ ᴄʜᴀᴛ ʜᴇʀᴇ!**"
                buttons = [[
                    InlineKeyboardButton("✅ ᴀʟʟᴏᴡᴇᴅ ᴍsɢ ɢʀᴏᴜᴘ", callback_data=f"allow_bio_{user_id}")
                ]]
                await client.send_message(chat_id=chat_id, text=alert_text, reply_markup=InlineKeyboardMarkup(buttons))
                
    except Exception as e:
        print(f"Error checking bio: {e}")

# --- Group Filter Commands ---
@pr0fess0r_99.on_message(filters.group & filters.command("filter"))
async def add_filter_cmd(client: Client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id): return
    if not message.reply_to_message:
        await message.reply_text("❌ **ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴛᴇxᴛ, ɪᴍᴀɢᴇ, ᴏʀ sᴛɪᴄᴋᴇʀ ᴛᴏ sᴀᴠᴇ ɪᴛ ᴀs ᴀ ꜰɪʟᴛᴇʀ!**")
        return
    args = message.text.split(None, 1)
    if len(args) < 2:
        await message.reply_text("❌ **ᴘʟᴇᴀsᴇ sᴘᴇᴄɪꜰʏ ᴀ ᴋᴇʏᴡᴏʀᴅ ꜰᴏʀ ᴛʜᴇ ꜰɪʟᴛᴇʀ!**")
        return
    keyword = args[1].lower().strip()
    chat_id = message.chat.id
    reply = message.reply_to_message
    if chat_id not in GROUP_FILTERS: GROUP_FILTERS[chat_id] = {}
    if reply.text: GROUP_FILTERS[chat_id][keyword] = {"type": "text", "data": reply.text.markdown}
    elif reply.photo: GROUP_FILTERS[chat_id][keyword] = {"type": "photo", "file_id": reply.photo.file_id, "caption": reply.caption.markdown if reply.caption else None}
    elif reply.sticker: GROUP_FILTERS[chat_id][keyword] = {"type": "sticker", "file_id": reply.sticker.file_id}
    elif reply.animation: GROUP_FILTERS[chat_id][keyword] = {"type": "animation", "file_id": reply.animation.file_id, "caption": reply.caption.markdown if reply.caption else None}
    elif reply.document: GROUP_FILTERS[chat_id][keyword] = {"type": "document", "file_id": reply.document.file_id, "caption": reply.caption.markdown if reply.caption else None}
    await message.reply_text(f"✅ **ꜰɪʟᴛᴇʀ sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴀᴅᴅᴇᴅ ꜰᴏʀ ᴋᴇʏᴡᴏʀᴅ:** `{keyword}`")

@pr0fess0r_99.on_message(filters.group & filters.command("stopfilter"))
async def stop_filter_cmd(client: Client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id): return
    args = message.text.split(None, 1)
    if len(args) < 2:
        await message.reply_text("❌ **ᴘʟᴇᴀsᴇ sᴘᴇᴄɪꜰʏ ᴛʜᴇ ᴋᴇʏᴡᴏʀᴅ ᴛᴏ ʀᴇᴍᴏᴠᴇ!**")
        return
    keyword = args[1].lower().strip()
    chat_id = message.chat.id
    if chat_id in GROUP_FILTERS and keyword in GROUP_FILTERS[chat_id]:
        GROUP_FILTERS[chat_id].pop(keyword)
        await message.reply_text(f"✅ **ꜰɪʟᴛᴇʀ ꜰᴏʀ ᴋᴇʏᴡᴏʀᴅ** `{keyword}` **ʜᴀs ʙᴇᴇɴ sᴛᴏᴘᴘᴇᴅ.**")
    else: await message.reply_text(f"❌ **ɴᴏ ꜰɪʟᴛᴇʀ ꜰᴏᴜɴᴅ ꜰᴏʀ ᴋᴇʏᴡᴏʀᴅ:** `{keyword}`")

# --- Custom Welcome Configuration Commands ---
@pr0fess0r_99.on_message(filters.group & filters.command("setwelcome"))
async def set_welcome_cmd(client: Client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id): return
    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.reply_text("❌ **ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀɴ ɪᴍᴀɢᴇ ᴡɪᴛʜ ʏᴏᴜʀ ᴡᴇʟᴄᴏᴍᴇ ᴛᴇxᴛ!**")
        return
    if len(message.text.split()) < 2:
        await message.reply_text("❌ **ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴄᴀᴘᴛɪᴏɴ ᴛᴇxᴛ ᴀʟᴏɴɢ ᴡɪᴛʜ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ!**")
        return
    welcome_text = message.text.split(None, 1)[1]
    photo_id = message.reply_to_message.photo.file_id
    CUSTOM_WELCOME_TEXT[message.chat.id] = welcome_text
    CUSTOM_WELCOME_PHOTO[message.chat.id] = photo_id
    await message.reply_text("✅ **ᴄᴜsᴛᴏᴍ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇᴅɪᴀ ᴀɴᴅ ᴛᴇxᴛ sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴜᴘᴅᴀᴛᴇᴅ!**")

@pr0fess0r_99.on_message(filters.group & filters.command("welcomeremove"))
async def remove_welcome_cmd(client: Client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id): return
    chat_id = message.chat.id
    if chat_id in CUSTOM_WELCOME_TEXT or chat_id in CUSTOM_WELCOME_PHOTO:
        CUSTOM_WELCOME_TEXT.pop(chat_id, None)
        CUSTOM_WELCOME_PHOTO.pop(chat_id, None)
        await message.reply_text("✅ **ᴄᴜsᴛᴏᴍ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ ʀᴇᴍᴏᴠᴇᴅ. ʀᴇsᴇᴛ ᴛᴏ ᴅᴇꜰᴀᴜʟᴛ.**")
    else: await message.reply_text("❌ **ɴᴏ ᴄᴜsᴛᴏᴍ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ ꜰᴏᴜɴᴅ ᴛᴏ ʀᴇᴍᴏᴠᴇ.**")

# --- Auto Approve Toggle Command ---
@pr0fess0r_99.on_message(filters.group & filters.command("autoapprove"))
async def toggle_autoapprove(client: Client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id): return
    args = message.text.split()
    if len(args) < 2:
        current = AUTO_APPROVE_STATUS.get(message.chat.id, "on")
        await message.reply_text(f"ℹ️ ᴄᴜʀʀᴇnt ᴀᴜᴛᴏ ᴀᴘᴘʀᴏᴠᴀʟ sᴛᴀᴛᴜs ɪs: **{current.upper()}**")
        return
    action = args[1].lower()
    if action in ["on", "off"]:
        AUTO_APPROVE_STATUS[message.chat.id] = action
        await message.reply_text(f"✅ ᴀᴜᴛᴏ ᴀᴘᴘʀᴏᴠᴀʟ ᴛᴜʀɴᴇᴅ **{action.upper()}** ꜰᴏʀ ᴛʜɪs ɢʀᴏᴜᴘ.")

# --- Admin Core Management Commands ---
@pr0fess0r_99.on_message(filters.group & filters.command("kickme"))
async def kickme_cmd(client: Client, message: Message):
    try:
        if await is_admin(client, message.chat.id, message.from_user.id): return
        await message.chat.ban_member(message.from_user.id)
        await message.chat.unban_member(message.from_user.id)
    except Exception as e: await message.reply_text(f"ᴇʀʀᴏʀ: {e}")

@pr0fess0r_99.on_message(filters.group & filters.command(["ban", "dban", "sban", "tban"]))
async def ban_user(client: Client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id): return
    cmd = message.command[0]
    user_id, reason_or_time = await extract_user(client, message)
    if not user_id: return
    until_date = datetime.fromtimestamp(0)
    if cmd == "tban":
        until_date = parse_time(reason_or_time)
        if not until_date: return
    try:
        await message.chat.ban_member(user_id, until_date=until_date)
        if cmd == "dban" and message.reply_to_message: await message.reply_to_message.delete()
        if cmd == "sban":
            if message.reply_to_message: await message.reply_to_message.delete()
            await message.delete()
            return
    except Exception as e: await message.reply_text(f"ᴇʀʀᴏʀ: {e}")

@pr0fess0r_99.on_message(filters.group & filters.command("unban"))
async def unban_user(client: Client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id): return
    user_id, _ = await extract_user(client, message)
    if not user_id: return
    try: await message.chat.unban_member(user_id)
    except Exception as e: await message.reply_text(f"ᴇʀʀᴏʀ: {e}")

# --- Text Listener for Filters ---
@pr0fess0r_99.on_message(filters.group & filters.text & ~filters.command([]))
async def filter_listener(client: Client, message: Message):
    chat_id = message.chat.id
    text = message.text.lower().strip()
    if chat_id in GROUP_FILTERS and text in GROUP_FILTERS[chat_id]:
        filt = GROUP_FILTERS[chat_id][text]
        if filt["type"] == "text": await message.reply_text(filt["data"])
        elif filt["type"] == "photo": await message.reply_photo(photo=filt["file_id"], caption=filt["caption"])
        elif filt["type"] == "sticker": await message.reply_sticker(sticker=filt["file_id"])

# --- Chat Join Request Handler ---
@pr0fess0r_99.on_chat_join_request((filters.group | filters.channel) & filters.chat(CHAT_ID) if CHAT_ID else (filters.group | filters.channel))
async def join_handler(client: pr0fess0r_99, request: ChatJoinRequest):
    chat = request.chat 
    user = request.from_user 
    approvedbot = await client.get_me()
    current_mode = AUTO_APPROVE_STATUS.get(chat.id, "on")
    
    if current_mode == "on":
        await client.approve_chat_join_request(chat_id=chat.id, user_id=user.id)
        try:
            pm_caption = f"🎉 **ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ ʜᴀs ʙᴇᴇɴ ᴀᴄᴄᴇᴘᴛᴇᴅ ʙʏ @{approvedbot.username}!**"
            pm_button = [[InlineKeyboardButton("ᴛʀʏ ᴛᴏ sᴛᴀʀᴛ", url=f"t.me/{approvedbot.username}?start=true")]]
            await client.send_photo(chat_id=user.id, photo=ACCEPT_IMAGE_URL, caption=pm_caption, reply_markup=InlineKeyboardMarkup(pm_button))
        except UserPrivacyRestricted: pass
        try:
            if chat.id in CUSTOM_WELCOME_TEXT:
                raw_text = CUSTOM_WELCOME_TEXT[chat.id]
                members_count = await client.get_chat_members_count(chat.id)
                formatted_text = raw_text.format(username=f"@{user.username}" if user.username else user.first_name, mention=user.mention, name=f"{user.first_name} {user.last_name or ''}".strip(), userid=user.id, membercount=members_count, title=chat.title)
                await client.send_photo(chat_id=chat.id, photo=CUSTOM_WELCOME_PHOTO[chat.id], caption=formatted_text)
            else: await client.send_message(chat_id=chat.id, text=DEFAULT_WELCOME.format(mention=user.mention, title=chat.title))
        except Exception as e: print(f"Error group welcome: {e}")

# --- Callback Queries for Accept/Reject Buttons ---
@pr0fess0r_99.on_callback_query(filters.regex(r"^man_(acc|rej)_(\d+)_(-?\d+)"))
async def manual_decision_callback(client: Client, query: CallbackQuery):
    if not await is_admin(client, query.message.chat.id, query.from_user.id): return
    action, user_id, chat_id = query.data.split("_")[1:]
    user_id, chat_id = int(user_id), int(chat_id)
    try:
        user = await client.get_users(user_id)
        mention = user.mention
    except Exception: mention = f"ᴜsᴇʀ ({user_id})"
    if action == "acc":
        try:
            await client.approve_chat_join_request(chat_id=chat_id, user_id=user_id)
            if chat_id in CUSTOM_WELCOME_TEXT:
                raw_text = CUSTOM_WELCOME_TEXT[chat_id]
                members_count = await client.get_chat_members_count(chat_id)
                formatted_text = raw_text.format(username=f"@{user.username}" if user.username else user.first_name, mention=user.mention, name=f"{user.first_name} {user.last_name or ''}".strip(), userid=user.id, membercount=members_count, title=query.message.chat.title)
                await client.send_photo(chat_id=chat_id, photo=CUSTOM_WELCOME_PHOTO[chat_id], caption=formatted_text)
        except Exception as e: await query.message.edit_text(f"❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴀᴄᴄᴇᴘᴛ ᴜsᴇʀ: {e}")

# --- Callback Query for Bio Link Whitelist Button ---
@pr0fess0r_99.on_callback_query(filters.regex(r"^allow_bio_(\d+)"))
async def allow_bio_callback(client: Client, query: CallbackQuery):
    chat_id = query.message.chat.id
    clicker_id = query.from_user.id
    
    if not await is_admin(client, chat_id, clicker_id):
        await query.answer("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴄʟɪᴄᴋ ᴛʜɪs ʙᴜᴛᴛᴏɴ!", show_alert=True)
        return
        
    target_user_id = int(query.data.split("_")[2])
    
    if chat_id not in WHITELISTED_BIO_USERS:
        WHITELISTED_BIO_USERS[chat_id] = set()
        
    WHITELISTED_BIO_USERS[chat_id].add(target_user_id)
    
    try:
        target_user = await client.get_users(target_user_id)
        mention = target_user.mention
    except Exception:
        mention = f"ᴜsᴇʀ ({target_user_id})"
        
    await query.message.edit_text(f"✅ ᴀᴅᴍɪɴ {query.from_user.mention} ᴀʟʟᴏᴡᴇᴅ {mention} ᴛᴏ sᴇɴᴅ ᴍᴇssᴀɢᴇs ᴅᴇsᴘɪᴛᴇ ʜᴀᴠɪɴɢ ʟɪɴᴋs ɪɴ ᴛʜᴇɪʀ ʙɪᴏ.")

# --- PM Navigation & Interactive Helper Menus ---
@pr0fess0r_99.on_message(filters.private & filters.command(["start"]))
async def start(client: pr0fess0r_99, message: Message):
    # /start செய்யும் யூசர் ஐடியை மெமரியில் சேமிக்கிறது (பிராட்காஸ்ட்டிற்கு பயன்படும்)
    PM_USERS.add(message.from_user.id)
    
    approvedbot = await client.get_me() 
    button = [
        [InlineKeyboardButton("· ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ᴄʜᴀᴛ ·", url=f"http://t.me/{approvedbot.username}?startgroup=botstart")],
        [InlineKeyboardButton("· ᴀʙᴏᴜᴛ ·", callback_data="pm_about"), InlineKeyboardButton("· ɢʀᴏᴜᴘ ʜᴇʟᴘᴇʀ ·", callback_data="pm_helper")]
    ]
    caption_text = f"👋 **ʜᴇʟʟᴏ {message.from_user.mention}!**\n\n🤖 **ɪ ᴀᴍ ᴀɴ ᴀᴜᴛᴏ ᴀᴘᴘʀᴏᴠᴇʀ ᴊᴏɪɴ ʀᴇǫᴜᴇsᴛ ʙᴏᴛ.**"
    await client.send_photo(chat_id=message.chat.id, photo=START_IMAGE_URL, caption=caption_text, reply_markup=InlineKeyboardMarkup(button))

@pr0fess0r_99.on_callback_query(filters.regex(r"^pm_(start|about|helper|detail_(approval|bans|welcome|bio))"))
async def pm_menu_callbacks(client: Client, query: CallbackQuery):
    data = query.data
    approvedbot = await client.get_me()
    
    if data == "pm_start":
        button = [
            [InlineKeyboardButton("· ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ᴄʜᴀᴛ ·", url=f"http://t.me/{approvedbot.username}?startgroup=botstart")],
            [InlineKeyboardButton("· ᴀʙᴏᴜᴛ ·", callback_data="pm_about"), InlineKeyboardButton("· ɢʀᴏᴜᴘ ʜᴇʟᴘᴇʀ ·", callback_data="pm_helper")]
        ]
        caption_text = f"👋 **ʜᴇʟʟᴏ {query.from_user.mention}!**\n\n🤖 **ɪ ᴀᴍ ᴀɴ ᴀᴜᴛᴏ ᴀᴘᴘʀᴏᴠᴇʀ ᴊᴏɪɴ ʀᴇǫᴜᴇsᴛ ʙᴏᴛ.**"
        await query.message.edit_media(media={"type": "photo", "media": START_IMAGE_URL, "caption": caption_text}, reply_markup=InlineKeyboardMarkup(button))

    elif data == "pm_about":
        button = [[InlineKeyboardButton("· ʙᴀᴄᴋ ·", callback_data="pm_start")]]
        await query.message.edit_media(media={"type": "photo", "media": START_IMAGE_URL, "caption": ABOUT_TXT}, reply_markup=InlineKeyboardMarkup(button))

    elif data == "pm_helper":
        button = [
            [InlineKeyboardButton("· ᴀᴜᴛᴏ ᴀᴘᴘʀᴏᴠᴀʟ ·", callback_data="pm_detail_approval"), InlineKeyboardButton("· ʙᴀɴs ·", callback_data="pm_detail_bans")],
            [InlineKeyboardButton("· ᴡᴇʟᴄᴏᴍᴇ ·", callback_data="pm_detail_welcome"), InlineKeyboardButton("· ʙɪᴏ ʟɪɴᴋ ʀᴇᴍᴏᴠᴇ ·", callback_data="pm_detail_bio")],
            [InlineKeyboardButton("· ʙᴀᴄᴋ ·", callback_data="pm_start")]
        ]
        helper_caption = "🛠️ **ɢʀᴏᴜᴘ ʜᴇʟᴘᴇʀ ᴅᴀsʜʙᴏᴀʀ減ᴅ**\n\nᴘʟᴇᴀsᴇ sᴇʟᴇᴄᴛ ᴀ ᴄᴀᴛᴇɢᴏʀʏ ʙᴇʟᴏᴡ ᴛᴏ sᴇᴇ ʜᴏᴡ ᴛʜᴇ ʙᴏᴛ ᴍᴀɴᴀɢᴇs ʏᴏᴜʀ ᴄʜᴀᴛs ᴀɴᴅ ᴄʜᴀɴɴᴇʟs ᴇꜰꜰɪᴄɪᴇɴᴛʟʏ!"
        await query.message.edit_media(media={"type": "photo", "media": HELP_IMAGE_URL, "caption": helper_caption}, reply_markup=InlineKeyboardMarkup(button))

    else:
        sub_category = data.split("_")[2]
        back_button = [[InlineKeyboardButton("· ʙᴀᴄᴋ ·", callback_data="pm_helper")]]
        
        if sub_category == "approval":
            caption = "⚙️ **ᴀᴜᴛᴏ ᴀᴘᴘʀᴏᴠᴀʟ sʏsᴛᴇᴍ**\n\n• ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴀᴄᴄᴇᴘᴛs ᴊᴏɪɴ ʀᴇǫᴜᴇsᴛs ꜰᴏʀ ɢʀᴏᴜᴘs/ᴄʜᴀɴɴᴇʟs.\n• sᴇɴᴅs ᴀ ᴘʀɪᴠᴀᴛᴇ ᴡᴇʟᴄᴏᴍᴇ ᴘʜᴏᴛᴏ ᴛᴏ ᴛʜᴇ ᴜsᴇʀ.\n• **...:** `/autoapprove on/off` (ᴀᴅᴍɪɴs ᴏɴʟʏ)."
        elif sub_category == "bans":
            caption = "🚫 **ʙᴀɴ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ**\n\n• `/ban` - ᴘᴇʀᴍᴀɴᴇɴᴛ ʙᴀɴ.\n• `/dban` - ʙᴀɴ & ᴅᴇʟᴇᴛᴇ ʀᴇᴘʟɪᴇᴅ ᴍsɢ.\n• `/sban` - sɪʟᴇɴᴛ ʙᴀɴ.\n• `/tban <time>` - ᴛᴇᴍᴘᴏʀᴀʀʏ ʙᴀɴ (ᴇ.ɢ., `1h`, `1d`)."
        elif sub_category == "welcome":
            caption = "🖼️ **ᴄᴜsᴛᴏᴍ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs**\n\n• ɢʀᴇᴇᴛ ɴᴇᴡ ᴍᴇᴍʙᴇʀs ᴡɪᴛʜ ᴍᴇᴅɪᴀ.\n• `/setwelcome <text>` - ʀᴇᴘʟʏ ᴛᴏ ɪᴍᴀɢᴇ ᴛᴏ sᴇᴛ.\n• `/welcomeremove` - ʀᴇsᴇᴛ ᴛᴏ ᴅᴇꜰᴀᴜʟᴛ sᴇᴛᴛɪŋɢs."
        elif sub_category == "bio":
            caption = "⚠️ **ʙɪᴏ ʟɪɴᴋ ʀᴇᴍᴏᴠᴇ ᴘʀᴏᴛᴇᴄᴛᴏʀ**\n\n• ᴅᴇʟᴇᴛᴇs ᴍᴇssᴀɢᴇs ɪꜰ ᴀ ᴜsᴇʀ ʜᴀs ʟɪɴᴋs ᴏʀ ᴏᴛʜᴇʀ ᴜsᴇʀɴᴀᴍᴇs ɪɴ ᴛʜᴇɪʀ ʙɪᴏ.\n• ᴀʟʟᴏᴡs ᴛʜᴇɪʀ ᴏᴡɴ `@username`.\n• ᴀʜᴍɪɴs ᴄᴀɴ ᴄʟɪᴄᴋ `✅ ᴀʟʟᴏᴡᴇᴅ ᴍsɢ ɢʀᴏᴜᴘ` ᴛᴏ ᴡʜɪᴛᴇʟɪsᴛ."

        await query.message.edit_media(media={"type": "photo", "media": HELP_IMAGE_URL, "caption": caption}, reply_markup=InlineKeyboardMarkup(back_button))

print("Auto Approved Bot Running with Owner Broadcast Support...")
pr0fess0r_99.run()
