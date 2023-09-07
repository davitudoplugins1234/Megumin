import html

from gpytranslate import Translator
from pyrogram import filters
from pyrogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Message,
)

from megumin import megux
from megumin.utils import get_collection, get_string, disableable_dec, is_disabled, inline_handler  


tr = Translator()

images_thumb_url = "https://telegra.ph/file/83402d7a4ca7b186a4281.jpg"

# See https://cloud.google.com/translate/docs/languages
# fmt: off
LANGUAGES = [
    "af", "sq", "am", "ar", "hy",
    "az", "eu", "be", "bn", "bs",
    "bg", "ca", "ceb", "zh", "co",
    "hr", "cs", "da", "nl", "en",
    "eo", "et", "fi", "fr", "fy",
    "gl", "ka", "de", "el", "gu",
    "ht", "ha", "haw", "he", "iw",
    "hi", "hmn", "hu", "is", "ig",
    "id", "ga", "it", "ja", "jv",
    "kn", "kk", "km", "rw", "ko",
    "ku", "ky", "lo", "la", "lv",
    "lt", "lb", "mk", "mg", "ms",
    "ml", "mt", "mi", "mr", "mn",
    "my", "ne", "no", "ny", "or",
    "ps", "fa", "pl", "pt", "pa",
    "ro", "ru", "sm", "gd", "sr",
    "st", "sn", "sd", "si", "sk",
    "sl", "so", "es", "su", "sw",
    "sv", "tl", "tg", "ta", "tt",
    "te", "th", "tr", "tk", "uk",
    "ur", "ug", "uz", "vi", "cy",
    "xh", "yi", "yo", "zu",
]
# fmt: on


def get_tr_lang(text):
    if len(text.split()) > 0:
        lang = text.split()[0]
        if lang.split("-")[0] not in LANGUAGES:
            lang = "pt"
        if len(lang.split("-")) > 1 and lang.split("-")[1] not in LANGUAGES:
            lang = "pt"
    else:
        lang = "pt"
    return lang


@megux.on_message(filters.command("tr", prefixes=["/", "!"]))
@disableable_dec("tr")
async def translate(c: megux, m: Message):
    if await is_disabled(m.chat.id, "tr"):
        return
    text = m.text[4:]
    lang = get_tr_lang(text)

    text = text.replace(lang, "", 1).strip() if text.startswith(lang) else text

    if not text and m.reply_to_message:
        text = m.reply_to_message.text or m.reply_to_message.caption

    if not text:
        return await m.reply_text("`Vou traduzir o vento?!`")
        

    sent = await m.reply_text("Traduzindo...")
    langs = {}

    if len(lang.split("-")) > 1:
        langs["sourcelang"] = lang.split("-")[0]
        langs["targetlang"] = lang.split("-")[1]
    else:
        langs["targetlang"] = lang

    trres = await tr.translate(text, **langs)
    text = trres.text

    res = html.escape(text)
    await sent.edit_text("<b>Idioma:</b> {from_lang} -> {to_lang}\n<b>Tradução:</b> <code>{translation}</code>".format(
            from_lang=trres.lang, to_lang=langs["targetlang"], translation=res))


@megux.on_inline_query(filters.regex(r"^tr|translate"))
async def tr_inline(c: megux, q: InlineQuery):
    try:
        to_tr = q.query.split(None, 2)[2]
        source_language = await tr.detect(q.query.split(None, 2)[2])
        to_language = q.query.lower().split()[1]
        translation = await tr(
            to_tr, sourcelang=source_language, targetlang=to_language
        )
        await q.answer(
            [
                InlineQueryResultArticle(
                    title="Traduzir de {srclangformat} para {tolangformat}".format(
                        srclangformat=source_language, tolangformat=to_language
                    ),
                    description=f"{translation.text}",
                    input_message_content=InputTextMessageContent(
                        f"{translation.text}"
                    ),
                )
            ]
        )
    except IndexError:
        return


inline_handler.add_cmd("tr <lang> <text>", "A simple inline text translator", images_thumb_url, aliases=["translate"])
