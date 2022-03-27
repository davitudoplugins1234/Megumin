import sys
import os
import random
import re
import requests
import wget
import datetime
import signal

from pyrogram import filters
from pyrogram.types import Message

from megumin import megux

@megux.on_message(filters.command("restart") & filters.user(1715384854))
async def broadcast(c: megux, m: Message):
    sent = await m.reply("__Reiniciando aguarde...__") 
    args = [sys.executable, "-m", "megumin"]
    await sent.edit("**WhiterKang Reiniciado com Sucesso!**")
    os.execl(sys.executable, *args)


@megux.on_message(filters.command(["update", "upgrade"]) & filters.user(1715384854))
async def broadcast(c: megux, m: Message):
    sent = await m.reply("__Atualizando aguarde...__")
    pull = [sys.executable, "gitpull"] 
    os.execl(sys.executable, *pull)
    await sent.edit("**WhiterKang foi atualizado!!**")
    args = [sys.executable, "-m", "megumin"]
    await sent.edit("__Reiniciando aguarde...__")
    os.execl(sys.executable, *args)
    await sent.edit("**WhiterKang Reiniciado com Sucesso!**")


@megux.on_message(filters.command(r"shutdown") & filters.user(OWNER))
async def shutdown(c: megux, m: Message):
    await m.reply_text("Adeus...")
    os.kill(os.getpid(), signal.SIGINT)
