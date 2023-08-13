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
        name = input_str(m) 
        searchi = f"{name}".replace(" ", "+")
        get_search_api = await search_device(searchi)
        if not get_search_api == []:
            # Access the link from the first search result  
            name = get_search_api[0]["name"]
            img = get_search_api[0]["img"]
            id = get_search_api[0]["id"]
            link = f"https://www.gsmarena.com/{id}.php"
            description = get_search_api[0]["description"]
            try:
                get_device_api = await get_device(id)
                name_cll = get_device_api["name"]
                s1 = get_device_api['detailSpec'][0]['specifications'][0]['value']
                s1_name = get_device_api['detailSpec'][0]['specifications'][0]['name']
                s2 = get_device_api['detailSpec'][1]['specifications'][0]['value']
                s2_name = get_device_api['detailSpec'][1]['specifications'][0]['name']
                s3 = get_device_api['detailSpec'][4]['specifications'][1]['value']
                s3_name = get_device_api['detailSpec'][4]['specifications'][1]['name']
                s4 = get_device_api['detailSpec'][3]['specifications'][1]['value']
                s4_name = getdevice_api['detailSpec'][3]['specifications'][1]['name']
                s5 = get_device_api['detailSpec'][2]['specifications'][3]['value']
                s5_name = get_device_api['detailSpec'][2]['specifications'][3]['name']
                await m.reply(f"<b>Foto Device</b>: {img}\n<b>URL Fonte:</b>: https://www.gsmarena.com/{id}.php\n\n<b>- Aparelho</b>:  <i>{name_cll}</i>\n<b>- {s1_name}</b>: <i>{s1}</i>\n<b>- {s2_name}</b>: <i>{s2}</i>\n<b>- {s3_name}</b>: <i>{s3}</i>\n<b>- {s4_name}</b>: <i>{s4}</i>\n<b>- {s5_name}</b>: <i>{s5}</i>\n\n<b>Descrição</b>: {description}", disable_web_page_preview=False)
            except Exception as err:
                return await m.reply(f"Não consegui obter resultados sobre o aparelho. O gsmarena pode estar offline. <i>Erro</i>: <b>{err}</b>")
        else:
            return await m.reply("Não encontrei este Dispositivo! :(")
    else:
        return await m.reply("Não consigo advinhar o dispositivo!! woobs!!")
