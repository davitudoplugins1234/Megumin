import random
from re import findall

from pyrogram.types import (
    ForceReply,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

MAP_CATEGORY_PT = {
"Display": "Tela",

"Platform": "Plataforma",

"Memory": "Memória",

"Main Camera": "Câmera principal",

"Selfie camera": "Câmera frontal",

"Sound": "Som",

"Network": "Rede",

"Battery": "Bateria",

"Body": "Corpo",

"Launch": "Lançado",

"Comms": "Comunicações",

"Features": "Características",

"Misc": "Diversos",

"Tests": "Testes"
}

MAP_CATEGORY_EN = {
"Display": "Display",

"Platform": "Platform",

"Memory": "Memory",

"Main Camera": "Main camera",

"Selfie camera": "Frontal camera",

"Sound": "Sound",

"Network": "Network",

"Battery": "Battery",

"Body": "Body",

"Launch": "Launch",

"Comms": "Comms",

"Features": "Features",

"Misc": "Misc",

"Tests": "Tests"
}

MAP_CATEGORY_ES = {
  
  "Display": "Pantalla",
  
  "Platform": "Plataforma",
  
  "Memory": "Memoria",
  
  "Main Camera": "Cámara principal",
  
  "Selfie camera": "Cámara frontal",
  
  "Sound": "Sonido",
  
  "Network": "Red",
  
  "Battery": "Batería",
  
  "Body": "Cuerpo",
  
  "Launch": "Lanzamiento",
  
  "Comms": "Comunicaciones",
  
  "Features": "Características",
  
  "Misc": "Varios",
  
  "Tests": "Pruebas"
  
}

# funções futuras


def rand_array(array: list, string: bool = True):
    random_num = random.choice(array)
    return str(random_num) if string else random_num


def get_urls_from_text(text: str) -> bool:
    regex = r"""(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]
                [.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(
                \([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\
                ()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))""".strip()
    return [x[0] for x in findall(regex, str(text))]



def ikb(rows=[]):
    lines = []
    for row in rows:
        line = []
        for button in row:
            button = btn(*button)  # InlineKeyboardButton
            line.append(button)
        lines.append(line)
    return InlineKeyboardMarkup(inline_keyboard=lines)
    # return {'inline_keyboard': lines}


def btn(text, value, type="callback_data"):
    return InlineKeyboardButton(text, **{type: value})
    # return {'text': text, type: value}


# The inverse of above
def bki(keyboard):
    lines = []
    for row in keyboard.inline_keyboard:
        line = []
        for button in row:
            button = ntb(button)  # btn() format
            line.append(button)
        lines.append(line)
    return lines
    # return ikb() format


def ntb(button):
    for btn_type in [
        "callback_data",
        "url",
        "switch_inline_query",
        "switch_inline_query_current_chat",
        "callback_game",
    ]:
        value = getattr(button, btn_type)
        if value:
            break
    button = [button.text, value]
    if btn_type != "callback_data":
        button.append(btn_type)
    return button
    # return {'text': text, type: value}


def kb(rows=[], **kwargs):
    lines = []
    for row in rows:
        line = []
        for button in row:
            button_type = type(button)
            if button_type == str:
                button = KeyboardButton(button)
            elif button_type == dict:
                button = KeyboardButton(**button)

            line.append(button)
        lines.append(line)
    return ReplyKeyboardMarkup(keyboard=lines, **kwargs)


kbtn = KeyboardButton


def force_reply(selective=True):
    return ForceReply(selective=selective)


def array_chunk(input, size):
    return [input[i : i + size] for i in range(0, len(input), size)]
