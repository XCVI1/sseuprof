import app.keyboard as kb
from app.keyboard import create_professions_keyboard
from config import TOKEN
from app.predict_profession import load_model_and_predict
from aiogram import F, Router, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from app.data.questions import questions_main
from app.data.datasets import datasets, professions_info
from app.data.database import create_pool, add_user, add_test_result, create_tables, load_questions_to_db, get_user_id_by_telegram_id

router = Router()
bot = Bot(token=TOKEN)
storage = MemoryStorage()
db_pool = None

async def on_startup():
    global db_pool
    db_pool = await create_pool()
    await create_tables(db_pool)
    await load_questions_to_db(db_pool, questions_main)

async def on_shutdown():
    await db_pool.close()

class Registr(StatesGroup):
    name = State()
    age = State()
    number = State()

class TestStates(StatesGroup):
    question1 = State()
    question2 = State()
    description = State()

questions = questions_main

@router.message(Command(commands=['start']))
async def send_welcome(message: Message):
    await message.answer(
        'Привет! Это профориентационный чат-бот СГЭУ, для получения информации о командах введи /help, для регистрации нажми кнопку.',
        reply_markup=kb.main
    )

@router.message(F.text == 'Регистрация')
async def start_registr(message: Message, state: FSMContext):
    await message.answer("Начало регистрации")
    bot_message = await message.answer('Введите имя', reply_markup=ReplyKeyboardRemove())
    await state.update_data(bot_message_id=bot_message.message_id)
    await state.set_state(Registr.name)
    await message.delete()

@router.message(Registr.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    bot_message = await message.answer('Сколько вам лет?')
    await state.update_data(bot_message_id=bot_message.message_id)
    await state.set_state(Registr.age)

@router.message(Registr.age)
async def process_age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    bot_message = await message.answer('Отправьте номер телефона', reply_markup=kb.number)
    await state.update_data(bot_message_id=bot_message.message_id)
    await state.set_state(Registr.number)

@router.message(Registr.number)
async def process_number(message: Message, state: FSMContext):
    user_data = await state.get_data()
    name = user_data.get("name")
    age = int(user_data.get("age"))
    number = message.contact.phone_number if message.contact else message.text
    telegram_id = message.from_user.id

    await add_user(db_pool, telegram_id, name, age, number)

    reg_message = await message.answer('Регистрация завершена!', reply_markup=kb.start_test)
    await state.update_data(reg_message_id=reg_message.message_id)

    await state.clear()

@router.message(Command('help'))
async def get_help(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Выберите действие', reply_markup=kb.key_help)

answer_mapping = {}
answer_id = 1

for question in questions_main:
    for i, answer in enumerate(question['answers']):
        question['answers'][i] = (answer, str(answer_id))
        answer_mapping[str(answer_id)] = answer
        answer_id += 1

async def create_professions_keyboard(answers):
    keyboard = InlineKeyboardBuilder()
    for answer in answers:
        keyboard.button(text=answer[0], callback_data=answer[1])
    keyboard.adjust(1)
    return keyboard.as_markup()

@router.callback_query(F.data == 'test')
async def start_test(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    reg_message_id = user_data.get('reg_message_id')

    if reg_message_id:
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=reg_message_id)

    await callback.message.answer('Начало профориентационного теста.')

    bot_message = await callback.message.answer(
        questions_main[0]['question'],
        reply_markup=await create_professions_keyboard(questions_main[0]['answers'])
    )
    await state.update_data(bot_message_id=bot_message.message_id, current_question=0, answers=[])

    await state.set_state(TestStates.question1)

@router.callback_query(TestStates.question1)
async def main_question(callback: CallbackQuery, state: FSMContext):
    answer_id = callback.data
    user_data = await state.get_data()
    bot_message_id = user_data.get('bot_message_id')
    current_question = user_data.get('current_question', 0)

    answer_text = answer_mapping.get(answer_id)

    answers = user_data.get('answers', [])
    answers.append(answer_text)
    await state.update_data(answers=answers)

    if current_question + 1 < len(questions_main):
        next_question = current_question + 1

        await bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=bot_message_id,
            text=questions_main[next_question]['question'],
            reply_markup=await create_professions_keyboard(questions_main[next_question]['answers'])
        )

        await state.update_data(current_question=next_question)
    else:
        await state.set_state(TestStates.description)
        await callback.message.answer("Опишите, что вам интересно в IT (например, что вы любите делать):")

@router.message(TestStates.description)
async def process_description(message: Message, state: FSMContext):
    user_description = message.text
    user_data = await state.get_data()
    answers = user_data.get('answers', [])
    answers.append(user_description)

    predicted_profession = load_model_and_predict(' '.join(answers))
    telegram_id = message.from_user.id
    user_id = await get_user_id_by_telegram_id(db_pool, telegram_id)

    await add_test_result(db_pool, user_id, ' '.join(answers), predicted_profession)
    await message.answer(f"Вам может подойти: {', '.join(predicted_profession[:2])}")
    await state.clear()
