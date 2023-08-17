import time
import psutil
import humanize
import platform
import asyncio 

from pyrogram import filters
from typing import Union
from pyrogram.enums import ChatType
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from megumin import megux, version
from megumin import START_TIME
from megumin.utils import get_collection, time_formatter, get_string, add_lang, find_user, add_user

CHAT_LOGS = -1001556292785
GROUPS = get_collection("GROUPS")
USERS = get_collection("USERS")

sm = psutil.swap_memory()
uname = platform.uname() 


@megux.on_message(filters.command("start", prefixes=["/", "!"]))
async def start_(c: megux, message: Message): 
    if not message.chat.type == ChatType.PRIVATE:
        return await message.reply(await get_string(message.chat.id, "START_NO_PRIVATE"))
    keyboard = InlineKeyboardMarkup(
        [
            [
              InlineKeyboardButton(text=await get_string(message.chat.id, "button_lang"), callback_data="lang_menu"),
            ],
            [
              InlineKeyboardButton(text=await get_string(message.chat.id, "HELP_BNT"), callback_data="help_menu"),
              InlineKeyboardButton(text=await get_string(message.chat.id, "REPO_BNT"), url="https://github.com/davitudoplugins1234/WhiterKang")
            ],
            [
              InlineKeyboardButton(text="Info", callback_data="infos"),
              InlineKeyboardButton(text=await get_string(message.chat.id, "SUP_BNT"), url="https://t.me/fnixsup"),
            ],
            [                
              InlineKeyboardButton(
                  text=await get_string(message.chat.id, "ADD_BNT"),
                  url=f"https://t.me/whiterkangbot?startgroup=new",
               ),
            ],
        ]
    )
    gif = "https://telegra.ph/file/576f9c3193a1dade06bce.gif"
    msg = await get_string(message.chat.id or message.message.chat.id, "START")
    await message.reply_animation(gif, caption=msg, reply_markup=keyboard)
    user_id = message.from_user.id
    if not await find_user(user_id):
        await add_user(user_id)

    @megux.on_callback_query(filters.regex(pattern=r"^start_back$"))
    async def start_back(client: megux, cb: CallbackQuery):
        await megux.edit_message_caption(
            chat_id=cb.message.chat.id,
            message_id=cb.message.id,
            caption=await get_string(cb.message.chat.id, "START"),
            reply_markup=InlineKeyboardMarkup(
        [
            [
              InlineKeyboardButton(text=await get_string(cb.message.chat.id, "button_lang"), callback_data="lang_menu"),
            ],
            [
              InlineKeyboardButton(text=await get_string(cb.message.chat.id, "HELP_BNT"), callback_data="help_menu"),
              InlineKeyboardButton(text=await get_string(cb.message.chat.id, "REPO_BNT"), url="https://github.com/davitudoplugins1234/WhiterKang")
            ],
            [
              InlineKeyboardButton(text="Info", callback_data="infos"),
              InlineKeyboardButton(text=await get_string(cb.message.chat.id, "SUP_BNT"), url="https://t.me/fnixsup"),
            ],
            [                
              InlineKeyboardButton(
                  text=await get_string(cb.message.chat.id, "ADD_BNT"),
                  url=f"https://t.me/whiterkangbot?startgroup=new",
               ),
            ],
        ]
    )
)
        


    @megux.on_callback_query(filters.regex(pattern=r"^infos$"))
    async def infos(client: megux, cb: CallbackQuery):
        info_text = f"""
╔════「 Sobre  WhiterKang 」
╠ Versão : `{version.__megumin_version__}`
╠ Uptime : `{time_formatter(time.time() - START_TIME)}`
╠ System : `{client.system_version}`
╠ Cpu : `{psutil.cpu_percent(interval=1)}%`
╠ Ram : `{psutil.virtual_memory().percent}%`
╠ Disco : `{psutil.disk_usage("/").percent}%`
╠ Python : `{version.__python_version__}`
╠ Pyrogram : `{version.__pyro_version__}`
╚═╗
    """
        button = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Voltar", callback_data="start_back"),
                ]
            ]
        )
        await megux.edit_message_caption(
            chat_id=cb.message.chat.id,
            message_id=cb.message.id,
            caption=info_text,
            reply_markup=button,
        )


    @megux.on_callback_query(filters.regex(pattern=r"^lang_menu$"))
    async def infos(client: megux, cb: CallbackQuery):
        info_text = await get_string(cb.message.chat.id, "select_lang")
        button = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🇺🇸 English", callback_data="en_lang"),
                    InlineKeyboardButton("🇧🇷 Português", callback_data="pt_lang"),
                    InlineKeyboardButton("🇪🇸 Español", callback_data="es_lang"),
                ],
                [
                    InlineKeyboardButton(await get_string(cb.message.chat.id, "BACK_BNT"), callback_data="start_back"),
                ]
            ]
        )
        await megux.edit_message_caption(
            chat_id=cb.message.chat.id,
            message_id=cb.message.id,
            caption=info_text.format(await get_string(cb.message.chat.id, "language_flag")),
            reply_markup=button,
        )


    @megux.on_callback_query(filters.regex(pattern=r"^pt_lang$"))
    async def infos(client: megux, cb: CallbackQuery):
        await add_lang(cb.message.chat.id, "pt")
        await asyncio.sleep(1.5)
        info_text = await get_string(cb.message.chat.id, "language_switch_success")
        button = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(await get_string(cb.message.chat.id, "BACK_BNT"), callback_data="start_back"),
                ]
            ]
        )
        await megux.edit_message_caption(
            chat_id=cb.message.chat.id,
            message_id=cb.message.id,
            caption=info_text.format(await get_string(cb.message.chat.id, "language_flag")),
            reply_markup=button,
        )


    @megux.on_callback_query(filters.regex(pattern=r"^en_lang$"))
    async def infos(client: megux, cb: CallbackQuery):
        await add_lang(cb.message.chat.id, "en")
        await asyncio.sleep(1.5)
        info_text = await get_string(cb.message.chat.id, "language_switch_success")
        button = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(await get_string(cb.message.chat.id, "BACK_BNT"), callback_data="start_back"),
                ]
            ]
        )
        await megux.edit_message_caption(
            chat_id=cb.message.chat.id,
            message_id=cb.message.id,
            caption=info_text.format(await get_string(cb.message.chat.id, "language_flag")),
            reply_markup=button,
        )


    @megux.on_callback_query(filters.regex(pattern=r"^es_lang$"))
    async def infos(client: megux, cb: CallbackQuery):
        await add_lang(cb.message.chat.id, "es")
        await asyncio.sleep(1.5)
        info_text = await get_string(cb.message.chat.id, "language_switch_success")
        button = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(await get_string(cb.message.chat.id, "BACK_BNT"), callback_data="start_back"),
                ]
            ]
        )
        await megux.edit_message_caption(
            chat_id=cb.message.chat.id,
            message_id=cb.message.id,
            caption=info_text.format(await get_string(cb.message.chat.id, "language_flag")),
            reply_markup=button,
        )


    @megux.on_callback_query(filters.regex(pattern=r"^help_menu$"))
    async def infos(client: megux, cb: CallbackQuery):
        info_text = await get_string(cb.message.chat.id, "HELP_MSG")
        button = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(await get_string(cb.message.chat.id, "BNT_1"), callback_data="admin_help_button"),
                    InlineKeyboardButton(await get_string(cb.message.chat.id, "BNT_2"), callback_data="anilist_help_button"),
                    InlineKeyboardButton(await get_string(cb.message.chat.id, "BNT_3"), callback_data="android_help_button"),
                ],
                [
                    InlineKeyboardButton(await get_string(cb.message.chat.id, "BNT_4"), callback_data="misc_help_button"),
                    InlineKeyboardButton(await get_string(cb.message.chat.id, "BNT_5"), callback_data="geral_help_button"),
                    InlineKeyboardButton(await get_string(cb.message.chat.id, "BNT_6"), callback_data="last_help_button"),
                ],
                [
                    InlineKeyboardButton(await get_string(cb.message.chat.id, "BNT_7"), callback_data="notes_help_button"),
                    InlineKeyboardButton(await get_string(cb.message.chat.id, "BNT_8"), callback_data="purges_help_button"), 
                    InlineKeyboardButton(await get_string(cb.message.chat.id, "BNT_9"), callback_data="yt_help_button"),
                ],
                [
                    InlineKeyboardButton(await get_string(cb.message.chat.id, "BNT_10"), callback_data="bans_help_button"),
                    InlineKeyboardButton(await get_string(cb.message.chat.id, "BNT_11"), callback_data="git_help_button"),
                    InlineKeyboardButton(await get_string(cb.message.chat.id, "BNT_12"), callback_data="memes_help_button"),
                ],
                [
                    InlineKeyboardButton(await get_string(cb.message.chat.id, "BNT_13"), callback_data="tr_help_button"),
                    InlineKeyboardButton(await get_string(cb.message.chat.id, "BNT_14"), callback_data="stickers_help_button"),
                    InlineKeyboardButton(await get_string(cb.message.chat.id, "BNT_15"), callback_data="disable_help_button"),
                ],
                [
                    InlineKeyboardButton(await get_string(cb.message.chat.id, "BNT_16"), callback_data="welcome_help_button"),
                    InlineKeyboardButton(await get_string(cb.message.chat.id, "BNT_17"), callback_data="warnings_help_button"),
                    InlineKeyboardButton(await get_string(cb.message.chat.id, "BNT_18"), callback_data="filters_help_button"),
                ],
                [
                    InlineKeyboardButton(await get_string(cb.message.chat.id, "BACK_BNT"), callback_data="start_back"),
                ],
            ]
        )
        await megux.edit_message_caption(
            chat_id=cb.message.chat.id,
            message_id=cb.message.id,
            caption=info_text,
            reply_markup=button,
        )

    @megux.on_callback_query(filters.regex(pattern=r"^start_back$"))
    async def start_back(client: megux, cb: CallbackQuery):
        await megux.edit_message_caption(
            chat_id=cb.message.chat.id,
            message_id=cb.message.id,
            caption=await get_string(cb.message.chat.id, "START"),
            reply_markup=keyboard,
        )


    @megux.on_callback_query(filters.regex(pattern=r"^admin_help_button$"))
    async def infos(client: megux, cb: CallbackQuery):
        info_text = await get_string(cb.message.chat.id, "HELP_ADMIN")
        button = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(await get_string(cb.message.chat.id, "BACK_BNT"), callback_data="help_menu"),
                ]
            ]
        )
        await megux.edit_message_caption(
            chat_id=cb.message.chat.id,
            message_id=cb.message.id,
            caption=info_text,
            reply_markup=button,
        )


    @megux.on_callback_query(filters.regex(pattern=r"^anilist_help_button$"))
    async def infos(client: megux, cb: CallbackQuery):
        info_text = await get_string(cb.message.chat.id, "HELP_ANILIST")
        button = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(await get_string(cb.message.chat.id, "BACK_BNT"), callback_data="help_menu"),
                ]
            ]
        )
        await megux.edit_message_caption(
            chat_id=cb.message.chat.id,
            message_id=cb.message.id,
            caption=info_text,
            reply_markup=button,
        )


    @megux.on_callback_query(filters.regex(pattern=r"^android_help_button$"))
    async def infos(client: megux, cb: CallbackQuery):
        info_text = await get_string(cb.message.chat.id, "HELP_ANDROID")
        button = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(await get_string(cb.message.chat.id, "BACK_BNT"), callback_data="help_menu"),
                ]
            ]
        )
        await megux.edit_message_caption(
            chat_id=cb.message.chat.id,
            message_id=cb.message.id,
            caption=info_text,
            reply_markup=button,
        )


    @megux.on_callback_query(filters.regex(pattern=r"^last_help_button$"))
    async def infos(client: megux, cb: CallbackQuery):
        info_text = f"""
Aqui está a ajuda para o módulo <b>LastFm</b>:

Antes de tudo você deve estar registrado no lastfm

• /lt ou /lastfm para mostrar oque você esta ouvindo agora.
• /reg ou /setuser para definir seu usuario LastFM.
• /deluser ou /duser para remover seu nome de usuario do banco de dados.
    """
        button = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(await get_string(cb.message.chat.id, "BACK_BNT"), callback_data="help_menu"),
                ]
            ]
        )
        await megux.edit_message_caption(
            chat_id=cb.message.chat.id,
            message_id=cb.message.id,
            caption=info_text,
            reply_markup=button,
        )


    @megux.on_callback_query(filters.regex(pattern=r"^notes_help_button$"))
    async def infos(client: megux, cb: CallbackQuery):
        info_text = await get_string(cb.message.chat.id, "HELP_NOTES")
        button = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(await get_string(cb.message.chat.id, "BACK_BNT"), callback_data="help_menu"),
                ]
            ]
        )
        await megux.edit_message_caption(
            chat_id=cb.message.chat.id,
            message_id=cb.message.id,
            caption=info_text,
            reply_markup=button,
        )


    @megux.on_callback_query(filters.regex(pattern=r"^tr_help_button$"))
    async def infos(client: megux, cb: CallbackQuery):
        info_text = await get_string(cb.message.chat.id, "HELP_TR")
        button = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(await get_string(cb.message.chat.id, "BACK_BNT"), callback_data="help_menu"),
                ]
            ]
        )
        await megux.edit_message_caption(
            chat_id=cb.message.chat.id,
            message_id=cb.message.id,
            caption=info_text,
            reply_markup=button,
        )


    @megux.on_callback_query(filters.regex(pattern=r"^yt_help_button$"))
    async def infos(client: megux, cb: CallbackQuery):
        info_text = await get_string(cb.message.chat.id, "HELP_YOUTUBE")
        button = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(await get_string(cb.message.chat.id, "BACK_BNT"), callback_data="help_menu"),
                ]
            ]
        )
        await megux.edit_message_caption(
            chat_id=cb.message.chat.id,
            message_id=cb.message.id,
            caption=info_text,
            reply_markup=button,
        )


    @megux.on_callback_query(filters.regex(pattern=r"^bans_help_button$"))
    async def infos(client: megux, cb: CallbackQuery):
        info_text = await get_string(cb.message.chat.id, "HELP_BANS")
        button = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(await get_string(cb.message.chat.id, "BACK_BNT"), callback_data="help_menu"),
                ]
            ]
        )
        await megux.edit_message_caption(
            chat_id=cb.message.chat.id,
            message_id=cb.message.id,
            caption=info_text,
            reply_markup=button,
        )


    @megux.on_callback_query(filters.regex(pattern=r"^git_help_button$"))
    async def infos(client: megux, cb: CallbackQuery):
        info_text = f"""
Aqui está a ajuda para o módulo **GitHub**:

• /github Retorna informações sobre um usuário ou organização do GitHub.
    """
        button = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(await get_string(cb.message.chat.id, "BACK_BNT"), callback_data="help_menu"),
                ]
            ]
        )
        await megux.edit_message_caption(
            chat_id=cb.message.chat.id,
            message_id=cb.message.id,
            caption=info_text,
            reply_markup=button,
        )


    @megux.on_callback_query(filters.regex(pattern=r"^disable_help_button$"))
    async def infos(client: megux, cb: CallbackQuery):
        info_text = await get_string(cb.message.chat.id, "HELP_DISABLE")
        button = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(await get_string(cb.message.chat.id, "BACK_BNT"), callback_data="help_menu"),
                ]
            ]
        )
        await megux.edit_message_caption(
            chat_id=cb.message.chat.id,
            message_id=cb.message.id,
            caption=info_text,
            reply_markup=button,
        )



    @megux.on_callback_query(filters.regex(pattern=r"^geral_help_button$"))
    async def infos(client: megux, cb: CallbackQuery):
        info_text = f"""
✨ Geral

• /ban  Bane a um usuário.
• /unban Desbane a um usuário.
• /kick Chute o usuário.
• /mute Silencia o usuário.
• /purge Limpa seu grupo.
• /del Deleta a mensagem que você respondeu.
• /zombies Bane contas excluídas do grupo 
• /cota : Veja a cotação do Dólar, Euro, BTC
• /cep : (cep) Busque um CEP
• /ddd : Busque um DDD
• /clima ou /weather  ( cidade ) Busque o clima para uma cidade.
• /device : Busque um aparelho pelo codename.
• /app : Busque um app da PlayStore. 
• /setuser : Defina seu username.
• /lt : Veja que musica você está scobblando.
• /deluser : Apague seu username lastfm do meu banco de dados.
• /github Retorna informações sobre um usuário ou organização do GitHub.
• /tr (código de idioma) <b>Texto<b> ou mensagem respondida.
• /getsticker Responda a um adesivo para eu enviar o PNG e as informações do sticker.
    """
        button = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(await get_string(cb.message.chat.id, "BACK_BNT"), callback_data="help_menu"),
                ]
            ]
        )
        await megux.edit_message_caption(
            chat_id=cb.message.chat.id,
            message_id=cb.message.id,
            caption=info_text,
            reply_markup=button,
        )


    @megux.on_callback_query(filters.regex(pattern=r"^memes_help_button$"))
    async def infos(client: megux, cb: CallbackQuery):
        info_text = f"""
Aqui está a ajuda para o módulo **Memes**:

• /slap Dá um tapa no usuário.
• /insults Insulta alguém com um insulto aleatório de minhas strings.
• /runs Responde uma sequência aleatória de minhas strings.
• /bird ou /passaro Envia a foto de um pássaro.
• /dog Envia a foto de um cachorro.
• /cat Envia a foto de um gato.
• /fox Envia a foto de uma raposa.
• /redpanda ou /rpanda Envia a foto de um panda vermelho.
• /panda Envia a foto de um panda.
• /vapor ｖａｐｏｒｗａｖｅ.
    """
        button = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(await get_string(cb.message.chat.id, "BACK_BNT"), callback_data="help_menu"),
                ]
            ]
        )
        await megux.edit_message_caption(
            chat_id=cb.message.chat.id,
            message_id=cb.message.id,
            caption=info_text,
            reply_markup=button,
        )


    @megux.on_callback_query(filters.regex(pattern=r"^misc_help_button$"))
    async def infos(client: megux, cb: CallbackQuery):
        info_text = await get_string(cb.message.chat.id, "HELP_MISC")
        button = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(await get_string(cb.message.chat.id, "BACK_BNT"), callback_data="help_menu"),
                ]
            ]
        )
        await megux.edit_message_caption(
            chat_id=cb.message.chat.id,
            message_id=cb.message.id,
            caption=info_text,
            reply_markup=button,
        )


    @megux.on_callback_query(filters.regex(pattern=r"^purges_help_button$"))
    async def infos(client: megux, cb: CallbackQuery):
        info_text = f"""
Aqui está a ajuda para o módulo <b>Purges</b>:

• /purge Exclui todas as mensagens desde a marcada até a última mensagem.
• /del Exclui a mensagem que você respondeu. 
    """
        button = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(await get_string(cb.message.chat.id, "BACK_BNT"), callback_data="help_menu"),
                ]
            ]
        )
        await megux.edit_message_caption(
            chat_id=cb.message.chat.id,
            message_id=cb.message.id,
            caption=info_text,
            reply_markup=button,
        )


    @megux.on_callback_query(filters.regex(pattern=r"^stickers_help_button$"))
    async def infos(client: megux, cb: CallbackQuery):
        info_text = await get_string(cb.message.chat.id, "HELP_STICKERS")
        button = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(await get_string(cb.message.chat.id, "BACK_BNT"), callback_data="help_menu"),
                ]
            ]
        )
        await megux.edit_message_caption(
            chat_id=cb.message.chat.id,
            message_id=cb.message.id,
            caption=info_text,
            reply_markup=button,
        )

    @megux.on_callback_query(filters.regex(pattern=r"^welcome_help_button$"))
    async def infos(client: megux, cb: CallbackQuery):
        info_text = await get_string(cb.message.chat.id, "HELP_WELCOME")
        button = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(await get_string(cb.message.chat.id, "BACK_BNT"), callback_data="help_menu"),
                ]
            ]
        )
        await megux.edit_message_caption(
            chat_id=cb.message.chat.id,
            message_id=cb.message.id,
            caption=info_text,
            reply_markup=button,
        )

    @megux.on_callback_query(filters.regex(pattern=r"^warnings_help_button$"))
    async def infos(client: megux, cb: CallbackQuery):
        info_text = await get_string(cb.message.chat.id, "HELP_WARNS")
        button = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(await get_string(cb.message.chat.id, "BACK_BNT"), callback_data="help_menu"),
                ]
            ]
        )
        await megux.edit_message_caption(
            chat_id=cb.message.chat.id,
            message_id=cb.message.id,
            caption=info_text,
            reply_markup=button,
        )            
   

    @megux.on_callback_query(filters.regex(pattern=r"^filters_help_button$"))
    async def infos(client: megux, cb: CallbackQuery):
        info_text = await get_string(cb.message.chat.id, "HELP_FILTERS")
        button = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(await get_string(cb.message.chat.id, "BACK_BNT"), callback_data="help_menu"),
                ]
            ]
        )
        await megux.edit_message_caption(
            chat_id=cb.message.chat.id,
            message_id=cb.message.id,
            caption=info_text,
            reply_markup=button,
        )
        
        
@megux.on_message(filters.new_chat_members)
async def thanks_for(c: megux, m: Message):
    user = (
        f"<a href='tg://user?id={m.from_user.id}'>{m.from_user.first_name}</a>")
    gp_title = m.chat.title
    gp_id = m.chat.id

    text_add = f"#NEW_GROUP #LOGS\n\n**Grupo**: __{gp_title}__\n**ID:** __{gp_id}__\n**User:** __{user}__"
    if m.chat.username:
        text_add += f"**\nUsername:** @{m.chat.username}"
    if c.me.id in [x.id for x in m.new_chat_members]:
        await c.send_message(chat_id=CHAT_LOGS, text=text_add)
        await c.send_message(
            chat_id=m.chat.id,
            text=("""
__Olá pessoal obrigado por me adicionar aqui!__\n**Eu sou o WhiterKang**, Prazer em conhece-los.
"""
                  ),
            disable_notification=True,
        )
        found = await GROUPS.find_one({"id_": gp_id})
        if not found:
            await asyncio.gather(
                GROUPS.insert_one({"id_": gp_id, "title": gp_title}))    


@megux.on_message(filters.left_chat_member)
async def thanks_for(c: megux, m: Message):
    gp_title = m.chat.title
    gp_id = m.chat.id
    text_left = f"#Whiter #LEFT_GROUP #LOGS\n\n**Group**: __{gp_title}__\n**ID:** __{gp_id}__"
    if m.chat.username:
        text_left += f"**\nUsername:** @{m.chat.username}"
    if c.me.id == m.left_chat_member.id:
        found = await GROUPS.find_one({"id_": gp_id})
        if found:
            await asyncio.gather(
                GROUPS.delete_one({"id_": gp_id, "title": gp_title}),
                c.send_log(
                    text_left,
                    disable_notification=False,
                    disable_web_page_preview=True,
                )
            )
        else:
            return


@megux.on_message(filters.left_chat_member)
async def thanks_owner(c: megux, m: Message):
    gp_title = m.chat.title
    gp_id = m.chat.id
    id = "1715384854"
    text_left = f"#OWNER #LEFT_GROUP #LOGS\n\n**Grupo**: __{gp_title}__\n**ID:** __{gp_id}__"
    if m.chat.username:
        text_left += f"**\nUsername:** @{m.chat.username}"
    if id == m.left_chat_member.id:
        await c.send_message(
            chat_id=m.chat.id,
            text=("""
Bem, meu mestre se foi, a festa acabou!
"""
                  ),
            disable_notification=True,
        )
        await asyncio.gather(
            c.send_log(
                text_left,
                disable_notification=False,
                disable_web_page_preview=True,
            )
        )
    else:
        return
