import requests
import asyncio 

from pyrogram import filters
from pyrogram.types import Message

from megumin import megux, Config

@megux.on_message(filters.command(["cota"], Config.TRIGGER))
async def pegar_cotacoes(_, message: Message):
    req = requests.get("https://economia.awesomeapi.com.br/last/USD-BRL,EUR-BRL,GBP-BRL,JPY-BRL,BTC-BRL,ETH-BRL,XRP-BRL,DOGE-BRL,ARS-BRL,RUB-BRL")

    res = req.json()

    cotacao_dolar = res['USDBRL']['bid']
    dat_dolar = res['USDBRL']['create_date']
    var_dolar = res['USDBRL']['varBid']
    cotacao_euro = res['EURBRL']['bid']
    dat_euro = res['EURBRL']['create_date']
    var_euro = res['EURBRL']['varBid']
    cotacao_btc = res['BTCBRL']['bid']
    dat_btc = res['BTCBRL']['create_date']
    var_btc = res['BTCBRL']['varBid']
    cotacao_iene = res['JPYBRL']['bid']
    dat_iene = res['JPYBRL']['create_date']
    var_iene = res['JPYBRL']['varBid']
    cotacao_doge = res['DOGEBRL']['bid']
    dat_doge = res['DOGEBRL']['create_date']
    var_doge = res['DOGEBRL']['varBid']
    cotacao_ars = res['ARSBRL']['bid']
    dat_ars = res['ARSBRL']['create_date']
    var_ars = res['ARSBRL']['varBid']
    cotacao_rub = res['RUBBRL']['bid']
    dat_rub = res['RUBBRL']['create_date']
    var_rub = res['RUBBRL']['varBid']

    obting_info = await message.reply(f"<i>Obtendo informações sobre as moedas...</i>")
    await asyncio.sleep(0.3)
    await obting_info.delete()

    result = "<b>Cotação das moedas:</b>\n\n💵 <b>Dólar:</b> R$ <code>{}</code>\n🗓 <b>Data:</b>  <code>{}</code>\n📊 <b>Variação:</b> <code>{}</code>\n\n💵 <b>Euro:</b> R$ <code>{}</code>\n🗓 <b>Data:</b>  <code>{}</code>\n📊 <b>Variação:</b> <code>{}</code>\n\n💵 <b>BTC:</b> R$ <code>{}</code>\n🗓 <b>Data:</b>  <code>{}</code>\n📊 <b>Variação:</b> <code>{}</code>\n\n💵 <b>DOGE:</b> R$ <code>{}</code>\n🗓 <b>Data:</b> <code>{}</code>\n📊 <b>Variação:</b> <code>{}</code>\n\n💵 <b>Iene:</b> R$ <code>{}</code>\n🗓 <b>Data:</b> <code>{}</code>\n📊 <b>Variação:</b> <code>{}</code>\n💵 <b>Peso Argentino:</b> R$ <code>{}</code>\n🗓 <b>Data:</b> <code>{}</code>\n📊 <b>Variação:</b> <code>{}</code>\n\n💵 <b>Ruplo Russo:</b> R$ <code>{}</code>\n🗓 <b>Data:</b> <code>{}</code>\n📊 <b>Variação:</b> <code>{}</code>"

    await message.reply_photo(photo="https://telegra.ph/file/d60e879db1cdba793a98c.jpg",
    caption=result.format(cotacao_dolar, dat_dolar, var_dolar, cotacao_euro, dat_euro, var_euro, cotacao_btc, dat_btc, var_btc, cotacao_doge, dat_doge, var_doge, cotacao_iene, dat_iene, var_iene, cotacao_ars, dat_ars, var_ars, cotacao_rub, dat_rub, var_rub))
    
    
