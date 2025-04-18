from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router = Router()

main_inline_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📅 Daily Tip", callback_data="menu:tip"),
     InlineKeyboardButton(text="📝 Update Birthdate", callback_data="menu:update_birthday")],
    [InlineKeyboardButton(text="📊 Track Mood", callback_data="menu:track"),
     InlineKeyboardButton(text="⚙️ Settings", callback_data="menu:settings")]
])

class Form(StatesGroup):
    waiting_for_birthdate = State()

@router.message(F.text == "/start")
async def start_command(message: Message, state: FSMContext):
    await message.answer(
        "👋 Hi! I’m NUNU — your caring assistant for parenting.\n\n"
        "To get started, please pick your child’s birthdate from the calendar below 📅",
        reply_markup=await SimpleCalendar().start_calendar()
    )
    await state.set_state(Form.waiting_for_birthdate)

@router.callback_query(SimpleCalendarCallback.filter())
async def process_calendar(callback_query: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    selected_date = callback_data.date
    await state.update_data(birthdate=selected_date.strftime("%d.%m.%Y"))
    await state.clear()
    print(f"📅 Birthdate set to {selected_date.strftime('%d.%m.%Y')} for user {callback_query.from_user.id}")

    await callback_query.answer()  # remove 'loading' animation

    await callback_query.message.edit_text(
        f"✅ Got it! Your child’s birthdate is set to {selected_date.strftime('%d.%m.%Y')}.\n\nHere’s your menu:",
        reply_markup=main_inline_menu
    )

@router.callback_query(F.data == "menu:tip")
async def handle_menu_tip(callback: CallbackQuery):
    print(f"🟡 User {callback.from_user.id} pressed Daily Tip button")
    await callback.message.answer("/tip")

@router.callback_query(F.data == "menu:update_birthday")
async def handle_menu_update_birthday(callback: CallbackQuery, state: FSMContext):
    print(f"🔄 User {callback.from_user.id} pressed Update Birthdate button")
    await start_command(callback.message, state)

@router.message(F.text == "/menu")
async def show_main_menu(message: Message):
    print(f"📋 User {message.from_user.id} requested the menu manually")
    await message.answer("Here’s your menu:", reply_markup=main_inline_menu)