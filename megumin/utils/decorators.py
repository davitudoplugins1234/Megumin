# WhiterKang Bot
# Copyright (C) 2023 Davi
#
# This file is a part of < https://github.com/DaviTudoPlugins1234/WhiterKang/ >
# PLease read the GNU v3.0 License Agreement in 
# <https://www.github.com/DaviTudoPlugins1234/WhiterKang/blob/master/LICENSE/>.

## WhiterKang Decorators
from typing import List, Optional

from pyrogram import filters
from pyrogram.types import Message

from megumin import megux, logging
from megumin.utils import is_disabled

DISABLABLE_CMDS: List[str] = []
    

def input_str(message) -> str:
    return " ".join(message.text.split()[1:])

def disableable_dec(command):
    if command not in DISABLABLE_CMDS:
        logging.info(
            f"Adding {command} to the disableable commands...",
        )
        DISABLABLE_CMDS.append(command)

    def decorator(func):
        async def wrapper(c: megux, message: Message, *args, **kwargs):
            chat_id = message.chat.id

            check = await is_disabled(chat_id, command)
            if check:
                return

            return await func(c, message, *args, **kwargs)

        return wrapper

    return decorator


class InlineHandler:
    """This class is a python interface to InlineHandler"""
    def __init__(self):
        self.INLINE_CMDS = []

    def add_cmd(
        self,
        command: str,
        txt_description: str,
        thumb_url: str,
        aliases: Optional[list] = None,
    ):
        self.INLINE_CMDS.append(
            {
                "command": command,
                "txt_description": txt_description,
                "url_thumb": thumb_url,
                "aliases": aliases or [],
            }
        )

    def search_cmds(self, query: Optional[str] = None):
        return [
            cmd
            for cmd in sorted(self.INLINE_CMDS, key=lambda k: k["command"])
            if (
                not query
                or query in cmd["command"]
                or any(query in alias for alias in cmd["aliases"])
            )
        ]

inline_handler = InlineHandler()
