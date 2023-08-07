import requests 
import openai
import asyncio

from pyrogram import filters 
from pyrogram.types import Message 
from pyrogram.enums import ChatType

from megumin import megux, Config
from megumin.utils import get_collection, get_string, disableable_dec, is_disabled, input_str


async def generate_response(text):
    openai.api_key = Config.API_CHATGPT
    response = openai.Completion.create(
        engine='text-davinci-003',  # Especifique o modelo do ChatGPT a ser usado
        prompt=text,  # O texto de entrada ou pergunta para o modelo
        temperature=0.2, # Modo de temperatura. forma da mensagem.
        max_tokens=2048,  # O número máximo de tokens para a resposta gerada
        n=1,  # O número de respostas a serem geradas
        stop="<b>By:</b> @WhiterKangBOT",  # Um token opcional para indicar o fim da resposta gerada
    )

    answer = response.choices[0].text.strip()  # Obtém a resposta gerada do ChatGPT
    return answer



@megux.on_message(filters.command("simi", Config.TRIGGER))
@disableable_dec("simi")
async def simi_(_, m: Message):
    chat_id = m.chat.id
    if await is_disabled(chat_id, "simi"):
        return
    text_ = m.text.split(maxsplit=1)[1]
    API = f"https://api.simsimi.net/v2/?text={text_}&lc=pt&cf=false"
    r = requests.get(API).json()  
    if r["success"] in "Eu não resposta. Por favor me ensine.":
        return await m.reply(await get_string(m.chat.id, "SIMI_NO_RESPONSE"))
    if r["success"]:
        return await m.reply(r["success"])
    else:
        return await m.reply(await get_string(m.chat.id, "SIMI_API_OFF"))


@megux.on_message(filters.command("ask", Config.TRIGGER))
@disableable_dec("ask")
async def chatgpt(c: megux, m: Message):
    chat_id = m.chat.id
    if await is_disabled(chat_id, "ask"):
        return
    args = m.text
    if not input_str(m):
        return await m.reply("Não foi possivel entender a sua pergunta, afirmação e entre outros..., Já que não descreveste ela!")
    msg = await m.reply("<i>Aguarde...</i>")
    await asyncio.sleep(2)
    await msg.edit("<i>A resposta está sendo gerada...</i>")
    try:
        response = await generate_response(args)
        await msg.edit("<i>Resposta Gerada!!</i> <b>Enviando Resposta...</b>")
        await msg.edit(response)
    except Exception as ex:
        await msg.edit(f"Ocorreu um erro: {ex.__class__.__name__} Devido a: {ex}")
