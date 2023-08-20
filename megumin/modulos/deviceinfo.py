Peço desculpas pela confusão. Aqui está a versão corrigida do código com os emojis em inglês:

```python
# Importações
from gpytranslate import Translator
from pyrogram import filters
from pyrogram.types import Message

from megumin import megux, Config
from megumin.utils import disableable_dec, is_disabled, search_device, get_device, add_user, find_user
from megumin.utils.decorators import input_str

tr = Translator()

# Mapeamento de emojis para categorias em inglês
CATEGORY_EMOJIS = {
    "Screen": "📱",
    "Platform": "⚙️",
    "Memory": "💾",
    "Cameras": "📷",
    "Front Camera": "🤳",
    "Sound": "🔈",
    "Connectivity": "🌐",
    "Extras": "✨",
    "Battery": "🔋"
}

@megux.on_message(filters.command(["deviceinfo", "d"], Config.TRIGGER))
@disableable_dec("deviceinfo")
async def deviceinfo(c: megux, m: Message):
    if await is_disabled(m.chat.id, "deviceinfo"):
        return

    if not await find_user(m.from_user.id):
        await add_user(m.from_user.id)

    if input_str(m):
        name = input_str(m).lower() 
        searchi = f"{name}".replace(" ", "+")
        get_search_api = await search_device(searchi)
        
        if not get_search_api == []:
            # Acessa o link do primeiro resultado de pesquisa
            name = get_search_api[0]["name"]
            img = get_search_api[0]["img"]
            id = get_search_api[0]["id"]
            link = f"https://www.gsmarena.com/{id}.php"
            description = get_search_api[0]["description"]
            
            try:
                get_device_api = await get_device(id)
                name_cll = get_device_api.get("name", "N/A")
                base_device = f"Photo Device: {img}\nSource URL: {link}"
                DEVICE_TEXT = f"📌 {name_cll}\n📅 Announced: {get_device_api['detailSpec'][1]['specifications'][0]['value']}\n\n{base_device}"
                
                for spec_index in range(7):
                    try:
                        category = get_device_api['detailSpec'][spec_index]['category']
                        translated_category = CATEGORY_EMOJIS.get(category, '')
                        specs = get_device_api['detailSpec'][spec_index]['specifications']
                        section_text = f"\n\n{translated_category} {category}:\n"
                        
                        for spec in specs:
                            name = spec['name']
                            value = spec['value']
                            section_text += f"{name}: {value}\n"
                        
                        DEVICE_TEXT += section_text
                    except (IndexError, KeyError):
                        pass
                DEVICE_TEXT += "\n\n<b>Description</b>: {description}"
                await m.reply(DEVICE_TEXT, disable_web_page_preview=False)
                
            except Exception as err:
                return await m.reply(f"Couldn't retrieve device details. The GSM Arena website might be offline. <i>Error</i>: <b>{err}</b>\n<b>Line</b>: {err.__traceback__.tb_lineno}")
        
        else:
            return await m.reply("Couldn't find this device! :(")
    else:
        return await m.reply("I can't guess the device!! woobs!!")
