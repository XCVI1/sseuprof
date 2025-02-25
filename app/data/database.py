import asyncpg
import os
import json

# Настройки подключения к БД
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "7830")
DB_NAME = os.getenv("DB_NAME", "proforientation") 
DB_HOST = os.getenv("DB_HOST", "localhost")

async def create_pool():
    """Создаёт подключение к базе данных."""
    return await asyncpg.create_pool(
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        host=DB_HOST
    )

async def create_tables(pool):
    """Создаёт таблицы, если они отсутствуют."""
    async with pool.acquire() as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id SERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                age INT NOT NULL,
                number TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS test_results (
                result_id SERIAL PRIMARY KEY,
                user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
                answers TEXT NOT NULL,
                predicted_professions TEXT[] NOT NULL,
                result_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS professions (
                profession_id SERIAL PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                description TEXT NOT NULL
            );
        ''')
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                question_id SERIAL PRIMARY KEY,
                question TEXT NOT NULL UNIQUE,
                answers JSONB NOT NULL
            );
        ''')

async def load_questions_to_db(pool, questions):
    """Загружает вопросы в базу данных."""
    async with pool.acquire() as conn:
        for question_data in questions:
            answers_json = json.dumps(question_data['answers'])
            await conn.execute('''
                INSERT INTO questions (question, answers)
                VALUES ($1, $2)
                ON CONFLICT (question) DO NOTHING
                RETURNING question_id
            ''', question_data['question'], answers_json)
            question_id = await conn.fetchval('SELECT question_id FROM questions WHERE question = $1', question_data['question'])
            question_data['question_id'] = question_id

async def add_user(pool, telegram_id, name, age, number):
    """Добавляет пользователя в базу данных, если его нет."""
    async with pool.acquire() as conn:
        user_id = await conn.fetchval('''
            INSERT INTO users (telegram_id, name, age, number)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (telegram_id) DO UPDATE 
            SET name = EXCLUDED.name, age = EXCLUDED.age, number = EXCLUDED.number
            RETURNING user_id
        ''', telegram_id, name, age, number)
        return user_id  # Теперь функция возвращает user_id

async def get_user_id_by_telegram_id(pool, telegram_id):
    """Получает user_id по telegram_id."""
    async with pool.acquire() as conn:
        result = await conn.fetchrow('SELECT user_id FROM users WHERE telegram_id = $1', telegram_id)
        return result['user_id'] if result else None

async def add_test_result(pool, user_id, answers, predicted_professions):
    async with pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO test_results (user_id, answers, predicted_professions)
            VALUES ($1, $2, $3)
        ''', user_id, answers, predicted_professions)  # Передаём список напрямую
  # Передаём список в формате asyncpg.Array()

async def test_db():
    """Проверяет соединение с базой данных."""
    pool = await create_pool()
    async with pool.acquire() as conn:
        result = await conn.fetch("SELECT 1")  # Проверяем соединение
        print("DB Connection Successful:", result)

# Если хочешь сразу протестировать, можно раскомментировать:
# import asyncio
# asyncio.run(test_db())
