import asyncio
import inspect
import math
import os.path
import re
from datetime import datetime, timedelta
from functools import partial, wraps
from string import Formatter
from pyrogram.enums import ParseMode
from typing import Callable, List, Optional, Union

from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message, User

from megumin import megux, Config
from megumin.utils import get_collection, check_rights, tld, disableable_dec
from megumin.utils.decorators import input_str

BTN_URL_REGEX = re.compile(r"(\[([^\[]+?)\]\(buttonurl:(?:/{0,2})(.+?)(:same)?\))")

SMART_OPEN = "“"
SMART_CLOSE = "”"
START_CHAR = ("'", '"', SMART_OPEN)

RESTRICTED_SYMBOLS_IN_NOTENAMES = [
    ':', '**', '__', '`', '#', '"', '[', ']', "'", '$', '||']


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




@megux.on_message(filters.command(["save", "savenote", "note"], Config.TRIGGER))
@disableable_dec("save")
async def save_notes(c: megux, m: Message):
    chat_id = m.chat.id
    user_id = m.from_user.id
    if not await check_rights(chat_id, user_id, "can_change_info"):
        return await m.reply(await tld(m.chat.id, "NOTES_NO_PERM"), quote=True)
    if m.reply_to_message is None and len(input_str(m)) < 2:
        await m.reply_text(await tld(m.chat.id, "NOTES_NOT_NAME"), quote=True)
        return
    db = get_collection(f"CHAT_NOTES {m.chat.id}")
    args = m.text.html.split(maxsplit=1)
    split_text = f"{args[1]}"
    trigger = split_text.lower()
    if trigger[0] == '#':
        trigger = trigger[1:]
        
    sym = None
    if any((sym := s) in trigger for s in RESTRICTED_SYMBOLS_IN_NOTENAMES):
        await m.reply("O nome da nota não deve ter o caractere {}".format(sym))
        return

    
    if m.reply_to_message and m.reply_to_message.photo:
        file_id = m.reply_to_message.photo.file_id
        raw_data = (
            m.reply_to_message.caption.html
            if m.reply_to_message.caption is not None
            else None
        )
        note_type = "photo"
    elif m.reply_to_message and m.reply_to_message.document:
        file_id = m.reply_to_message.document.file_id
        raw_data = (
            m.reply_to_message.caption.html
            if m.reply_to_message.caption is not None
            else None
        )
        note_type = "document"
    elif m.reply_to_message and m.reply_to_message.video:
        file_id = m.reply_to_message.video.file_id
        raw_data = (
            m.reply_to_message.caption.html
            if m.reply_to_message.caption is not None
            else None
        )
        note_type = "video"
    elif m.reply_to_message and m.reply_to_message.audio:
        file_id = m.reply_to_message.audio.file_id
        raw_data = (
            m.reply_to_message.caption.html
            if m.reply_to_message.caption is not None
            else None
        )
        note_type = "audio"
    elif m.reply_to_message and m.reply_to_message.voice:
        file_id = m.reply_to_message.voice.file_id
        raw_data = (
            m.reply_to_message.caption.html
            if m.reply_to_message.caption is not None
            else None
        )
        note_type = "voice"
    elif m.reply_to_message and m.reply_to_message.animation:
        file_id = m.reply_to_message.animation.file_id
        raw_data = (
            m.reply_to_message.caption.html
            if m.reply_to_message.caption is not None
            else None
        )
        note_type = "animation"
    elif m.reply_to_message and m.reply_to_message.sticker:
        file_id = m.reply_to_message.sticker.file_id
        raw_data = split_text[1] if len(split_text) > 1 else None
        note_type = "sticker"
    else:
        if m.reply_to_message and m.reply_to_message.text:
            file_id = None
            raw_data = m.reply_to_message.text
            note_type = "text"
        else:
            await m.reply(await tld(m.chat.id, "NOTES_NO_REPLY"))
            return

    check_note = await db.find_one({"name": trigger})
    if check_note:
        await db.delete_one({"chat_id": chat_id, "name": trigger})
        await db.insert_one({"chat_id": chat_id, "name": trigger, "raw_data": raw_data, "file_id": file_id, "type": note_type})
    else:
        await db.insert_one({"chat_id": chat_id, "name": trigger, "raw_data": raw_data, "file_id": file_id, "type": note_type})
    await m.reply((await tld(m.chat.id, "NOTES_SAVED")).format(trigger))


@megux.on_message(filters.command("notes", Config.TRIGGER) & filters.group)
@disableable_dec("notes")
async def get_all_chat_note(c: megux, m: Message):
    db = get_collection(f"CHAT_NOTES {m.chat.id}")
    chat_id = m.chat.id
    reply_text = (await tld(m.chat.id, "NOTES_LIST")).format(m.chat.title)
    all_notes = db.find()          
    async for note_s in all_notes:
        keyword = note_s["name"]
        reply_text += f" - <code>#{keyword}</code> \n"
    if not await db.find_one():
        await m.reply_text(await tld(m.chat.id, "NOTES_NOT_FOUND"), quote=True)
    else:
        reply_text += await tld(m.chat.id, "NOTES_SUB_LIST")
        await m.reply_text(reply_text, quote=True)
        
        
@megux.on_message(filters.command(["rmnote", "delnote"]))
@disableable_dec("delnote")
async def rmnote(c: megux, m: Message):
    args = m.text.html.split(maxsplit=1)
    trigger = args[1].lower()
    chat_id = m.chat.id
    db = get_collection(f"CHAT_NOTES {chat_id}")
    check_note = await db.find_one({"chat_id": chat_id, "name": trigger})
    if check_note:
        await db.delete_one({"chat_id": chat_id, "name": trigger})
        await m.reply_text(
            (await tld(m.chat.id, "NOTES_REMOVED")).format(trigger), quote=True
        )
    else:
        await m.reply_text(
            (await tld(m.chat.id, "NOTES_REMOVE_NOT_FOUND")).format(trigger), quote=True
        )

        
@megux.on_message(filters.command(["resetnotes", "clearnotes"]))
@disableable_dec("resetnotes")
async def clear_notes(c: megux, m: Message):
    chat_id = m.chat.id
    db = get_collection(f"CHAT_NOTES {chat_id}")
    check_note = await db.find_one()
    if check_note:
        await db.drop()
        await m.reply_text(
            "Todas as notas desse chat foram apagadas.", quote=True
        )
    else:
        await m.reply_text(
            "O grupo não tem notas.", quote=True
        )        

async def serve_note(c: megux, m: Message, txt):
    chat_id = m.chat.id
    db = get_collection(f"CHAT_NOTES {m.chat.id}")
    text = txt

    all_notes = db.find()
    async for note_s in all_notes:
        keyword = note_s["name"]
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, text, flags=re.IGNORECASE):
            data, button = button_parser(note_s["raw_data"])
            if note_s["type"] == "text":
                await m.reply_text(
                    data,
                    quote=True,
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup(button)
                    if len(button) != 0
                    else None,
                )
            elif note_s["type"] == "photo":
                await m.reply_photo(
                    note_s["file_id"],
                    quote=True,
                    caption=data if not None else None,
                    reply_markup=InlineKeyboardMarkup(button)
                    if len(button) != 0
                    else None,
                )
            elif note_s["type"] == "document":
                await m.reply_document(
                    note_s["file_id"],
                    quote=True,
                    caption=data if not None else None,
                    reply_markup=InlineKeyboardMarkup(button)
                    if len(button) != 0
                    else None,
                )
            elif note_s["type"] == "video":
                await m.reply_video(
                    note_s["file_id"],
                    quote=True,
                    caption=data if not None else None,
                    reply_markup=InlineKeyboardMarkup(button)
                    if len(button) != 0
                    else None,
                )
            elif note_s["type"] == "audio":
                await m.reply_audio(
                    note_s["file_id"],
                    quote=True,
                    caption=data if not None else None,
                    reply_markup=InlineKeyboardMarkup(button)
                    if len(button) != 0
                    else None,
                )
            elif note_s["type"] == "voice":
                await m.reply_voice(
                    note_s["file_id"],
                    quote=True,
                    caption=data if not None else None,
                    reply_markup=InlineKeyboardMarkup(button)
                    if len(button) != 0
                    else None,
                )
            elif note_s["type"] == "animation":
                await m.reply_animation(
                    note_s["file_id"],
                    quote=True,
                    caption=data if not None else None,
                    reply_markup=InlineKeyboardMarkup(button)
                    if len(button) != 0
                    else None,
                )
            elif note_s["type"] == "sticker":
                await m.reply_sticker(
                    note_s["file_id"],
                    quote=True,
                    reply_markup=InlineKeyboardMarkup(button)
                    if len(button) != 0
                    else None,
                )
                
                
@megux.on_message(filters.command("get") & filters.group)
async def note_by_get_command(c: megux, m: Message):
    note_data = " ".join(m.command[1:])
    targeted_message = m.reply_to_message or m
    await serve_note(c, targeted_message, txt=note_data)

    
@megux.on_message(filters.regex(r"^#[^\s]+") & filters.group)
async def note_by_hashtag(c: megux, m: Message):
    note_data = m.text[1:]
    targeted_message = m.reply_to_message or m
    await serve_note(c, targeted_message, txt=note_data)
