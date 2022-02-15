import requests
from pyrogram import filters
from pyrogram.types import Message

from megumin import megux

DEVICE_LIST = "https://raw.githubusercontent.com/androidtrackers/certified-android-devices/master/by_device.json"

@megux.on_message(filters.command(["device", "whatis"]))
async def device_(_, message: Message):
    msg = await message.reply("Procurando...")
    if not len(message.text.split()) == 1:
        await message.edit("Quer que eu adivinhe? Por favor digite um codename")
        return
    getlist = requests.get(DEVICE_LIST).json()
    target_device = message.text.split()[1].lower()
    if target_device in list(getlist):
        device = getlist.get(target_device)
        text = ""
        for x in device:
            text += f"**Marca:** ```{x['brand']}```\n**Nome:** ```{x['name']}```\n**Dispositivo:** ```{x['model']}```\n**Codename:** ```{target_device}```"
            text += "\n\n"
        await msg.edit(text)
    else:
        await msg.edit(f"Device {target_device} não foi encontrado!")
        await sleep(5)
        await msg.delete()
