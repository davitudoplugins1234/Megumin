import base64
import uuid
import html
import re
import time
import httpx
import requests
import asyncio
import spamwatch
import logging

from datetime import datetime, timedelta
from httpx import HTTPError
from typing import Tuple, Callable
from functools import partial, wraps
from math import floor

from pyrogram.enums import ChatMemberStatus 
from pyrogram.types import Message
from pyrogram.enums import ChatType

from megumin import megux, Config
from megumin.utils import get_collection

_BOT_ID = 0


timeout = httpx.Timeout(30, pool=None)
http = httpx.AsyncClient(http2=True, timeout=timeout)


weather_apikey = "8de2d8b3a93542c9a2d8b3a935a2c909"


def time_formatter(seconds: float) -> str:
    """tempo"""
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = (
        ((str(days) + "d, ") if days else "")
        + ((str(hours) + "h, ") if hours else "")
        + ((str(minutes) + "m, ") if minutes else "")
        + ((str(seconds) + "s, ") if seconds else "")
    )
    return tmp[:-2]


async def admin_check(message: Message) -> bool:
    if message.chat.type == ChatType.PRIVATE:
        return True
    client = message._client
    chat_id = message.chat.id
    user_id = message.from_user.id

    check_status = await client.get_chat_member(chat_id=chat_id, user_id=user_id)
    admin_strings = [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    if check_status.status not in admin_strings:
        return False
    else:
        return True


async def is_admin(chat_id: int, user_id: int, check_devs: bool = False) -> bool:
    """checa admin no chat"""
    if check_devs and is_dev(user_id):
        return True
    check_status = await megux.get_chat_member(chat_id=chat_id, user_id=user_id)
    admin_strings = [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    if check_status.status not in admin_strings:
        return False
    else:
        return True



def is_dev(user_id: int) -> bool:
    """retorna se é dev ou não"""
    return user_id in Config.DEV_USERS


async def is_self(user_id: int) -> bool:
    """retorna se usuario é assistente ou não"""
    global _BOT_ID  # pylint: disable=global-statement
    if not _BOT_ID:
        _BOT_ID = (await megux.get_me()).id
    return user_id == _BOT_ID


async def check_rights(chat_id: int, user_id: int, rights: str) -> bool:
    """Verifica os privilégios do usuário"""
    user = await megux.get_chat_member(chat_id, user_id)
    if user_id in Config.DEV_USERS:
        return True
    elif user.status == ChatMemberStatus.OWNER:
        return True
    elif user.status == ChatMemberStatus.ADMINISTRATOR:
        if getattr(user.privileges, rights, None):
            return True
        return False
    return False


async def check_bot_rights(chat_id: int, rights: str) -> bool:
    """checa privilegios megux"""
    global _BOT_ID  # pylint: disable=global-statement
    if not _BOT_ID:
        _BOT_ID = (await megux.get_me()).id
    bot_ = await megux.get_chat_member(chat_id, _BOT_ID)
    if bot_.status == ChatMemberStatus.ADMINISTRATOR:
        if getattr(bot_.privileges, rights, None):
            return True
        return False
    return False


async def sed_sticker(msg: Message):
    """envia sticker"""
    sticker = (await megux.get_messages("kannagifs", 19)).sticker.file_id
    await msg.reply_sticker(sticker)


def humanbytes(size: float) -> str:
    """humanize size"""
    if not size:
        return ""
    power = 1024
    t_n = 0
    power_dict = {0: " ", 1: "Ki", 2: "Mi", 3: "Gi", 4: "Ti"}
    while size > power:
        size /= power
        t_n += 1
    return "{:.2f} {}B".format(size, power_dict[t_n])


def encode_to_base64_string(msg: str) -> str:
    msg_bytes = msg.encode("utf-8")
    base64_bytes = base64.b64encode(msg_bytes)
    return base64_bytes.decode("utf-8")


def decode_to_base64_string(msg: str) -> str:
    msg_bytes = msg.encode("utf-8")
    base64_bytes = base64.b64decode(msg_bytes)
    return base64_bytes.decode("utf-8")


async def extract_time(msg, time_val):
    if any(time_val.endswith(unit) for unit in ("m", "h", "d")):
        unit = time_val[-1]
        time_num = time_val[:-1]  # type: str
        if not time_num.isdigit():
            await msg.reply("`Quantidade de tempo específicada é inválida.`")
            return

        if unit == "m":
            bantime = datetime.now() + timedelta(minutes=int(time_num))
        elif unit == "h":
            bantime = datetime.now() + timedelta(hours=int(time_num))
        elif unit == "d":
            bantime = datetime.now() + timedelta(days=int(time_num))  
        else:
            await msg.reply("`Existe outra unidade de tempo que você conhece ..?`")
            return
        return bantime
    else:
        await msg.reply("`Eu preciso que você informe um tempo (m, h ou d)`")
        return


async def cssworker_url(target_url: str, pc_id: str):
    url = "https://htmlcsstoimage.com/demo_run"
    my_headers = {
    "User-Agent": f"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0 [PC-ID({pc_id})]",
    "Accept-Language": "pt-BR"
}


    data = {
        "url": target_url,
        # Sending a random CSS to make the API to generate a new screenshot.
        "css": f"random-tag {uuid.uuid4()}",
        "render_when_ready": False,
        "viewport_width": 1280,
        "viewport_height": 720,
        "device_scale": 1,
    }

    try:
        resp = await http.post(url, headers=my_headers, json=data)
        return resp.json()
    except HTTPError:
        return None


def cleanhtml(raw_html):
    cleanr = re.compile("<.*?>")
    cleantext = re.sub(cleanr, "", raw_html)
    return cleantext


def escape_definition(definition):
    for key, value in definition.items():
        if isinstance(value, str):
            definition[key] = html.escape(cleanhtml(value))
    return definition

async def unwarn_bnt(gid: int, user_id: int):
    DB = get_collection(f"WARNS")
    await DB.delete_one({"chat_id": gid, "user_id": user_id})

def aiowrap(func: Callable) -> Callable:
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)

    return run


def get_progress(percentage: int):
    progress_bar = (
        "[" + "==" * floor(15 * percentage / 100) +
        "\\" * floor(15 * (1 - percentage / 100)) + "]"
    )
    return progress_bar


spamwatch_api = Config.SW_API
if spamwatch_api == "None":
    sw = None
    logging.warning("SpamWatch API key is missing! Check your config.env.")
else:
    try:
        sw = spamwatch.Client(spamwatch_api)
    except Exception:
        sw = None
