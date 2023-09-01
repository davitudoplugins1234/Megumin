# lastfm module by @fnix

import asyncio
import requests 
import os

from telegraph import upload_file
from bs4 import BeautifulSoup as bs
from wget import download
from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, InlineQuery, InlineQueryResultPhoto, InlineQueryResultArticle, InputTextMessageContent

from megumin import megux, Config
from megumin.utils.decorators import input_str
from .misc import *
from megumin.utils import get_collection, get_response, disableable_dec, is_disabled

API = "http://ws.audioscrobbler.com/2.0"
LAST_KEY = Config.LASTFM_API_KEY
REG = get_collection("USERS")
          

@megux.on_message(filters.command(["setuser", "reg", "set"], prefixes=["/", "!"]))
@disableable_dec("set")
async def last_save_user(_, message: Message):
    user_id = message.from_user.id
    fname = message.from_user.first_name
    uname = message.from_user.username
    text = input_str(message)
    if not text:
        await message.reply("__Bruh.. use /set lastfm username.__")
        return
    found = await REG.find_one({"id_": user_id})
    user_start = f"#USER_REGISTER #LOGS\n\n**User:** {fname}\n**ID:** {user_id} <a href='tg://user?id={user_id}'>**Link**</a>"
    if uname:
        user_start += f"\n**Username:** @{uname}"
    if found:
        await asyncio.gather(
                REG.update_one({"id_": user_id}, {
                                "$set": {"last_data": text}}, upsert=True),
                message.reply("__Your username has been successfully updated.__")
            )
    else:
        await asyncio.gather(
                REG.update_one({"id_": user_id}, {
                                "$set": {"last_data": text}}, upsert=True),
                megux.send_log(
                    user_start,
                    disable_notification=False,
                    disable_web_page_preview=True,
                ),
                message.reply("__Your username has been successfully set.__")
            )


@megux.on_message(filters.command(["deluser", "duser"], prefixes=["/", "!"]))
@disableable_dec("deluser")
async def last_save_user(_, message: Message):
    user_id = message.from_user.id
    found = await REG.find_one({"id_": user_id})
    if found:
        await asyncio.gather(
                REG.delete_one(found),
                message.reply("__Your username has been deleted.__")
            )
    else:
        return await message.reply("__You don't have a registered username__")


@megux.on_message(filters.command(["profile", "user"]))
@disableable_dec("profile")
async def now_play(c: megux, message: Message):
    user_ = message.from_user
    lastdb = await REG.find_one({"id_": user_.id})
    if not lastdb:
        button = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Create LastFM account", url="https://www.last.fm/join"
                    )
                ]
            ]
        )
        reg_ = "__Enter some username or use /set (username) to set yours. If you don't already have a LastFM account, click the button below to register.__"
        await message.reply(reg_, reply_markup=button)
        return
    user_lastfm = lastdb["last_data"]
    params = {
        "method": "user.getinfo",
        "user": user_lastfm,
        "api_key": Config.LASTFM_API_KEY,
        "format": "json",
    }
    try:
        view_data = await get_response.json(link=API, params=params)
    except ValueError:
        return await message.reply("__Error. Make sure you entered the correct username__")
    params_ = {
        "method": "user.getrecenttracks",
        "user": user_lastfm,
        "api_key": Config.LASTFM_API_KEY,
        "limit": 3,
        "format": "json",
    }
    try:
        view_scr = await get_response.json(link=API, params=params_)
    except ValueError:
        return await message.reply("__Error. Make sure you entered the correct username__")

    # == scrap site
    url_ = f"https://www.last.fm/user/{user_lastfm}/loved"
    get_url = requests.get(url_).text
    soup = bs(get_url, "html.parser")
    try:
        scrob = soup.select('h1.content-top-header')[0].text.strip()
        scrr = scrob.split()[2].replace("(", "").replace(")", "")
    except IndexError:
        scrr = None
    
    # == user latest scrobbles
    scr_ = view_scr["recenttracks"]["track"]
    kek = ""
    for c in scr_:
        kek += f"    ♪ **{c['name']}** - __{c['artist']['#text']}__\n"

    # == user data
    data = view_data["user"]
    usuario = data["name"]
    user_url = data["url"]
    playcount = data["playcount"]
    country = data["country"]
    userr = f"<a href='{user_url}'>{usuario}</a>"
    text_ = f"**{userr} profile**\n"
    if playcount:
        text_ += f"**Scrobbles :** {playcount}\n"
    if country:
        text_ += f"**Country :** {country}\n"
    if scrr:
        text_ += f"**Loved Tracks :** {scrr}\n"
    if scr_:
        text_ += f"\n**Latest scrobbles :**\n{kek}"
    await message.reply(text_, disable_web_page_preview=True)
          

@megux.on_message(filters.command("status", prefixes=""))
@megux.on_message(filters.command(["lt", "lastfm", "lmu"], Config.TRIGGER))
@disableable_dec("lt")
async def last_user(c: megux, message: Message):
    query = input_str(message)
    user_ = message.from_user
    lastdb = await REG.find_one({"id_": user_.id})
    if not (lastdb or query):
        await message.reply("Me consta no meu banco de dados que você não é cadastrado, para se cadastrar digite /reg [username], se você não tem uma conta no last.fm entre em https://www.last.fm/join")
        return
    if query:
        user_lastfm = query
    else:
        user_lastfm = lastdb["last_data"]
    params = {
        "method": "user.getrecenttracks",
        "limit": 1,
        "extended": 1,
        "user": user_lastfm,
        "api_key": Config.LASTFM_API_KEY,
        "limit": 1,
        "format": "json",
    }
    try:
        view_data = await get_response.json(link=API, params=params)
    except ValueError:
        return await message.reply("__Error. Make sure you entered the correct username__")
    if "error" in view_data:
        return await message.reply(view_data["error"])
    recent_song = view_data["recenttracks"]["track"]
    if len(recent_song) == 0:
        if query:
            return await message.reply(f"__{user_lastfm} Não scrobbou nenhuma música__")
        else:
            return await message.reply("__Você não scrobbou nenhuma música__")
    try:
        song_ = recent_song[0]
        song_name = song_["name"]
        artist_name = song_["artist"]["name"]
        image_ = song_["image"][3].get("#text")
        params_ = {
            "method": "track.getInfo",
            "track": song_name,
            "artist": artist_name,
            "user": user_lastfm,
            "api_key": Config.LASTFM_API_KEY,
            "format": "json",
        }
    except KeyError:
        await message.reply("__Algo deu errado com essa conta do last.fm__")
        return
    try:
        view_data_ = await get_response.json(link=API, params=params_)
        get_track = view_data_["track"]
        get_scrob = int(get_track["userplaycount"])
        if get_scrob == 0:
            scrob = get_scrob + 1
        else:
            scrob =  get_scrob            
    except KeyError:
        scrob = "none"
    if image_:
        img = image_
    else:
        img = "https://telegra.ph/file/3ad207681d56059a7d90d.jpg"
    if song_.get("@attr"):
        listering = (
            ("Está ouvindo:")
            if scrob == "none"
            else (f"Está ouvindo pela <b>{scrob}ª vez:</b>")
        )
    elif scrob == "none":
        listering = "Estava ouvindo:"
    else:
        listering = f"Estava ouvindo pela <b>{scrob}ª vez:</b>"
    kek = f"<a href='{img}'>\u200c</a>"
    kek += f"<b>{user_.mention}</b> {listering}\n<b>{artist_name}</b> - {song_name}\n"
    loved = int(song_["loved"])
    if loved:
        kek += "❤️<i>Loved</i>"
    await message.reply(kek, disable_web_page_preview=False)
                    
            
