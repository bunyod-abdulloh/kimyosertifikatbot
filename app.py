from aiogram import executor

from loader import dp, db
import middlewares, filters, handlers
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands


async def on_startup(dispatcher):
    await set_default_commands(dispatcher)
    await on_startup_notify(dispatcher)
    await db.create()
<<<<<<< HEAD
=======
    # await db.drop_table_links()
    # await db.drop_table_users()
    # await db.drop_table_users_data()
    # await db.drop_table_admins()
>>>>>>> 47ac071aca438aaeee605ea3514ec842536f62f4
    await db.create_tables()
    await db.add_send_status()


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
