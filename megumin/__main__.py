# Copyright (C) 2022 by fnixdev
#
from .utils import logging
from .bot import megux
from pyrogram import idle
from logging.handlers import RotatingFileHandler
import asyncio
from .utils.database.lang import load_language
from .utils.database.antiflood import rflood
from .utils.check import check_requirements


logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s - %(levelname)s] - %(name)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S',
                    handlers=[
                        RotatingFileHandler(
                            "WhiterKang.log", maxBytes=20480, backupCount=10),
                        logging.StreamHandler()
                    ])

logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("pyrogram.parser.html").setLevel(logging.ERROR)
logging.getLogger("pyrogram.session.session").setLevel(logging.ERROR)


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
