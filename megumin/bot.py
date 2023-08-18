# Copyright (C) 2022 by fnixdev
#

from pyrogram import Client

import time
import logging
import os

START_TIME = time.time()

from megumin import version, Config

GP_LOGS = Config.GP_LOGS

class WhiterKang(Client):
    def __init__(self):
        kwargs = {
            'name': "WhiterKang",
            'api_id': os.environ.get("API_ID"),
            'api_hash': os.environ.get("API_HASH"),
            'bot_token': os.environ.get("BOT_TOKEN"),
            'workers': 24,
            'in_memory': True,
            'plugins': dict(root="megumin.modulos")
        }
        super().__init__(**kwargs)

    async def start(self):
        await super().start()
        self.me = await self.get_me()
        text_ = f"#Whiter #Logs\n\n__WhiterKang está trabalhando agora.__\n\n**Versão:** `{version.__megumin_version__}`\n**System:** `{self.system_version}`\n**Python:** `{version.__python_version__}`\n**Pyrogram:** `{version.__pyro_version__}`"
        await self.send_message(chat_id=GP_LOGS, text=text_) 
        logging.info("WhiterKang esta acordando...")

    async def stop(self):
        self.me = await self.get_me()
        text_ = f"#Whiter #Logs\n\n__WhiterKang foi dormir.__"
        await self.send_message(chat_id=GP_LOGS, text=text_)
        await super().stop()
        logging.info("WhiterKang dormiu...")

    async def send_log(self, text: str, *args, **kwargs):
        await self.send_message(
            chat_id=GP_LOGS,
            text=text,
            *args,
            **kwargs,
        )
        logging.info(text)
        
    async def send_err(self, err: str, *args, **kwargs):
        await self.send_message(
            chat_id=GP_LOGS,
            text=f"#TRACEBACK\n\n{err}",
            *args,
            **kwargs
        )
        logging.error(err)

megux = WhiterKang()
