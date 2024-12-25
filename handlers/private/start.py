from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.utils.deep_linking import get_start_link
from asyncpg.exceptions import UniqueViolationError

from data.config import CHANNEL_ID, PRIVATE_CHANNEL
from loader import dp, db, bot
from states.users import UserStates


async def generate_invite_button(user_id):
    link = await get_start_link(str(user_id))
    send_link_text = (
        f"Qiymati 2000$ bo'lgan Milliy Sertifikat kitobini olish uchun quyidagi havola orqali botga a'zo bo'ling:\n\n{link}"
    )
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="Yuborish", switch_inline_query=send_link_text))
    return markup


async def send_welcome_message(message: types.Message):
    channel_info = await bot.get_chat(chat_id=CHANNEL_ID)
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(text=channel_info.full_name, url=f"https://t.me/{channel_info.username}"),
        types.InlineKeyboardButton(text="✅ A'zo bo'ldim!", callback_data="subscribed")
    )
    await message.answer(
        "Tabriklaymiz!!! Siz birinchi qadamni bosdingiz! Davom etish uchun yagona bo'lgan kanalimizga a'zo bo'ling.\n\n"
        "Keyin \"✅ А'zo bo'ldim!\" tugmasini bosing",
        reply_markup=markup
    )


@dp.message_handler(CommandStart(), state="*")
async def bot_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    args = message.get_args()
    user = await db.select_user(user_id)

    if not user:
        await message.answer("Ism sharifingizni kiriting:\n\n<b>Namuna: Behruz Jalolov</b>")
        await UserStates.GET_FULL_NAME.set()
        return

    if args:
        inviter_id = int(args)
        invite_count = await db.count_members(inviter=inviter_id)

        if invite_count == 4:
            invite_link = (await bot.create_chat_invite_link(chat_id=PRIVATE_CHANNEL, member_limit=1)).invite_link
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(text="Kanalga qo'shilish", url=invite_link))
            await bot.send_message(
                chat_id=inviter_id,
                text="Tabriklaymiz! Siz ushbu sovg'ani olishga haqli deb topildingiz.\n\n"
                     "Quyidagi tugma orqali yopiq kanalga qo'shiling.",
                reply_markup=markup, protect_content=True
            )
        elif invite_count > 4:
            await send_welcome_message(message)
        else:
            try:
                await db.add_members(inviter=inviter_id, new_member=user_id, invite_count=1)
                inviter_name = (await bot.get_chat(chat_id=inviter_id)).full_name
                await bot.send_message(
                    chat_id=inviter_id,
                    text=(
                        f"Tabriklaymiz, {inviter_name}! Do’stingiz {message.from_user.full_name} "
                        f"Sizning unikal taklif havolangiz orqali botimizga qo’shildi.\n\n"
                        f"Bonus sovg'alarni olish uchun yana {4 - invite_count} ta do’stingizni taklif qiling."
                    ),
                    reply_markup=await generate_invite_button(user_id=inviter_id)
                )
            except UniqueViolationError:
                await message.answer("Siz bot uchun ro'yxatdan o'tgansiz!")
                await bot.send_message(
                    chat_id=inviter_id,
                    text=(
                        f"Foydalanuvchi {message.from_user.full_name} bot uchun avval ro'yxatdan o'tgan!\n\n"
                        "Iltimos, boshqa foydalanuvchi taklif qiling!"
                    )
                )
        await state.finish()
    else:
        await send_welcome_message(message)


@dp.message_handler(state=UserStates.GET_FULL_NAME)
async def get_full_name(message: types.Message):
    await db.add_user_data(telegram_id=message.from_user.id, full_name=message.text)
    await message.answer(
        "Telefon raqamingizni kiriting:\n\n<b>Namuna: 998971234567</b>\n\n"
        "(raqam namunadagi kabi kiritilishi lozim!)"
    )
    await UserStates.GET_PHONE.set()


@dp.message_handler(state=UserStates.GET_PHONE)
async def get_phone(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await db.update_user_phone(phone=f"+{message.text}", telegram_id=message.from_user.id)
        await db.add_user(telegram_id=message.from_user.id)
        await message.answer(
            "Ma'lumotlaringiz qabul qilindi!\n\n/start buyru'gini qayta kiritib botimizdan foydalanishingiz mumkin!")
        await state.finish()
    else:
        await message.answer("Raqamni namunada ko'rsatilganidek kiritishingiz lozim!")
