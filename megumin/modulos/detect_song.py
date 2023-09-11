import os
import asyncio

from shazamio import Shazam

from pyrogram import filters
from pyrogram.types import Message

from megumin import megux, Config
from megumin.utils import find_user, add_user, disableable_dec


shazam = Shazam()

@megux.on_message(filters.command(["whichsong", "detectsong"], Config.TRIGGER))
async def which_song(c: megux, message: Message):
    """ discover song using shazam"""
    if not await find_user(message.from_user.id):
        await add_user(message.from_user.id)
    replied = message.reply_to_message
    if not replied or not (replied.audio, replied.voice):
        await message.reply("<code>Reply audio needed.</code>")
        return
    sent = await message.reply("<i>Downloading audio..</i>")
    file = await c.download_media(
                message=message.reply_to_message,
                file_name=Config.DOWN_PATH
            )
    try:
        await sent.edit("<i>Detecting song...</i>")
        res = await shazam.recognize_song(file)
    except Exception as e:
        await sent.edit(e)
        os.remove(file)
        return await sent.edit("<i>Failed to get sound data.</i>")
    try:
        song = res["track"]
    except KeyError:
        await sent.edit("<i>Failed to get sound data.</i>")
        return
    out = f"<b>Song Detected!\n\n{song['title']}</b>\n<i>- {song['subtitle']}</i>"
    try:
        await sent.delete()
        await message.reply_photo(photo=song["images"]["coverart"], caption=out)
    except KeyError:
        await sent.edit(out)
    except Exception:
        os.remove(file)
        return await sent.edit("<i>Failed to get sound data.</i>")
    os.remove(file)
