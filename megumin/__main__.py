# Copyright (C) 2022 by fnixdev
#
from . import logging
from .bot import megux
from pyrogram import idle
from logging.handlers import RotatingFileHandler
import asyncio
from .utils.database.lang import load_language
from .utils.database.antiflood import rflood
from .utils.check import check_requirements

# Start BOT

async def main():
    if check_requirements():
        load_language()
        await rflood()
        await megux.start()
        await idle()
        await megux.stop()
    else:
        return logging.warning("WhiterKang has not been started. Due to the VM not meeting the Minimum Requirements!")
    

if __name__ == "__main__" :
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
    except Exception as err:
        logging.error(err.with_traceback(None))
    finally:
        loop.stop()
