import asyncio

import aiogram
from aiogram import types
from aiogram.utils.exceptions import BotBlocked, Throttled

from loader import db, bot


async def send_message_to_users(message: types.Message):
    await db.update_status_true()
    all_users = await db.select_all_users()
    success_count, failed_count = 0, 0

    for index, user in enumerate(all_users, start=1):
        try:
            await message.copy_to(chat_id=user["telegram_id"])
            success_count += 1
        except aiogram.exceptions.BotBlocked:
            failed_count += 1
            await db.delete_user(user["telegram_id"])
            await db.delete_inviter(user["telegram_id"])
        except Exception:
            pass
        if index % 1500 == 0:
            await asyncio.sleep(30)
        await asyncio.sleep(0.05)
    await db.update_status_false()
    return success_count, failed_count


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


# Foydalanuvchilarni ma'lumotlar bazasidan olish
async def get_users_in_batches(batch_size=1000):
    all_users = await db.select_all_users()
    for i in range(0, len(all_users), batch_size):
        yield all_users[i:i + batch_size]  # Batch qilib yuborish


# Xabarni nusxa ko'rinishida yuboruvchi asosiy funksiya
async def send_copy_to_users(original_message: types.Message):
    semaphore = asyncio.Semaphore(30)  # Bir vaqtning o'zida maksimal 30 ta xabar yuborish
    success_count, failed_count = 0, 0

    async def send_to_user(user):
        """Foydalanuvchiga xabarni nusxa ko'rinishida yuborish va xatoliklarni boshqarish."""
        nonlocal success_count, failed_count
        async with semaphore:
            try:
                await original_message.copy_to(chat_id=user["telegram_id"])
                success_count += 1
                await asyncio.sleep(0.05)  # Har bir xabar orasida 50 millisekund kutish
            except BotBlocked:
                failed_count += 1
                print(f"Bot foydalanuvchi tomonidan bloklandi: {user['telegram_id']}")
            except Throttled as e:
                print(f"Flood cheklovi: {user['telegram_id']}, kutyapmiz {e.retry_after} sekund")
                await asyncio.sleep(e.retry_after)  # Telegram bergan kutish muddatiga rioya qilish
            except Exception as e:
                failed_count += 1
                print(f"Xatolik: {e}")

    # Foydalanuvchilarni batch bo'lib o'qib, har bir batch uchun xabarni nusxa ko'rinishida yuborish
    async for batch in get_users_in_batches(batch_size=1000):
        tasks = [send_to_user(user) for user in batch]
        await asyncio.gather(*tasks)

    await original_message.answer(text=f"✅ Muvaffaqiyatli yuborilgan xabarlar: {success_count}"
                                       f"❌ Muvaffaqiyatsiz xabarlar: {failed_count}")
    await db.update_status_false()
