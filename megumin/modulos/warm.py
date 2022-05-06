import os
import asyncio 

from typing import Union
from pyrogram import filters 
from pyrogram.types import (CallbackQuery, 
InlineKeyboardButton, 
InlineKeyboardMarkup,
Message, 
)


from megumin import megux 
from megumin.utils import get_collection


@megux.on_message(filters.command(["warm"], prefixes=["/", "!"]))
async def warm_(_, message):
    ids = (message.reply_to_message.from_user.id)
    WARMS = get_collection(f"WARMS {ids}")
    name_user = (message.reply_to_message.from_user.mention())
    await asyncio.gather(WARMS.insert_one({"id_": ids, "title": name_user}))
    G = await WARMS.estimated_document_count()
    if G > 2:
        await message.reply(f"{G}/3 Advertencias, {name_user} foi banido!")
        await asyncio.gather(WARMS.drop())
        return
    keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Remover Advertencia",
              callback_data="remove_warm_")]
            ]
        )
    await message.reply(f"{name_user} <b>foi advertido!</b>\nEle(a) tem {G}/3 Advertências.", reply_markup=(keyboard))


@megux.on_callback_query(filters.regex(pattern=r"^remove_warm_$"))
async def warm_remove_(client: megux, cb: CallbackQuery, message: Message):
    await cb.answer(f"""Advertência removida.""", show_alert=True)
    await asyncio.gather(WARMS.delete_one())

    
          


