import re
import os
import requests
from requests.structures import CaseInsensitiveDict

from pyrogram import filters 
from pyrogram.types import Message 

from megumin import megux, Config 


def GRS(path_to_file):
    if os.path.exists(path_to_file):
        filePath = path_to_file
    else:
        raise ValueError("file don't exist, please verify your \"path to file\"")
    searchUrl = 'http://www.google.hr/searchbyimage/upload'
    multipart = {'encoded_image': (filePath, open(filePath, 'rb')), 'image_content': ''}
    response = requests.post(searchUrl, files=multipart, allow_redirects=False)
    fetchUrl = str(response.headers['Location'])
    url = fetchUrl
    headers = CaseInsensitiveDict()
    headers["Host"] = "www.google.hr"
    headers["Connection"] = "keep-alive"
    headers["Upgrade-Insecure-Requests"] = "1"
    headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
    headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
    headers["Sec-Fetch-Site"] = "none"
    headers["Sec-Fetch-Mode"] = "navigate"
    headers["Sec-Fetch-User"] = "?1"
    headers["Sec-Fetch-Dest"] = "document"
    headers["sec-ch-ua"] = '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"'
    headers["sec-ch-ua-mobile"] = "?0"
    headers["Accept-Language"] = "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6,zh;q=0.5"
    resp = requests.get(url, headers=headers)
    regex = re.findall('value="(.*?)" aria-label="Pesquisar"', resp.text)
    return fetchUrl, regex[0]

@megux.on_message(filters.command("reverse", Config.TRIGGER))
async def reverse_search(_, message: Message):
    """reverse search on google"""
    if message.reply_to_message:
        try:
            media = await message.reply_to_message.download()
            texto = await message.reply("__Uploading it to Google.__")
        except ValueError:
            return await texto.edit("A mensagem não contém nenhum arquivo de midia.")
        if media.endswith((".jpg", ".gif", ".png", ".bmp", ".tif", ".webp")):
            try:
                reverse = GRS(media)
            except BaseException as error:
                return await texto.edit(error)
            text = "**Resultados da pesquisa:** "
            if reverse:
                text += f"[{reverse[1]}]({reverse[0]})"
            else:
                text += "\n\tLink não encontrado."
            await texto.edit(text,parse_mode="md", disable_web_page_preview=True)
        else:
            await texto.edit("Arquivo não suportado.")
        os.remove(media)
    else:
        await message.reply("Por favor, responda a uma foto ou video para que eu possa pesquisar")
