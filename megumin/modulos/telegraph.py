##
#
import os
import html

from pyrogram import filters
from pyrogram.types import Message
from telegraph.aio import Telegraph
from telegraph.exceptions import TelegraphException

from megumin import megux, Config 
from megumin.utils import get_string


tg = Telegraph()


@megux.on_message(filters.command(["telegraph", "tg"], Config.TRIGGER))
async def telegraph(c: megux, m: Message):
    if not m.reply_to_message:
        await m.reply_text("Por favor, responda a uma foto, vídeo, gif ou texto.")
        return

    await tg.create_account(
        short_name="WhiterKang",
        author_name="WhiterKang",
        author_url="https://t.me/WhiterKangBOT",
    )

    if (
        m.reply_to_message.photo
        or m.reply_to_message.video
        or m.reply_to_message.animation
    ):
        file = await m.reply_to_message.download()
        try:
            r = await tg.upload_file(file)
        except TelegraphException as err:
            await m.reply_text(f"<b>Erro!</b> <code>{err}</code>")
            os.remove(file)
            return
        await m.reply_text(f"https://telegra.ph{r[0]['src']}")
    elif m.reply_to_message.text:
        r = await tg.create_page(
            "Auto generated by @WhiterKangBOT",
            html_content=m.reply_to_message.text.html,
        )
        await m.reply_text(r["url"])
