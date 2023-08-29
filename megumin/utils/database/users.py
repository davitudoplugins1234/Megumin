import asyncio
import logging

from megumin import megux
from megumin.utils import get_collection, logging

DB_USER = get_collection("USERS_START")
DB_GROUP = get_collection("GROUPS")

async def find_user(uid: int):
    try:
        user = await megux.get_users(uid)
        USR = await DB_USER.find_one({"_id": user.id})
        return bool(USR)
    except Exception as e:
        logging.error(f"An Error Ocurred: {e}")
        return False

async def add_user(uid: int):
    try:
        user = await megux.get_users(uid)
        user_start = f"#NEW_USER #LOGS\n\n<b>User:</b> {user.mention}\n<b>ID:</b> {user.id} <a href='tg://user?id={user.id}'>**Link**</a>"
        if user.username:
            user_start += f"\n<b>Username:</b> @{user.username}"
        await asyncio.gather(
            DB_USER.update_one({"_id": user.id}, {"$set": {"user": user.first_name}}, upsert=True),
            megux.send_log(user_start),
        )
    except Exception as e:
        logging.error(f"An Error Occurred: {e}")
        pass
