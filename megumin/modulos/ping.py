import time
import asyncio 

from pyrogram import filters
from pyrogram.types import Message
from datetime import datetime

from megumin import megux, Config 
from megumin import START_TIME
from megumin.utils import time_formatter, get_collection 


@megux.on_message(filters.command(["ping"], Config.TRIGGER))

async def pingme(_, message: Message):
    DISABLED = get_collection(f"DISABLED {message.chat.id}")
    query = "ping"  
    off = await DISABLED.find_one({"_cmd": query})
    if off:
        return
    text = " ".join(message.text.split()[1:])  
    start = datetime.now() 
    if text and text == "-a":
        m = await message.reply("!....")
        await asyncio.sleep(0.3)
        await m.edit("..!..")
        await asyncio.sleep(0.3)
        await m.edit("....!")
        end = datetime.now()
        t_m_s = (end - start).microseconds / 1000
        m_s = round((t_m_s - 0.6) / 3, 3)
        await m.edit(f"🏓 ᴘᴏɴɢ! \n`{m_s} ᴍs`")
    else:
        sla = await message.reply("🏓 ᴘᴏɴɢ!")
        end = datetime.now()
        m_s = (end - start).microseconds / 1000
        await sla.edit("🏓 <b>Ping:</b> <code>{} ᴍs</code>\n⏱ <b>Uptime:</b> <code>{}</code>".format(m_s, time_formatter(time.time() - START_TIME)))
        
