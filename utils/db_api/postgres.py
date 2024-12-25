from typing import Union
import asyncpg

from asyncpg.pool import Pool
from data import config


class Database:
    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME
        )

    async def execute(self, command, *args, fetch=False, fetchval=False, fetchrow=False, execute=False):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)  # *args bilan argumentlar yuboriladi
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)  # To'g'ri uzatilgan argumentlar
        return result

    async def create_tables(self):
        queries = [
            """
                CREATE TABLE IF NOT EXISTS link_table (
                    id SERIAL PRIMARY KEY,
                    inviter BIGINT NOT NULL,
                    new_member BIGINT NOT NULL UNIQUE,
                    invite_count INTEGER DEFAULT 0,
                    created_at DATE DEFAULT CURRENT_DATE            
                );
            """,
            """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    telegram_id BIGINT NOT NULL UNIQUE,
                    check_status BOOLEAN DEFAULT FALSE                                
            );
            """,
            """
                CREATE TABLE IF NOT EXISTS users_data (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL REFERENCES users (id) ON DELETE CASCADE,
                    full_name VARCHAR(255) NULL,
                    phone VARCHAR(255) NULL                                                    
            );
            """,
            """
                CREATE TABLE IF NOT EXISTS admins (
                    id SERIAL PRIMARY KEY,
                    status BOOLEAN DEFAULT FALSE                                
                );
            """
        ]
        for query in queries:
            await self.execute(query, execute=True)

    # ====================== LINK_TABLE ======================
    async def add_members(self, inviter, new_member, invite_count):
        sql = "INSERT INTO link_table (inviter, new_member, invite_count) VALUES ($1, $2, $3) returning id"
        return await self.execute(sql, inviter, new_member, invite_count, fetchrow=True)

    async def count_members(self, inviter):
        sql = "SELECT COUNT(*) FROM link_table WHERE inviter = $1"
        return await self.execute(sql, inviter, fetchval=True)

    async def delete_old_links(self):
        sql = "DELETE FROM link_table WHERE created_at != CURRENT_DATE"
        return await self.execute(sql, execute=True)

    async def delete_inviter(self, inviter):
        sql = "DELETE FROM link_table WHERE inviter = $1"
        return await self.execute(sql, inviter, execute=True)

    async def drop_table_links(self):
        sql = "DROP TABLE link_table"
        return await self.execute(sql, execute=True)

    # ====================== USERS ======================
    async def add_user(self, telegram_id):
        sql = "INSERT INTO users (telegram_id) VALUES ($1) RETURNING id"
        await self.execute(sql, telegram_id, execute=True)

    async def select_user(self, telegram_id):
        sql = "SELECT * FROM users WHERE telegram_id = $1"
        return await self.execute(sql, telegram_id, fetchval=True)

    async def select_all_users(self):
        sql = "SELECT telegram_id FROM users "
        return await self.execute(sql, fetch=True)

    async def count_users(self):
        sql = "SELECT COUNT(*) FROM users"
        return await self.execute(sql, fetchval=True)

    async def update_status_false(self, telegram_id):
        sql = """ UPDATE users SET status = FALSE WHERE telegram_id = $1 """
        return await self.execute(sql, telegram_id, execute=True)

    async def update_user_status(self, check_status, telegram_id):
        sql = "UPDATE users SET check_status = $1 WHERE telegram_id = $2"
        return await self.execute(sql, check_status, telegram_id, execute=True)

    async def delete_blocked_users(self):
        sql = "DELETE FROM users WHERE status = FALSE"
        return await self.execute(sql, execute=True)

    async def drop_table_users(self):
        sql = "DROP TABLE users"
        return await self.execute(sql, execute=True)

    # ====================== USERS_DATA ======================
    async def add_user_data(self, user_id):
        sql = "INSERT INTO users_data (user_id) VALUES ($1)"
        await self.execute(sql, user_id, execute=True)

    async def select_user_data(self, user_id):
        sql = "SELECT * FROM users_data WHERE user_id = $1"
        return await self.execute(sql, user_id, fetchval=True)

    async def update_user_full_name(self, full_name, user_id):
        sql = "UPDATE users_data SET full_name = $1 WHERE user_id = $2"
        return await self.execute(sql, full_name, user_id, execute=True)

    async def update_user_phone(self, phone, user_id):
        sql = "UPDATE users_data SET phone = $1 WHERE user_id = $2"
        return await self.execute(sql, phone, user_id, execute=True)



    # ====================== ADMINS ======================
    async def update_send_status(self, send_status):
        sql = "UPDATE admins SET status = $1"
        return await self.execute(sql, send_status, execute=True)

    async def get_send_status(self):
        sql = "SELECT status FROM admins"
        return await self.execute(sql, fetchval=True)
