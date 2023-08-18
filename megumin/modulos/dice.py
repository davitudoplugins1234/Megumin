from pyrogram import filters
from pyrogram.types import Message

from megumin import megux


@megux.on_message(filters.command(["dice", "dado"], prefixes=["/", "!"]))
async def dice(c: megux, m: Message):
    dicen = await c.send_dice(m.chat.id, reply_to_message_id=m.id)
    await dicen.reply_text("🎲 O dado parou no número: {number}".format(number=dicen.dice.value), quote=True
    )
