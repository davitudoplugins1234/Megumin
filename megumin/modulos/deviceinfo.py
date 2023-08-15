from gpytranslate import Translator
from pyrogram import filters
from pyrogram.types import Message

from megumin import megux, Config
from megumin.utils import disableable_dec, is_disabled, http, tld, search_device, get_device
from megumin.utils.decorators import input_str

tr = Translator()

@megux.on_message(filters.command(["deviceinfo", "d"], Config.TRIGGER))
@disableable_dec("deviceinfo")
async def deviceinfo(c: megux, m: Message):
    if await is_disabled(m.chat.id, "deviceinfo"):
        return
    if input_str(m):
        name = input_str(m).lower() 
        searchi = f"{name}".replace(" ", "+")
        get_search_api = await search_device(searchi)
        if get_search_api:
            # Access the link from the first search result  
            name = get_search_api[0].get("name", "N/A")
            img = get_search_api[0].get("img", "N/A")
            id = get_search_api[0].get("id", "N/A")
            link = f"https://www.gsmarena.com/{id}.php"
            description = get_search_api[0].get("description", "N/A")
            try:
                get_device_api = await get_device(id)
                name_cll = get_device_api.get("name", "N/A")
                s1 = get_device_api['detailSpec'][0]['specifications'][0].get('value', 'N/A')
                s1_name = get_device_api['detailSpec'][0]['specifications'][0].get('name', 'N/A')
                s2 = get_device_api['detailSpec'][1]['specifications'][0].get('value', 'N/A')
                s2_name = get_device_api['detailSpec'][1]['specifications'][0].get('name', 'N/A')
                s3 = get_device_api['detailSpec'][4]['specifications'][1].get('value', 'N/A')
                s3_name = get_device_api['detailSpec'][4]['specifications'][1].get('name', 'N/A')
                s4 = get_device_api['detailSpec'][3]['specifications'][1].get('value', 'N/A')
                s4_name = get_device_api['detailSpec'][3]['specifications'][1].get('name', 'N/A')
                s5 = get_device_api['detailSpec'][2]['specifications'][3].get('value', 'N/A')
                s5_name = get_device_api['detailSpec'][2]['specifications'][3].get('name', 'N/A')
                await m.reply(f"<b>Photo Device</b>: {img}\n<b>URL Font</b>: https://www.gsmarena.com/{id}.php\n\n<b>- Device</b>:  <i>{name_cll}</i>\n<b>- {s1_name}</b>: <i>{s1}</i>\n<b>- {s2_name}</b>: <i>{s2}</i>\n<b>- {s3_name}</b>: <i>{s3}</i>\n<b>- {s4_name}</b>: <i>{s4}</i>\n<b>- {s5_name}</b>: <i>{s5}</i>\n\n<b>Description</b>: {description}", disable_web_page_preview=False)
            except Exception as err:
                return await m.reply(f"Não consegui obter resultados sobre o aparelho. O gsmarena pode estar offline. <i>Erro</i>: <b>{err}</b>")
        else:
            return await m.reply("Não encontrei este Dispositivo! :(")
    else:
        return await m.reply("Não consigo advinhar o dispositivo!! woobs!!")
