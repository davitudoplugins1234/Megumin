import requests
import io

from gpytranslate import Translator
from pyrogram import filters
from pyrogram.types import Message

from megumin import megux, Config
from megumin.utils import disableable_dec, is_disabled, search_device, get_device, add_user, find_user
from megumin.utils.decorators import input_str

tr = Translator()

# Mapeamento de emojis para categorias em inglês
CATEGORY_EMOJIS = {
    "Display": "📱",
    "Platform": "⚙️",
    "Memory": "💾",
    "Main Camera": "📷",
    "Selfie camera": "🤳",
    "Sound": "🔈",
    "Network": "🌐",
    "Battery": "🔋",
    "Body": "🏗",
    "Launch": "🚀",
    "Comms": "📡",
    "Features": "✨",
    "Misc": "📦",
    "Tests": "ℹ️"
}

DEVICE_LIST = "https://raw.githubusercontent.com/androidtrackers/certified-android-devices/master/by_device.json"

@megux.on_message(filters.command(["deviceinfo", "d"], Config.TRIGGER))
@disableable_dec("deviceinfo")
async def deviceinfo(c: megux, m: Message):
    if not await find_user(m.from_user.id):
        await add_user(m.from_user.id)

    getlist = requests.get(DEVICE_LIST).json()

    if input_str(m):
        name = input_str(m).lower()
        if name in list(getlist):
            searchi = getlist.get(name)[0]['name'].replace(" ", "+")
        else:
            searchi = f"{name}".replace(" ", "+")
            
        get_search_api = await search_device(searchi)
        
        if not get_search_api == []:
            name = get_search_api[0]["name"]
            img = get_search_api[0]["img"]
            id = get_search_api[0]["id"]
            link = f"https://www.gsmarena.com/{id}.php"
            description = get_search_api[0]["description"]
            
            try:
                get_device_api = await get_device(id)
                name_cll = get_device_api.get("name", "N/A")
                base_device = f"<b>Photo Device:</b> <i>{img}</i>\n<b>Source URL:</b> <i>{link}</i>"
                DEVICE_TEXT = f"{base_device}\n\n📌 <b><u>{name_cll}</b></u>\n📅 <b>Announced:</b> <i>{get_device_api['detailSpec'][1]['specifications'][0]['value']}</i>"
                
                for spec_index in range(14):
                    try:
                        category = get_device_api['detailSpec'][spec_index]['category']
                        translated_category = CATEGORY_EMOJIS.get(category, '')
                        category = await tr.translate(category, targetlang=await tld(m.chat.id, "language")).text
                        specs = get_device_api['detailSpec'][spec_index]['specifications']
                        section_text = f"\n\n<b>{translated_category} <u>{category}</b></u>:\n"
                        
                        for spec in specs:
                            name = spec['name']
                            name = await tr.translate(name, targetlang=await tld(m.chat.id, "language")).text
                            value = spec['value']
                            value = await tr.translate(value, targetlang=await tld(m.chat.id, "language")).text
                            section_text += f"- <b>{name}:</b> <i>{value}</i>\n"
                        
                        DEVICE_TEXT += section_text
                    except (IndexError, KeyError):
                        pass
                        
                #Create Description
                DEVICE_TEXT += f"\n\n<b>Description</b>: <i>{description}</i>"
                
                try:
                    await m.reply(DEVICE_TEXT, disable_web_page_preview=False)
                except Exception as err:
                    # Send the image with the first part of the caption
                    caption_part = DEVICE_TEXT[:1024]
                    caption_rest = DEVICE_TEXT[1024:]

                    await c.send_photo(chat_id=m.chat.id, photo=img, caption=caption_part)

                    # Split the remaining caption and send as regular text messages
                    message_chunks = [caption_rest[i:i + 4096] for i in range(0, len(caption_rest), 4096)]
                    for chunk in message_chunks:
                        await c.send_message(chat_id=m.chat.id, text=chunk)
                    
                    
            except Exception as err:
                return await m.reply(f"Couldn't retrieve device details. The GSM Arena website might be offline. <i>Error</i>: <b>{err}</b>\n<b>Line</b>: {err.__traceback__.tb_lineno}")
        
        else:
            return await m.reply("Couldn't find this device! :(")
    else:
        return await m.reply("I can't guess the device!! woobs!!")
