import asyncio
from pyrogram import filters
from pyrogram.errors import PeerIdInvalid, UserIdInvalid, UsernameInvalid
from pyrogram.types import Message

from megumin import megux, Config
from megumin.utils import check_rights, get_collection, is_dev, tld, gban_user, ungban_user

@megux.on_message(filters.command(["antispam on", "antispam true"], Config.TRIGGER) & filters.group)
async def enable_antispam_message(c: megux, m: Message):
    db = get_collection("ANTISPAM_CHATS")
    if not await check_rights(m.chat.id, m.from_user.id, "can_change_info"):
        return
    await db.update_one({"chat_id": m.chat.id}, {"$set": {"status": True}}, upsert=True)
    await m.reply_text("Antispam Ativado.")
    
    
@megux.on_message(filters.command(["antispam off", "antispam false"], Config.TRIGGER) & filters.group)
async def disable_antispam_message(c: megux, m: Message):
    db = get_collection("ANTISPAM_CHATS")
    if not await check_rights(m.chat.id, m.from_user.id, "can_change_info"):
        return
    await db.update_one({"chat_id": m.chat.id}, {"$set": {"status": False}}, upsert=True)
    await m.reply_text("Antispam Desativado.")
    
    
@megux.on_message(filters.command("antispam", Config.TRIGGER) & filters.group)
async def enable_welcome_message(c: megux, m: Message):
    if not await check_rights(m.chat.id, m.from_user.id, "can_change_info"):
        return
    await m.reply_text("Dê um argumento exemplo: /antispam on/off/true/false")


@megux.on_message(filters.command("gban", prefixes=["/", "!"]))
async def _gban_user(_, message: Message):
    if not is_dev(message.from_user.id):
        return
    chat_id = message.chat.id
    
    cmd = len(message.text)
    replied = message.reply_to_message
    reason = ""
    if replied:
        id_ = replied.from_user.id
        if cmd > 6:
            _, reason = message.text.split(maxsplit=1)
    elif cmd > 6:
        _, args = message.text.split(maxsplit=1)
        if " " in args:
            id_, reason = args.split(" ", maxsplit=1)
        else:
            id_ = args
    else:
        await message.reply(await tld(chat_id, "BANS_NOT_ESPECIFIED_USER"))
        return
    try:
        user = await megux.get_users(id_)
        user_id = user.id
        mention = user.mention
    except (UsernameInvalid, PeerIdInvalid, UserIdInvalid):
        await message.reply(
            await tld(message.chat.id, "BANS_ID_INVALID")
        )
        return
    
    sudo_name = message.from_user.mention
    try:
        await gban_user(message, user_id, mention, sudo_name, reason or None) 
    except Exception as e_f:
        await message.reply(f"`A error occurred 🤔`\n\n**ERROR:** `{e_f}`")


@megux.on_message(filters.command("ungban", prefixes=["/", "!"]))
async def _ungban_user(_, message: Message):
    if not is_dev(message.from_user.id):
        return
    chat_id = message.chat.id
    
    cmd = len(message.text)
    replied = message.reply_to_message
    reason = ""
    if replied:
        id_ = replied.from_user.id
        if cmd > 7:
            _, reason = message.text.split(maxsplit=1)
    elif cmd > 7:
        _, args = message.text.split(maxsplit=1)
        if " " in args:
            id_, reason = args.split(" ", maxsplit=1)
        else:
            id_ = args
    else:
        await message.reply(await tld(chat_id, "BANS_NOT_ESPECIFIED_USER"))
        return
    try:
        user = await megux.get_users(id_)
        user_id = user.id
        mention = user.mention
    except (UsernameInvalid, PeerIdInvalid, UserIdInvalid):
        await message.reply(
            await tld(message.chat.id, "BANS_ID_INVALID")
        )
        return
    
    sudo_name = message.from_user.mention
    try:
        await ungban_user(message, user_id, mention, sudo_name, reason or None) 
    except Exception as e_f:
        await message.reply(f"`A error occurred 🤔`\n\n**ERROR:** `{e_f}`")

