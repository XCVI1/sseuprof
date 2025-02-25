import json
from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder
import os
import asyncpg
import logging

logging.basicConfig(level=logging.INFO)

DATA_FILE = 'users.json'

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Регистрация')],
],
                            resize_keyboard=True,
                            input_field_placeholder='Выберите пункт меню',
                            one_time_keyboard=True)

start_test = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Пройти тест', callback_data='test')]
])

number = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Отправить номер телефона', request_contact=True)]
    ],
    resize_keyboard=True, one_time_keyboard=True
)

key_help = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Пройти тестирование еще раз', callback_data='test')],
    [InlineKeyboardButton(text='Результат тестирования', callback_data='result')]
])

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "7830")
DB_NAME = os.getenv("DB_NAME", "proforientation")
DB_HOST = os.getenv("DB_HOST", "localhost")

async def create_pool():
    return await asyncpg.create_pool(
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        host=DB_HOST
    )

async def create_professions_keyboard(answers):
    logging.info(f"Creating keyboard with answers: {answers}")

    keyboard = InlineKeyboardBuilder()
    for answer in answers:
        keyboard.button(text=answer[0], callback_data=answer[1])
    keyboard.adjust(1)
    return keyboard.as_markup()
