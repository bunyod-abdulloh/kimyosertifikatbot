from aiogram import types
from magic_filter import F

from data.config import CHANNEL_ID
from handlers.private.start import generate_invite_button
from loader import bot, dp


async def not_subcribe_message(call: types.CallbackQuery):
    bot_fullname = (await bot.get_chat(chat_id=CHANNEL_ID)).full_name
    await call.answer(
        text=f"Siz {bot_fullname} kanaliga a'zo bo'lmagansiz!", show_alert=True
    )


@dp.callback_query_handler(F.data == "subscribed")
async def subscribe_callback(call: types.CallbackQuery):
    user_status = (await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=call.from_user.id)).status

    if user_status == 'left':
        await not_subcribe_message(call=call)
    elif user_status == 'kicked':
        await not_subcribe_message(call=call)
    else:
        await call.message.edit_text(
            text=f"So'nggi qadam!\n\nYechimlarni qo'lga kiritish uchun Kimyo-Biologiya "
                 f"o'qiydigan 5 ta do'stingizni taklif qiling.\n\n"
                 f"Yechimlarni yopiq kanalga joyladik takliflar soni 5 ta bo'lganda Siz ushbu "
                 f"kanalga havola(link) olasiz.",
            reply_markup=await generate_invite_button(call.from_user.id)
        )
