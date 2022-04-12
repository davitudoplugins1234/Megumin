import os
import shutil
import tempfile
import ffmpeg
import re
import math
import httpx


from PIL import Image


from pyrogram import filters, emoji
from pyrogram.errors import PeerIdInvalid, StickersetInvalid
from pyrogram.raw.functions.messages import GetStickerSet, SendMedia
from pyrogram.raw.functions.stickers import AddStickerToSet, CreateStickerSet
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from typing import Tuple, Callable
from functools import wraps, partial
from pyrogram.raw.types import (
    DocumentAttributeFilename,
    InputDocument,
    InputMediaUploadedDocument,
    InputStickerSetItem,
    InputStickerSetShortName,
)

def get_emoji_regex():
    e_list = [
        getattr(emoji, e).encode("unicode-escape").decode("ASCII")
        for e in dir(emoji)
        if not e.startswith("_")
    ]
    # to avoid re.error excluding char that start with '*'
    e_sort = sorted([x for x in e_list if not x.startswith("*")], reverse=True)
    # Sort emojis by length to make sure multi-character emojis are
    # matched first
    pattern_ = f"({'|'.join(e_sort)})"
    return re.compile(pattern_)


EMOJI_PATTERN = get_emoji_regex()


SUPPORTED_TYPES = ["jpeg", "png", "webp"]
CHAT_LOGS = -1001556292785
http = httpx.AsyncClient()


from megumin import megux, Config


@megux.on_message(filters.command(["getsticker"], prefixes=["/", "!"]))
async def getsticker_(c: megux, m: Message):
    sticker = m.reply_to_message.sticker

    if sticker:
        if sticker.is_animated:
            await m.reply_text("Sticker animado não é suportado!")
        elif not sticker.is_animated:
            with tempfile.TemporaryDirectory() as tempdir:
                path = os.path.join(tempdir, "getsticker")
            sticker_file = await c.download_media(
                message=m.reply_to_message,
                file_name=f"{path}/{sticker.set_name}.png",
            )
            await m.reply_to_message.reply_document(
                document=sticker_file,
                caption=(
                    f"<b>Emoji:</b> {sticker.emoji}\n"
                    f"<b>Sticker ID:</b> <code>{sticker.file_id}</code>\n\n"
                    f"<b>Send by:</b> @WhiterKangBOT"
                ),
            )
            shutil.rmtree(tempdir, ignore_errors=True)
    else:
        await m.reply_text("Isso não é um sticker!")


@megux.on_message(filters.command("stickerid", prefixes=["/", "!"]) & filters.reply)
async def getstickerid(c: megux, m: Message):
    if m.reply_to_message.sticker:
        await m.reply_text(
            "O id deste sticker é: <code>{stickerid}</code>".format(
                stickerid=m.reply_to_message.sticker.file_id
            )
        )


@megux.on_message(filters.command("kang", prefixes=["/", "!"]))
async def kang_sticker(c: megux, m: Message):
    if m.chat.id == int(-1001471874620):
       return
    prog_msg = await m.reply_text("Roubando o sticker...")
    user = await c.get_me()
    bot_username = user.username
    sticker_emoji = "🤔"
    packnum = 0
    packname_found = False
    resize = False
    animated = False
    videos = False
    reply = m.reply_to_message
    user = await c.resolve_peer(m.from_user.username or m.from_user.id)

    elif reply and reply.media:
        if reply.photo:
            resize = True
        elif reply.animation:
            videos = True
            convert = True
        elif reply.document:
            if "image" in reply.document.mime_type:
                # mime_type: image/webp
                resize = True
            elif "video/mp4" in reply.document.mime_type:
                # mime_type: application/v
                videos = True
            elif "tgsticker" in reply.document.mime_type:
                # mime_type: application/v
                animated = True

        elif reply.sticker:
            if not reply.sticker.file_name:
                return await prog_msg.edit_text(
                    "O sticker não tem nome."
                )
            if reply.sticker.emoji:
                sticker_emoji = reply.sticker.emoji
            animated = reply.sticker.is_animated
            videos = reply.sticker.is_video
            if videos:
                convert = False
            else:
                if not reply.sticker.file_name.endswith(".tgs"):
                    resize = True
        else:
            return await prog_msg.edit_text(
                "<code>Não suportado!</code>"
            )

        pack_prefix = "anim" if animated else "vid" if videos else "a"
        packname = f"{pack_prefix}_{m.from_user.id}_by_{bot_username}"

        if len(m.command) > 1:
            if m.command[1].isdigit() and int(m.command[1]) > 0:
                # provide pack number to kang in desired pack
                packnum = m.command.pop(1)
                packname = f"{pack_prefix}{packnum}_{m.from_user.id}_by_{bot_username}"
            if len(m.command) > 1:
                # matches all valid emojis in input
                sticker_emoji = (
                    "".join(set(EMOJI_PATTERN.findall("".join(m.command[1:]))))
                    or sticker_emoji
                )
        filename = await c.download_media(m.reply_to_message)
        if not filename:
            # Failed to download
            await prog_msg.delete()
            return
    elif m.entities and len(m.entities) > 1:
        packname = f"c{m.from_user.id}_by_{bot_username}"
        pack_prefix = "a"
        # searching if image_url is given
        img_url = None
        filename = "sticker.png"
        for y in m.entities:
            if y.type == "url":
                img_url = m.text[y.offset : (y.offset + y.length)]
                break
        if not img_url:
            await prog_msg.delete()
            return
        try:
            r = await http.get(img_url)
            if r.status_code == 200:
                with open(filename, mode="wb") as f:
                    f.write(r.read())
        except Exception as r_e:
            return await prog_msg.edit_text(f"{r_e.__class__.__name__} : {r_e}")
        if len(m.command) > 2:
            # m.command[1] is image_url
            if m.command[2].isdigit() and int(m.command[2]) > 0:
                packnum = m.command.pop(2)
                packname = f"a{packnum}_{m.from_user.id}_by_{bot_username}"
            if len(m.command) > 2:
                sticker_emoji = (
                    "".join(set(EMOJI_PATTERN.findall("".join(m.command[2:]))))
                    or sticker_emoji
                )
            resize = True
    else:
        return await prog_msg.edit_text("Quer que eu adivinhe o sticker? Por Favor marque um sticker.")
    try:
        if resize:
            filename = resize_image(filename)
        elif convert:
            filename = convert_video(filename)
        max_stickers = 50 if animated else 120
        while not packname_found:
            try:
                stickerset = await c.send(
                    GetStickerSet(
                        stickerset=InputStickerSetShortName(short_name=packname),
                        hash=0,
                    )
                )
                if stickerset.set.count >= max_stickers:
                    packnum += 1
                    packname = (
                        f"{pack_prefix}_{packnum}_{m.from_user.id}_by_{bot_username}"
                    )
                else:
                    packname_found = True
            except StickersetInvalid:
                break
        file = await c.save_file(filename)
        media = await c.send(
            SendMedia(
                peer=(await c.resolve_peer(CHAT_LOGS)),
                media=InputMediaUploadedDocument(
                    file=file,
                    mime_type=c.guess_mime_type(filename),
                    attributes=[DocumentAttributeFilename(file_name=filename)],
                ),
                message=f"#Sticker kang by UserID -> {m.from_user.id}",
                random_id=c.rnd_id(),
            ),
        )
        msg_ = media.updates[-1].message
        stkr_file = msg_.media.document
        if packname_found:
            await prog_msg.edit_text("<code>Usando o pacote de stickers existente...</code>")
            await c.send(
                AddStickerToSet(
                    stickerset=InputStickerSetShortName(short_name=packname),
                    sticker=InputStickerSetItem(
                        document=InputDocument(
                            id=stkr_file.id,
                            access_hash=stkr_file.access_hash,
                            file_reference=stkr_file.file_reference,
                        ),
                        emoji=sticker_emoji,
                    ),
                )
            )
        else:
            await prog_msg.edit_text("<b>Criando um novo pacote de stickers...</b>")
            stkr_title = f"@{m.from_user.username[:32]}'s "
            if animated:
                stkr_title += "WhiterKang AnimPack"
            elif videos:
                stkr_title += "WhiterKang VidPack"
            if packnum != 0:
                stkr_title += f" v{packnum}"
            try:
                await c.send(
                    CreateStickerSet(
                        user_id=user,
                        title=stkr_title,
                        short_name=packname,
                        stickers=[
                            InputStickerSetItem(
                                document=InputDocument(
                                    id=stkr_file.id,
                                    access_hash=stkr_file.access_hash,
                                    file_reference=stkr_file.file_reference,
                                ),
                                emoji=sticker_emoji,
                            )
                        ],
                        animated=animated,
                        videos=videos,
                    )
                )
            except PeerIdInvalid:
                return await prog_msg.edit_text(
                    "Parece que você nunca interagiu comigo no chat privado, é necessário que faça isso primeiro. .",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "/start", url=f"https://t.me/{bot_username}?start"
                                )
                            ]
                        ]
                    ),
                )
    except Exception as all_e:
        await prog_msg.edit_text(f"{all_e.__class__.__name__} : {all_e}")
    else:
        await prog_msg.edit_text(
            "<b>Sticker roubado com sucesso!</b>\n<a href='t.me/addstickers/{}'>Pack</a>.\n<b>Emoji:</b> {}".format(packname, sticker_emoji)
        )
        # Cleanup
        await c.delete_messages(chat_id=CHAT_LOGS, message_ids=msg_.id, revoke=True)
        try:
            os.remove(filename)
        except OSError:
            pass


def resize_image(filename: str) -> str:
    im = Image.open(filename)
    maxsize = 512
    scale = maxsize / max(im.width, im.height)
    sizenew = (int(im.width * scale), int(im.height * scale))
    im = im.resize(sizenew, Image.NEAREST)
    downpath, f_name = os.path.split(filename)
    # not hardcoding png_image as "sticker.png"
    png_image = os.path.join(downpath, f"{f_name.split('.', 1)[0]}.png")
    im.save(png_image, "PNG")
    if png_image != filename:
        os.remove(filename)
    return png_image


def convert_video(filename: str) -> str:
    downpath, f_name = os.path.split(filename)
    webm_video = os.path.join(downpath, f"{f_name.split('.', 1)[0]}.webm")
    webm_video = os.path.join(downpath, f"{f_name.split('.', 1)[0]}.webm")
    stream = ffmpeg.input(filename).filter("fps", fps=30, round="up").trim(duration=3)
    stream = ffmpeg.output(
        stream, webm_video, s="512x512", vcodec="vp9", video_bitrate="500k"
    )
    ffmpeg.run(stream, overwrite_output=True, quiet=True)
    if webm_video != filename:
        os.remove(filename)
    return webm_video
