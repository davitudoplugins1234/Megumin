from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatType
from pyrogram.errors import PeerIdInvalid

from megumin import megux, Config 
from megumin.utils import check_bot_rights, check_rights, get_string, get_collection, is_disabled, disableable_dec 
from megumin.utils.decorators import input_str 


@megux.on_message(filters.command("pin", Config.TRIGGER))
@disableable_dec("pin")
async def pin_msg(c: megux, m: Message):
    LOGS = get_collection(f"LOGS {m.chat.id}")
    input_ = input_str(m).split()
    if await is_disabled(m.chat.id, "pin"):
        return
    reply = m.reply_to_message
    gid = m.chat.id
    silent = bool()
    mode = ""
    if not await check_rights(gid, m.from_user.id, "can_pin_messages"):
        return await m.reply(await get_string(m.chat.id, "NO_PIN_USER"))
    if not await check_rights(gid, c.me.id, "can_pin_messages"):
        return await m.reply(await get_string(m.chat.id, "NO_PIN_BOT"))
    if not reply:
        return await m.reply(await get_string(m.chat.id, "PIN_NO_REPLY"))
    msg_id = reply.id
    chat = str(f"{gid}").replace("-100", "")
    link = f"https://t.me/c/{chat}/{reply.id}"
    string = await get_string(m.chat.id, "PIN_SUCCESS")
    if input_:
        if input_ in ("silent", "s"):
            silent += True
            mode += await get_string(m.chat.id, "PIN_SILENT_ON")
        elif input_ in ("notify", "loud"):
            silent += False 
            mode += await get_string(m.chat.id, "PIN_SILENT_OFF")
        else:
            silent += True
            mode += await get_string(m.chat.id, "PIN_SILENT_ON")
    try:
        await megux.pin_chat_message(gid, msg_id, disable_notification=silent)
        await m.reply(string.format(link))
        data = await LOGS.find_one()
        if data:
            id = data["log_id"]
            id_log = int(id)
            try:
                return await megux.send_message(id_log, (await get_string(gid, "PIN_LOGGER")).format(m.chat.title, m.from_user.mention(), m.from_user.id, link, mode))
            except PeerIdInvalid:
                return
    except Exception as e:
        await megux.send_log(e)


@megux.on_message(filters.command("unpin", Config.TRIGGER))
@disableable_dec("unpin")
async def pin_msg(c: megux, m: Message):
    LOGS = get_collection(f"LOGS {m.chat.id}")
    input_ = input_str(m).split()
    if await is_disabled(m.chat.id, "unpin"):
        return
    reply = m.reply_to_message
    gid = m.chat.id
    if not await check_rights(gid, m.from_user.id, "can_pin_messages"):
        return await m.reply(await get_string(m.chat.id, "NO_PIN_USER"))
    if not await check_rights(gid, c.me.id, "can_pin_messages"):
        return await m.reply(await get_string(m.chat.id, "NO_PIN_BOT"))
    if input_:
        if "all" in input_:
            try:
                await m.reply(await get_string(m.chat.id, "UNPIN_ALL_SUCCESS"))
                return await megux.unpin_all_chat_messages(gid)
            except Exception as e:
                await megux.send_log(e)
        else:
            pass
    elif reply:
        try:
            chat = str(f"{gid}").replace("-100", "")
            link = f"https://t.me/c/{chat}/{reply.id}"
            string = await get_string(m.chat.id, "UNPIN_SUCCESS")
            await m.reply(string.format(link))
            await megux.unpin_chat_message(gid, reply.id)
            data = await LOGS.find_one()
            if data:
                id = data["log_id"]
                id_log = int(id)
                try:
                    return await megux.send_message(id_log, (await get_string(gid, "UNPIN_LOGGER")).format(m.chat.title, m.from_user.mention(), m.from_user.id, link))
                except PeerIdInvalid:
                    return 
                except Exception as e:
                    await megux.send_log(e)
                    return
        except Exception as e:
            await megux.send_log(e)
    else:
        return await m.reply(await get_string(m.chat.id, "UNPIN_NO_REPLY"))


@megux.on_message(filters.command("antichannelpin", Config.TRIGGER))
async def setantichannelpin(c: megux, m: Message):
    gid = m.chat.id
    DATA = get_collection(f"ANTICHANNELPIN {gid}")
    if not await check_rights(gid, m.from_user.id, "can_pin_messages"):
        return await m.reply(await get_string(m.chat.id, "NO_PIN_USER"))
    if not await check_rights(gid, c.me.id, "can_change_info"):
        return await m.reply(await get_string(m.chat.id, "NO_PIN_BOT"))
    if len(m.text.split()) > 1:
        if m.command[1] == "on":
            await DATA.drop()
            await DATA.insert_one({"status": "on"})
            await m.reply(await get_string(m.chat.id, "ANTICHANNELPIN_ENABLED"))
        elif m.command[1] == "off":
            await DATA.drop()
            await DATA.insert_one({"status": "off"})
            await m.reply(await get_string(m.chat.id, "ANTICHANNELPIN_DISABLED"))
        else:
            await m.reply(await get_string(m.chat.id, "ANTICHANNELPIN_ERROR"))
    else: 
         if not await DATA.find_one({"status": "on"}):
             await m.reply(await get_string(m.chat.id, "CHANNELPIN_DISABLED")) 
         else: 
             await m.reply(await get_string(m.chat.id, "CHANNELPIN_ENABLED")) 
         

@megux.on_message(filters.linked_channel, group=-1)
async def acp_action(c: megux, m: Message):
    gid = m.chat.id 
    DATA = get_collection(f"ANTICHANNELPIN {m.chat.id}")
    get_acp = await DATA.find_one({"status": "on"})
    getmychatmember = await m.chat.get_member("me")
    if get_acp:
        if not await check_rights(gid, c.me.id, "can_pin_messages"):
            return await m.reply(await get_string(m.chat.id, "NO_PIN_BOT"))
        await m.unpin()
    else:
        pass
