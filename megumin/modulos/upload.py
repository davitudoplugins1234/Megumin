import asyncio
import math
import os
import re

from datetime import datetime
from typing import Tuple, Union
from urllib.parse import unquote_plus

from pySmartDL import SmartDL

from pyrogram import filters 
from pyrogram.types import Message 
from megumin import megux, Config 
from megumin.utils import humanbytes
from megumin.utils.decorators import input_str

FINISHED_PROGRESS_STR = os.environ.get("FINISHED_PROGRESS_STR")
UNFINISHED_PROGRESS_STR = os.environ.get("UNFINISHED_PROGRESS_STR")


class ProcessCanceled(Exception):
    """raise if thread has terminated"""


@megux.on_message(filters.command("upload", Config.TRIGGER))
async def upload_(_, m: Message):
    url = input_str(m)
    if not url:
        return await m.reply("Vou enviar o Vento?")
    is_url = re.search(r"(?:https?|ftp)://[^|\s]+\.[^|\s]+", url)
    del_path = False
    if is_url:
        del_path = True
        try:
            path_, _ = await url_download(message, url)
        except ProcessCanceled:
            await msg.edit("`Process Canceled!`")
            return
        except Exception as e_e:  # pylint: disable=broad-except
            await msg.reply(str(e_e))
            return
    if "|" in path_:
        url, file_name = path_.split("|")
        url = path_.strip()
        if os.path.isfile(url):
            new_path = os.path.join(Config.DOWN_PATH, file_name.strip())
            os.rename(path_, new_path)
            path_ = new_path
    try:
        string = Path(url)
    except IndexError:
        await msg.edit("wrong syntax\n`.upload [path]`")
    else:
        await message.delete()
        await upload_path(message=message, path=string, del_path=del_path)


async def url_download(message: Message, url: str) -> Tuple[str, int]:
    """download from link"""
    msg = await message.reply("`Uploading...`")
    start_t = datetime.now()
    custom_file_name = unquote_plus(os.path.basename(url))
    if "|" in url:
        url, c_file_name = url.split("|", maxsplit=1)
        url = url.strip()
        if c_file_name:
            custom_file_name = c_file_name.strip()
    dl_loc = os.path.join(Config.DOWN_PATH, custom_file_name)
    downloader = SmartDL(url, dl_loc, progress_bar=False)
    downloader.start(blocking=False)
    count = 0
    while not downloader.isFinished():
        if message.process_is_canceled:
            downloader.stop()
            raise ProcessCanceled
        total_length = downloader.filesize or 0
        downloaded = downloader.get_dl_size()
        percentage = downloader.get_progress() * 100
        speed = downloader.get_speed(human=True)
        estimated_total_time = downloader.get_eta(human=True)
        progress_str = (
            "__{}__\n"
            + "```[{}{}]```\n"
            + "**Progress** : `{}%`\n"
            + "**URL** : `{}`\n"
            + "**FILENAME** : `{}`\n"
            + "**Completed** : `{}`\n"
            + "**Total** : `{}`\n"
            + "**Speed** : `{}`\n"
            + "**ETA** : `{}`"
        )
        progress_str = progress_str.format(
            "trying to download",
            "".join(
                (
                    FINISHED_PROGRESS_STR
                    for i in range(math.floor(percentage / 5))
                )
            ),
            "".join(
                (
                    UNFINISHED_PROGRESS_STR
                    for i in range(20 - math.floor(percentage / 5))
                )
            ),
            round(percentage, 2),
            url,
            custom_file_name,
            humanbytes(downloaded),
            humanbytes(total_length),
            speed,
            estimated_total_time,
        )
        count += 1
        if count >= 10:
            count = 0
            await msg.edit(progress_str, disable_web_page_preview=True)
        await asyncio.sleep(1)
    return dl_loc, (datetime.now() - start_t).seconds
