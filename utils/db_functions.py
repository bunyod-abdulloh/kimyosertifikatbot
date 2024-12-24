import asyncio

import aiogram
from aiogram import types

from loader import db, bot


async def send_message_to_users(message: types.Message):
    all_users = await db.select_all_users()
    success_count, failed_count = 0, 0

    for index, user in enumerate(all_users, start=1):
        try:
            await message.copy_to(chat_id=user["telegram_id"])
            success_count += 1
        except aiogram.exceptions.BotBlocked:
            failed_count += 1
            await db.delete_user(user["telegram_id"])
        else:
            pass
        if index % 1500 == 0:
            await asyncio.sleep(30)
        await asyncio.sleep(0.05)

    return success_count, failed_count


async def send_media_group_to_users(media_group: types.MediaGroup):
    all_users = await db.select_all_users()
    success_count, failed_count = 0, 0

    for index, user in enumerate(all_users, start=1):
        try:
            await bot.send_media_group(chat_id=user['telegram_id'], media=media_group)
            success_count += 1
        except aiogram.exceptions.BotBlocked:
            failed_count += 1
            await db.delete_user(user["telegram_id"])
        else:
            pass
        if index % 1500 == 0:
            await asyncio.sleep(30)
        await asyncio.sleep(0.05)

    return success_count, failed_count
