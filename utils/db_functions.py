import asyncio

import aiogram
from aiogram import types
from aiogram.utils.exceptions import BotBlocked, Throttled

from loader import db, bot
#
#
# async def send_message_to_users(message: types.Message):
#     await db.update_status_true()
#     all_users = await db.select_all_users()
#     success_count, failed_count = 0, 0
#
#     for index, user in enumerate(all_users, start=1):
#         try:
#             await message.copy_to(chat_id=user["telegram_id"])
#             success_count += 1
#         except aiogram.exceptions.BotBlocked:
#             failed_count += 1
#             await db.delete_user(user["telegram_id"])
#             await db.delete_inviter(user["telegram_id"])
#         except Exception:
#             pass
#         if index % 1500 == 0:
#             await asyncio.sleep(30)
#         await asyncio.sleep(0.05)
#     await db.update_status_false()
#     return success_count, failed_count


async def send_media_group_to_users(media_group: types.MediaGroup):
    await db.update_status_true()
    all_users = await db.select_all_users()
    success_count, failed_count = 0, 0

    for index, user in enumerate(all_users, start=1):
        try:
            await bot.send_media_group(chat_id=user['telegram_id'], media=media_group)
            success_count += 1
        except aiogram.exceptions.BotBlocked:
            failed_count += 1
            await db.delete_user(user["telegram_id"])
        except Exception:
            pass
        if index % 1500 == 0:
            await asyncio.sleep(30)
        await asyncio.sleep(0.05)
    await db.update_status_false()

    return success_count, failed_count


async def send_message_to_users(message: types.Message):
    await db.update_status_true()
    all_users = await db.select_all_users()
    success_count, failed_count = 0, 0

    semaphore = asyncio.Semaphore(30)  # Bir vaqtning o'zida maksimal 30 ta xabar yuboriladi

    async def send_to_user(user):
        nonlocal success_count, failed_count
        async with semaphore:
            try:
                await message.copy_to(chat_id=user["telegram_id"])
                success_count += 1
                await asyncio.sleep(0.05)  # Oraliq kutish
            except BotBlocked:
                failed_count += 1
                await db.delete_user(user["telegram_id"])
                await db.delete_inviter(user["telegram_id"])
            except Throttled as e:
                await asyncio.sleep(e.retry_after)
                failed_count += 1
            except Exception:
                failed_count += 1

    # Parallel tarzda xabarlarni yuborish
    tasks = [send_to_user(user) for user in all_users]
    await asyncio.gather(*tasks)

    await db.update_status_false()
    return success_count, failed_count
