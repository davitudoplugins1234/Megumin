import time
import asyncio 

from pyrogram import filters
from pyrogram.types import Message
from datetime import datetime

from megumin import megux
from megumin import START_TIME
from megumin.utils import time_formatter, get_collection 

DISABLED = get_collection("DISABLED")

@megux.on_message(filters.command(["ping"]))

async def pingme(_, message: Message):
    gid = message.chat.id  
    off = await DISABLED.find_one({"_id": gid})
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
        await message.reply(f"🏓 ᴘᴏɴɢ! \n`{m_s} ᴍs`")
    else:
        sla = await message.reply("🏓 ᴘᴏɴɢ!")
        end = datetime.now()
        m_s = (end - start).microseconds / 1000
        await sla.edit(f"🏓 **Ping:** ```{m_s} ᴍs``` \n⏱ **Uptime:** ```{time_formatter(time.time() - START_TIME)}```")
        
