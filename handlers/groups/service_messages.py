import aiogram
from aiogram import types

from data.config import ADMINS, BOT_ID
from filters.group_chat import IsGroup
from loader import dp, bot, db


def alert_message(message):
    text = (f"Bot guruhga admin qilinmaganligi sababli foydalanuvchi {message} haqidagi habarni "
            "o'chirmadi!\n\nBot to'g'ri ishlashi uchun botni guruhga admin qilishingiz lozim!")
    return text


async def send_alert(message, text):
    """Common function to send alert message and delete the original."""
    await message.answer(text)


@dp.message_handler(IsGroup(), content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def new_member(message: types.Message):
    try:
        member_mentions = []

        # Iterate through new members
        for member in message.new_chat_members:
            if member.id == BOT_ID:
                # Bot qo'shilganida administratorlarga xabar yuborish
                await bot.send_message(
                    chat_id=ADMINS[0],
                    text=f"Sizning {(await bot.me).full_name} botingiz {message.chat.full_name} guruhiga qo'shildi!"
                )
                await db.add_group(group_id=message.chat.id)
            # Yangi a'zo uchun HTML formatida mention
            mention = member.get_mention(name=member.first_name, as_html=True)
            member_mentions.append(mention)

        # Salomlashish xabari
        if member_mentions:
            await message.answer(f"Xush kelibsiz, {' , '.join(member_mentions)}!", parse_mode="HTML")
        else:
            # Agar faqat bot qo'shilmagan bo'lsa, oddiy xush kelibsiz xabarini yuborish
            await message.answer(f"Xush kelibsiz, {message.from_user.full_name}")

        # Xabarni o'chirish
        await message.delete()

    except aiogram.exceptions.MessageCantBeDeleted:
        # Xatolik yuzaga kelganida xabar yuborish
        await send_alert(message=message, text=alert_message(message="guruhga qo'shilganligi"))


@dp.message_handler(IsGroup(), content_types=types.ContentType.LEFT_CHAT_MEMBER)
async def banned_member(message: types.Message):
    try:
        left_member = message.left_chat_member
        if left_member.id == message.from_user.id:
            await message.answer(f"{left_member.get_mention(as_html=True)} guruhni tark etdi")

        else:
            # Admin tomonidan haydalgan foydalanuvchi
            if left_member.id == BOT_ID:
                await bot.send_message(
                    chat_id=ADMINS[0],
                    text=f"Sizning {(await bot.me).full_name} botingiz {message.chat.full_name} guruhidan chiqarildi!"
                )
                await db.delete_group(group_id=message.chat.id)
            else:
                await message.answer(f"{left_member.full_name} guruhdan haydaldi "
                                     f"\n\nAdmin: {message.from_user.get_mention(as_html=True)}.")
                # Xabarni o'chirish
                await message.delete()

    except aiogram.exceptions.MessageCantBeDeleted:
        await send_alert(message=message, text=alert_message("guruhdan chiqqanligi"))
