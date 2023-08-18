import asyncio
import re
import math
import inspect
import os.path

from pyrogram import filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from pyrogram.enums import ParseMode

from datetime import datetime, timedelta
from functools import partial, wraps
from string import Formatter
from typing import Callable, List, Optional, Union


from megumin import megux, Config
from megumin.utils import get_collection, check_rights, check_bot_rights, is_admin, add_user_count, check_ban, check_antispam, find_user, add_user



BTN_URL_REGEX = re.compile(r"(\[([^\[]+?)\]\(buttonurl:(?:/{0,2})(.+?)(:same)?\))")

def get_format_keys(string: str) -> List[str]:
    """Return a list of formatting keys present in string."""
    return [i[1] for i in Formatter().parse(string) if i[1] is not None]


def button_parser(markdown_note):
    note_data = ""
    buttons = []
    if markdown_note is None:
        return note_data, buttons
    if markdown_note.startswith("/") or markdown_note.startswith("!"):
        args = markdown_note.split(None, 2)
        markdown_note = args[2]
    prev = 0
    for match in BTN_URL_REGEX.finditer(markdown_note):
        n_escapes = 0
        to_check = match.start(1) - 1
        while to_check > 0 and markdown_note[to_check] == "\\":
            n_escapes += 1
            to_check -= 1

        if n_escapes % 2 == 0:
            if bool(match.group(4)) and buttons:
                buttons[-1].append(
                    InlineKeyboardButton(text=match.group(2), url=match.group(3))
                )
            else:
                buttons.append(
                    [InlineKeyboardButton(text=match.group(2), url=match.group(3))]
                )
            note_data += markdown_note[prev : match.start(1)]
            prev = match.end(1)

        else:
            note_data += markdown_note[prev:to_check]
            prev = match.start(1) - 1

    note_data += markdown_note[prev:]

    return note_data, buttons


@megux.on_message(filters.command("setwelcome", Config.TRIGGER))
async def set_welcome_message(c: megux, m: Message):
    if not await find_user(m.from_user.id):
        await add_user(m.from_user.id)
    db = get_collection(f"WELCOME_CHAT")
    if not await check_rights(m.chat.id, m.from_user.id, "can_change_info"):
        return
   
    if len(m.text.split()) > 1:
        message = m.text.html.split(None, 1)[1]
        try:
            # Try to send message with default parameters
            sent = await m.reply_text(
                message.format(
                    id=m.from_user.id,
                    username=m.from_user.username,
                    mention=m.from_user.mention,
                    first_name=m.from_user.first_name,
                    first=m.from_user.first_name,
                    # full_name and name are the same
                    full_name=m.from_user.first_name,
                    name=m.from_user.first_name,
                    # title and chat_title are the same
                    title=m.chat.title,
                    chat_title=m.chat.title,
                    count=(await c.get_chat_members_count(m.chat.id)),
                )
            )
            await asyncio.sleep(0.7)
        except (KeyError, BadRequest) as e:
            await m.reply_text(
                "<b>Erro:</b> {error}".format(
                    error=e.__class__.__name__ + ": " + str(e)
                )
            )
        else:
            await db.update_one({"chat_id": m.chat.id}, {"$set": {"msg": message}}, upsert=True)
            await sent.edit_text(
                "Boas Vindas Alterada em {chat_title}".format(chat_title=m.chat.title)
            )
    else:
        await m.reply_text(
            "De um argumento exemplo: /setwelcome Olá {mention}",
            disable_web_page_preview=True,
        )

@megux.on_message(filters.command(["welcome on", "welcome true"], Config.TRIGGER) & filters.group)
async def enable_welcome_message(c: megux, m: Message):
    if not await find_user(m.from_user.id):
        await add_user(m.from_user.id)
    db = get_collection(f"WELCOME_STATUS")
    if not await check_rights(m.chat.id, m.from_user.id, "can_change_info"):
        return
    await db.update_one({"chat_id": m.chat.id}, {"$set": {"status": True}}, upsert=True)
    await m.reply_text("Boas Vindas agora está Ativadas.")
    
    
@megux.on_message(filters.command(["welcome off", "welcome false"], Config.TRIGGER) & filters.group)
async def enable_welcome_message(c: megux, m: Message):
    if not await find_user(m.from_user.id):
        await add_user(m.from_user.id)
    db = get_collection(f"WELCOME_STATUS")
    if not await check_rights(m.chat.id, m.from_user.id, "can_change_info"):
        return
    await db.update_one({"chat_id": m.chat.id}, {"$set": {"status": False}}, upsert=True)
    await m.reply_text("Boas Vindas agora está Desativadas.")
    
    
@megux.on_message(filters.command("welcome", Config.TRIGGER) & filters.group)
async def enable_welcome_message(c: megux, m: Message):
    if not await find_user(m.from_user.id):
        await add_user(m.from_user.id)
    if not await check_rights(m.chat.id, m.from_user.id, "can_change_info"):
        return
    await m.reply_text("Dê um argumento exemplo: /welcome on/off/true/false")
 

@megux.on_message(filters.new_chat_members & filters.group)
async def greet_new_members(c: megux, m: Message):
    db = get_collection(f"WELCOME_CHAT")
    db_ = get_collection(f"WELCOME_STATUS")
    captcha = get_collection(f"CAPTCHA")
    members = m.new_chat_members
    chat_title = m.chat.title
    first_name = ", ".join(map(lambda a: a.first_name, members))
    full_name = ", ".join(
        map(lambda a: a.first_name + " " + (a.last_name or ""), members)
    )
    user_id = ", ".join(map(lambda a: str(a.id), members))
    username = ", ".join(
        map(lambda a: "@" + a.username if a.username else a.mention, members)
    )
    
    #Check if is GBANNED
    if await check_antispam(m.chat.id):
        await check_ban(m, m.chat.id, user_id)
        
    mention = ", ".join(map(lambda a: a.mention, members))
    await add_user_count(m.chat.id, user_id)
    dbu = get_collection(f"TOTAL_GROUPS {user_id}")
    await dbu.drop()
    if not m.from_user.is_bot:
        welcome_enabled = await db_.find_one({"chat_id": m.chat.id, "status": True})
        welcome_pack = await db.find_one({"chat_id": m.chat.id})
        captcha_pack = await captcha.find_one({"chat_id": m.chat.id})
        if welcome_enabled:
            if not welcome_pack:
                welcome = "Hey {first_name}, how are you?"
            else:
                welcome = welcome_pack["msg"]
            if "count" in get_format_keys(welcome):
                count = await c.get_chat_members_count(m.chat.id)
            else:
                count = 0

            welcome = welcome.format(
                id=user_id,
                username=username,
                mention=mention,
                first_name=first_name,
                first=first_name,
                # full_name and name are the same
                full_name=full_name,
                name=full_name,
                # title and chat_title are the same
                title=chat_title,
                chat_title=chat_title,
                count=count,
            )

            if not await find_user(m.from_user.id):
                await add_user(m.from_user.id)
            
            welcome, welcome_buttons = button_parser(welcome)
            if await captcha.find_one({"chat_id": m.chat.id, "status": True}):
                if await is_admin(m.chat.id, user_id):
                    #send message for admin 
                    await m.reply_text(
                        welcome,
                        disable_web_page_preview=True,
                        reply_markup=(
                            InlineKeyboardMarkup(welcome_buttons)
                            if len(welcome_buttons) != 0
                            else None
                        ),
                    )
                    return
                if await check_bot_rights(m.chat.id, "can_restrict_members"):
                    welcome_buttons += [[InlineKeyboardButton("Clique aqui para ser desmutado", callback_data=f"cptcha|{user_id}")]]
                    try:
                        await megux.restrict_chat_member(m.chat.id, user_id, ChatPermissions())
                    except Exception as e:
                        await m.reply("Não foi possivel mutar o usúario devido a: {}".format(e))
            #send message
            await m.reply_text(
                welcome,
                disable_web_page_preview=True,
                reply_markup=(
                    InlineKeyboardMarkup(welcome_buttons)
                    if len(welcome_buttons) != 0
                    else None
                ),
            )

    
@megux.on_message(filters.command("getwelcome", Config.TRIGGER))
async def get_welcome(c: megux, m: Message):
    if not await find_user(m.from_user.id):
        await add_user(m.from_user.id)
    db = get_collection(f"WELCOME_CHAT")
    resp = await db.find_one({"chat_id": m.chat.id})
    if resp:
        welcome = resp["msg"]
    else:
        welcome = "Hey {first}, how are you?"
        
    await m.reply(welcome)

    
@megux.on_message(filters.command("resetwelcome", Config.TRIGGER))
async def rm_welcome(c: megux, m: Message):
    if not await find_user(m.from_user.id):
        await add_user(m.from_user.id)
    db = get_collection(f"WELCOME_CHAT")
    r = await db.find_one()
    if r:
        message = r["msg"]
        await db.delete_one({"chat_id": m.chat.id, "msg": message})
        await m.reply("A mensagem de boas vindas foi resetada!") 
    else:
        return await m.reply("Nenhuma mensagem de boas vindas foi definida.")

    
@megux.on_callback_query(filters.regex(pattern=r"^cptcha\|(.*)"))
async def warn_rules(client: megux, cb: CallbackQuery):
    try:
        data, userid = cb.data.split("|")
    except ValueError:
        return print(cb.data)
    db = get_collection(f"WELCOME_CHAT")
    if cb.from_user.id != int(userid):
        await cb.answer("Isso não é para você!")
        return
    if await is_admin(cb.message.chat.id, userid):
        await cb.answer("Você não precisa mais compretar o captcha já que és administrador.")
        return
    response = await db.find_one({"chat_id": cb.message.chat.id})
    if response:
        msg = response["msg"]
    else:
        msg = "Hey {first}, How are you?"
    if "count" in get_format_keys(msg):
        count = await client.get_chat_members_count(cb.message.chat.id)
    else:
        count = 0

    first = cb.from_user.first_name
    mention = cb.from_user.mention
    user_id = cb.from_user.id
    chat_title = cb.message.chat.title
    full_name = cb.from_user.first_name + " " + cb.from_user.last_name if cb.from_user.last_name else cb.from_user.first_name
    username = "@" + cb.from_user.username if cb.from_user.username else cb.from_user.mention
    try:
        msg = msg.format(
            id=user_id,
            username=username,
            mention=mention,
            first_name=first,
            first=first,
            # full_name and name are the same
            full_name=full_name,
            name=full_name,
            # title and chat_title are the same
            title=chat_title,
            chat_title=chat_title,
            count=count,
        )
    except (KeyError, BadRequest) as e:
        await cb.message.edit_text(
            "<b>Erro:</b> {error}".format(
                error=e.__class__.__name__ + ": " + str(e)
            )
        )
    captcha_welcome, buttons = button_parser(msg)
    try:
        await client.unban_chat_member(cb.message.chat.id, userid)
        await cb.answer("Parabéns você completou o captcha, Agora você pode falar no chat!", show_alert=True)
        await cb.message.edit_text(
            captcha_welcome,
            disable_web_page_preview=True,
            reply_markup=(
                InlineKeyboardMarkup(buttons)
                if len(buttons) != 0
                else None
            ),
        )
    except Exception as e:
        return await cb.answer("Não foi possivel completar o captcha devido a: {}".format(e))

    
@megux.on_message(filters.command("captcha on", Config.TRIGGER) & filters.group)
async def enable_welcome_message(c: megux, m: Message):
    db = get_collection(f"CAPTCHA")
    if not await check_rights(m.chat.id, m.from_user.id, "can_change_info"):
        return
    r = await db.find_one({"chat_id": m.chat.id})
    if r:
        await db.update_one({"chat_id": m.chat.id}, {"$set": {"status": True}}, upsert=True)
    else: 
        await db.update_one({"chat_id": m.chat.id}, {"$set": {"status": True}}, upsert=True)
    await m.reply_text("Captcha agora está Ativado.")

    
@megux.on_message(filters.command("captcha off", Config.TRIGGER) & filters.group)
async def enable_welcome_message(c: megux, m: Message):
    db = get_collection(f"CAPTCHA")
    if not await check_rights(m.chat.id, m.from_user.id, "can_change_info"):
        return
    r = await db.find_one({"chat_id": m.chat.id})
    if r:
        await db.update_one({"chat_id": m.chat.id}, {"$set": {"status": False}}, upsert=True)
    else: 
        await db.update_one({"chat_id": m.chat.id}, {"$set": {"status": False}}, upsert=True)
    await m.reply_text("Captcha agora está Desativado.")
    

@megux.on_message(filters.command("captcha", Config.TRIGGER) & filters.group)
async def enable_welcome_message(c: megux, m: Message):
    if not await check_rights(m.chat.id, m.from_user.id, "can_change_info"):
        return
    await m.reply_text("Dê um argumento exemplo: /captcha on/off")
 
