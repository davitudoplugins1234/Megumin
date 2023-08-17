import re
import asyncio 

from pyrogram import filters
from pyrogram.enums import MessageEntityType
from pyrogram.errors import FloodWait, UserNotParticipant, BadRequest, ChatWriteForbidden
from pyrogram.types import Message 

from megumin import megux, Config
from megumin.utils import get_collection, get_string, check_afk, find_user, add_user  
from megumin.utils.decorators import input_str



@megux.on_message(filters.command("afk", Config.TRIGGER))
@megux.on_message(filters.regex(r"^(?i)brb(\s(?P<args>.+))?"))
async def afk_cmd(_, m: Message):
    if not await find_user(m.from_user.id):
        await add_user(m.from_user.id)
        
    x = input_str(m)
    REASON = get_collection("REASON_AFK")
    AFK_STATUS = get_collection("_AFK")
    AFK_COUNT = get_collection("AFK_COUNT")
    if input_str(m):
        await AFK_COUNT.delete_one({"mention_": m.from_user.mention()})
        await AFK_STATUS.delete_one({"user_id": m.from_user.id, "_afk": "on"})
        await REASON.delete_one({"user_id": m.from_user.id}) 
        await AFK_COUNT.insert_one({"mention_": m.from_user.mention()})
        await AFK_STATUS.insert_one({"user_id": m.from_user.id, "_afk": "on"})
        await REASON.insert_one({"user_id": m.from_user.id, "_reason": x})
        res = await REASON.find_one({"user_id": m.from_user.id})
        r = res["_reason"]     
        await m.reply((await get_string(m.chat.id, "AFK_IS_NOW_REASON")).format(m.from_user.first_name, r))
        await m.stop_propagation()
    else:
        try:
            await AFK_STATUS.delete_one({"user_id": m.from_user.id, "status": "on"})
            await REASON.delete_one({"user_id": m.from_user.id}) 
            await AFK_COUNT.delete_one({"mention_": m.from_user.mention()})
            await AFK_COUNT.insert_one({"mention_": m.from_user.mention()})
            await AFK_STATUS.insert_one({"user_id": m.from_user.id, "_afk": "on"})
            await m.reply((await get_string(m.chat.id, "AFK_IS_NOW")).format(m.from_user.first_name))
        except AttributeError as err: 
            await megux.send_log(err)
            return
        except Exception as e:
            await megux.send_log(e)
            return     
        await m.stop_propagation()

@megux.on_message(~filters.private & ~filters.bot & filters.all, group=1)
async def rem_afk(c: megux, m: Message):
    if m.sender_chat:
        return
    user = m.from_user
    AFK_STATUS = get_collection("_AFK")
    AFK_COUNT = get_collection("AFK_COUNT")
    
    try:
        if m.text:
            if m.text.startswith(("brb", "/afk")):
                return
    except AttributeError:
        return

    if user and await AFK_STATUS.find_one({"user_id": user.id, "_afk": "on"}):
        await AFK_STATUS.delete_one({"user_id": user.id, "_afk": "on"})
        await AFK_COUNT.delete_one({"mention_": m.from_user.mention()})
        try:
            return await m.reply_text(
                (await get_string(m.chat.id, "AFK_LOOGER")).format(user.first_name)
            )
        except ChatWriteForbidden:
            return

    elif m.reply_to_message and m.reply_to_message.from_user:
        await check_afk(
            m,
            m.reply_to_message.from_user.id,
            m.reply_to_message.from_user.first_name,
            user,
        )

    elif m.entities:
        for y in m.entities:
            if y.type == MessageEntityType.MENTION:
                try:
                    ent = await c.get_users(m.text[y.offset : y.offset + y.length])
                except (IndexError, KeyError, BadRequest):
                    return
                except FloodWait as e:
                    await asyncio.sleep(e.value)

            elif y.type == MessageEntityType.TEXT_MENTION:
                try:
                    ent = y.user
                except UnboundLocalError:
                    return
            else:
                return

            return await check_afk(m, ent.id, ent.first_name, user)
