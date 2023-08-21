import requests
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
    if await is_disabled(m.chat.id, "deviceinfo"):
        return

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
        print(searchi)
        
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
                        specs = get_device_api['detailSpec'][spec_index]['specifications']
                        section_text = f"\n\n<b>{translated_category} <u>{category}</b></u>:\n"
                        
                        for spec in specs:
                            name = spec['name']
                            value = spec['value']
                            section_text += f"- <b>{name}:</b> <i>{value}</i>\n"
                        
                        DEVICE_TEXT += section_text
                    except (IndexError, KeyError):
                        pass
                DEVICE_TEXT += f"\n\n<b>Description</b>: <i>{description}</i>"
                if len(DEVICE_TEXT) >= 4096:
                    ftext = DEVICE_TEXT[:4092] + "..."
                else:
                    ftext = DEVICE_TEXT
                await m.reply(ftext, disable_web_page_preview=False)
                
            except Exception as err:
                return await m.reply(f"Couldn't retrieve device details. The GSM Arena website might be offline. <i>Error</i>: <b>{err}</b>\n<b>Line</b>: {err.__traceback__.tb_lineno}")
        
        else:
            return await m.reply("Couldn't find this device! :(")
    else:
        return await m.reply("I can't guess the device!! woobs!!")
