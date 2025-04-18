from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import datetime
import json
import random
from pathlib import Path
import google.generativeai as genai
genai.configure(api_key="AIzaSyBZ-R3dGbLQn7sLBY2t5j6uY1WwmPAdAMQ")

print("🔍 Listing available Gemini models...")
try:
    models = genai.list_models()
    for m in models:
        print("✅ Available model:", m.name)
except Exception as e:
    print("❌ Error listing models:", e)

# Quick Gemini model test (optional)
try:
    test_model = genai.GenerativeModel("gemini-1.5-flash")
    test_response = test_model.generate_content("✅ Gemini test: How does AI work?")
    print("🔎 Gemini test response:", test_response.text)
except Exception as e:
    print("❌ Gemini test failed:", e)

challenge_ideas = [
    "👀 Try 5 minutes of undistracted eye contact during playtime today.",
    "🌱 Let your child lead the play — follow their ideas for 10 minutes.",
    "💛 Whisper a compliment to your child while cuddling.",
    "🎨 Offer your child 3 objects and let them invent a game.",
    "🧘 Take 3 deep breaths together before bedtime."
]

play_ideas = [
    # For babies 1-2 years
    "🖐️ Sensory basket: Fill a box with soft, crinkly, and textured items for your child to explore.",
    "🔔 Sound play: Use a small bell, shaker, or keys and shake them gently — see how your child reacts!",
    "📦 Box surprise: Put a toy inside a box and encourage your child to find it.",
    "🐾 Follow the leader: Crawl or walk slowly and let your child mimic your movements.",
    "🎵 Dance freeze: Dance to music and freeze when it stops — giggles guaranteed!",
    
    # For toddlers 2-3 years
    "🧩 Puzzle time: Try a simple 2-4 piece puzzle together.",
    "🎨 Sticker fun: Give them dot stickers and a paper to freely decorate.",
    "🚗 Toy road trip: Draw a road on paper and drive small toy cars along it together.",
    "🧺 Laundry toss: Toss socks into a basket — like basketball!",
    "👣 Copy-cat walk: Walk like animals together — hop like a frog, waddle like a penguin.",
    
    # For children 3-4 years
    "🎭 Shadow show: Use a flashlight and hands to make shadows on the wall.",
    "🧽 Sponge squeeze: Fill a bowl with water and sponges — squeeze and transfer water between bowls.",
    "🧵 Threading fun: Thread big pasta on a shoelace together (supervised!).",
    "🌈 Color sort: Sort toys by color into bowls or containers.",
    "📚 Story switch: Start a story and let your child invent what happens next.",
    
    # For 4-6 years
    "🎨 Nature painting: Use leaves or sticks as brushes outside.",
    "🏗️ Build-a-bridge: Use blocks or cardboard to build something tall or long.",
    "🕵️ Treasure hunt: Hide a few objects and give playful clues to find them.",
    "🎲 Movement dice: Make a dice with actions like jump, spin, stomp — roll and do it!",
    "🎬 Act it out: Pretend you're animals or characters and guess who’s who!",
    
    # Additional cozy, developmentally valuable play rituals
    # General rituals for connection
    "👐 High-five ritual: Every morning, give your child a high-five and say one thing you love about them.",
    "🌞 Wake-up whisper: Gently whisper something sweet to your child when they wake up.",
    "📸 Photo moment: Take a playful selfie together once a week and talk about how you’ve changed.",
    
    # For babies 1–2 years
    "🧴 Lotion bonding: After bath time, massage your baby’s legs or arms with lotion while naming each part.",
    "🐻 Teddy talk: Let your child 'talk' to their favorite toy and you respond like the toy is real.",
    "🧦 Sock fun: Put socks on their hands or head and giggle together while playing ‘silly monster’.",
    
    # For toddlers 2–3 years
    "🍌 Snack helper: Let your toddler peel a banana or pick a snack and say ‘thank you’ like it’s a big deal.",
    "🐾 Animal hunt: Hide animal toys and play ‘who lives here?’ as you find them.",
    "🎶 Morning song: Pick a fun song to sing together every morning while getting dressed.",
    
    # For children 3–4 years
    "🎈 Balloon toss: Toss a balloon and keep it in the air — try counting out loud with each hit.",
    "🎒 Backpack surprise: Hide a small surprise in their bag and let them find it after a walk or outing.",
    "🎤 Echo game: Say a silly phrase and let them echo it back with a new voice (robot, whisper, lion).",
    
    # For 4–6 years
    "📜 Family scroll: Create a ‘scroll’ where you write little things that made you happy today together.",
    "🎯 Sock bowling: Roll a ball toward a set of socks and count how many fall!",
    "🌌 Star stretch: Do a slow bedtime stretch with arms to the sky and say ‘I’m proud of you’ before sleep.",
    "🔍 Detective play: Pretend you lost something and explore the room together to find clues.",
    "🎙️ Story broadcast: Use a wooden spoon or toy mic and let your child tell a ‘news report’ of their day."
]

main_inline_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📅 Daily Tip", callback_data="menu:tip"),
     InlineKeyboardButton(text="📝 Update Birthdate", callback_data="menu:update_birthday")],
    [InlineKeyboardButton(text="📊 Track Mood", callback_data="menu:track_mood")],
    [InlineKeyboardButton(text="🤯 Ask NUNU", callback_data="menu:ask_nunu")],
    [InlineKeyboardButton(text="🆘 SOS", callback_data="menu:sos")],
    [InlineKeyboardButton(text="✨ Memory Spark", callback_data="menu:memory_spark")],
    [InlineKeyboardButton(text="🧸 Play Ritual", callback_data="menu:play_ritual")]
])
main_reply_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👶 Daily Tip"), KeyboardButton(text="📊 Mood Log")],
        [KeyboardButton(text="🌟 Challenge"), KeyboardButton(text="🎲 Play Idea")],
        [KeyboardButton(text="🤯 Ask NUNU")]
    ],
    resize_keyboard=True,
    is_persistent=True
)

def generate_gpt_tip(age_in_months: int) -> str:
    age_text = f"{age_in_months} month old" if age_in_months != 1 else "1 month old"
    prompt = (
        f"Write a warm, concise, emotionally supportive parenting tip for a parent of a {age_text} child. "
        f"The tone should be positive, gentle, and loving. After the tip, add one short practical example "
        f"like a child psychologist would — for example: 'You could try saying…' or 'One idea to try is…'. "
        f"Limit the total response to 3 short sentences."
    )
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text.strip()

BIRTHDAYS_FILE = Path("birthdays.json")

def load_birthdates():
    if BIRTHDAYS_FILE.exists():
        with open(BIRTHDAYS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_birthdate(user_id: int, birthdate: str):
    data = load_birthdates()
    data[str(user_id)] = birthdate
    with open(BIRTHDAYS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

router = Router()

class Form(StatesGroup):
    waiting_for_year = State()
    waiting_for_month = State()
    waiting_for_day = State()
    waiting_for_question = State()

@router.message(Command("start"))
async def start_command(message: Message, state: FSMContext):
    print(f"📩 Received /start from user {message.from_user.id}")
    years = [str(y) for y in range(datetime.datetime.now().year - 6, datetime.datetime.now().year + 1)]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=year, callback_data=f"year:{year}")] for year in years
    ])
    await message.answer("👋 Hi! I’m NUNU — your parenting buddy!\n\nPick your child's birth **year**:", reply_markup=keyboard)
    await message.answer("📌 I’ve added a menu below for your convenience 🌿", reply_markup=main_reply_keyboard)
    await state.set_state(Form.waiting_for_year)

@router.callback_query(F.data.startswith("year:"), Form.waiting_for_year)
async def pick_year(callback: CallbackQuery, state: FSMContext):
    year = callback.data.split(":")[1]
    await state.update_data(year=year)

    months = [f"{i:02d}" for i in range(1, 13)]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=month, callback_data=f"month:{month}")] for month in months
    ])
    await callback.message.edit_text("📅 Now pick the **month**:", reply_markup=keyboard)
    await state.set_state(Form.waiting_for_month)

@router.callback_query(F.data.startswith("month:"), Form.waiting_for_month)
async def pick_month(callback: CallbackQuery, state: FSMContext):
    month = callback.data.split(":")[1]
    await state.update_data(month=month)

    days = [f"{i:02d}" for i in range(1, 32)]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=day, callback_data=f"day:{day}")] for day in days
    ])
    await callback.message.edit_text("🗓️ And finally, pick the **day**:", reply_markup=keyboard)
    await state.set_state(Form.waiting_for_day)

@router.callback_query(F.data.startswith("day:"), Form.waiting_for_day)
async def pick_day(callback: CallbackQuery, state: FSMContext):
    day = callback.data.split(":")[1]
    data = await state.get_data()
    birthdate = f"{day}.{data['month']}.{data['year']}"
    await state.update_data(birthdate=birthdate)
    await callback.message.edit_text(
        f"✅ Birthdate saved as {birthdate}. I’ll start sending daily tips soon 💛"
    )
    save_birthdate(callback.from_user.id, birthdate)
    await state.clear()

import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from utils import scheduler

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    
    print("🚀 Bot is running. Waiting for messages...")
    await dp.start_polling(bot)

@router.callback_query(F.data == "menu:ask_nunu")
async def handle_ask_nunu(callback: CallbackQuery, state: FSMContext):
    print(f"🤯 Ask NUNU clicked by user {callback.from_user.id}")
    await callback.message.answer("🧠 What would you like to ask NUNU?\n\nI’m listening — just type your question and I’ll share a warm, personalized response 💛")
    await state.set_state(Form.waiting_for_question)
    await callback.answer()

@router.message(Form.waiting_for_question)
async def ask_nunu_text_trigger(message: Message, state: FSMContext):
    prompt = message.text
    system_message = "You are NUNU, a warm and gentle parenting guide. Speak softly and kindly. Use short, helpful suggestions."
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(system_message + "\n\n" + prompt)
    await message.answer("💬 " + response.text.strip())
    await state.clear()

@router.message(F.text == "🤯 Ask NUNU")
async def handle_ask_nunu_text(message: Message, state: FSMContext):
    print(f"🤯 Ask NUNU (text) by user {message.from_user.id}")
    await message.answer(
        "🧠 What would you like to ask NUNU?\n\nI’m listening — just type your question and I’ll share a warm, personalized response 💛"
    )
    await state.set_state(Form.waiting_for_question)

@router.message(Command("google_test"))
async def google_test(message: Message):
    # Simple test using Google Gemini
    response = google_client.models.generate_content(
        model="gemini-2.0-flash",
        contents="Explain how AI works in a few words"
    )
    await message.answer(f"🤖 Google Gemini says:\n{response.text}")

@router.callback_query(F.data == "menu:sos")
async def handle_sos_button(callback: CallbackQuery, state: FSMContext):
    print(f"🆘 SOS button pressed by user {callback.from_user.id}")
    categories = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="😩 I'm overwhelmed", callback_data="sos:overwhelmed")],
        [InlineKeyboardButton(text="😢 Feeling sad", callback_data="sos:sad")],
        [InlineKeyboardButton(text="😤 Angry or frustrated", callback_data="sos:angry")],
        [InlineKeyboardButton(text="😔 Just tired", callback_data="sos:tired")],
        [InlineKeyboardButton(text="🕯️ Need hope", callback_data="sos:hope")]
    ])
    await callback.message.answer("💛 I’m here. What are you feeling right now?", reply_markup=categories)
    await callback.answer()

@router.callback_query(F.data.startswith("sos:"))
async def handle_sos_category(callback: CallbackQuery):
    category = callback.data.split(":")[1]

    sos_messages = {
        "overwhelmed": [
            "💛 You're doing better than you think. Pause. Breathe. One small step at a time.",
            "🔥 Big feelings don’t mean you’re failing. They mean you care deeply.",
            "☁️ Breathe in softness, breathe out tension. You’re safe right now.",
        ],
        "sad": [
            "🌿 This too shall pass. You are not alone.",
            "🫂 Imagine a warm hug wrapped around your tired soul.",
            "📖 This is just one chapter. The story of your parenting is beautiful.",
        ],
        "angry": [
            "🧘‍♀️ Inhale for 4… Hold for 4… Exhale for 6… Repeat once more with kindness to yourself.",
            "📦 Imagine putting your worries in a box and setting it aside for now.",
            "🪞 Speak to yourself like you would to your child — gently and with love.",
        ],
        "tired": [
            "💧 Drink a sip of water. Look out the window. You're a good parent, even now.",
            "🫖 Make a small cozy moment just for you — tea, silence, or a song.",
            "🌻 You’re allowed to pause. The world can wait a moment.",
        ],
        "hope": [
            "🕯️ Light a tiny flame of hope inside. It’s still burning.",
            "🌤️ The sky clears after the clouds. So will this moment.",
            "📅 Today doesn’t define you. Love does.",
        ],
    }

    selected_messages = sos_messages.get(category, [])
    if selected_messages:
        text = random.choice(selected_messages)
        await callback.message.answer(text)
    else:
        await callback.message.answer("💛 I'm here for you.")
    await callback.answer()

@router.callback_query(F.data == "menu:track_mood")
async def handle_track_mood(callback: CallbackQuery, state: FSMContext):
    mood_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="😊 Happy", callback_data="mood:happy")],
        [InlineKeyboardButton(text="😢 Sad", callback_data="mood:sad")],
        [InlineKeyboardButton(text="😡 Angry", callback_data="mood:angry")],
        [InlineKeyboardButton(text="😴 Tired", callback_data="mood:tired")],
        [InlineKeyboardButton(text="😰 Anxious", callback_data="mood:anxious")]
    ])
    await callback.message.answer("📊 How are you feeling today?", reply_markup=mood_keyboard)
    await callback.answer()

@router.callback_query(F.data.startswith("mood:"))
async def handle_mood_choice(callback: CallbackQuery):
    mood = callback.data.split(":")[1]

    mood_responses = {
        "happy": [
            "🌈 That’s wonderful! Take a moment to soak it all in — joy builds connection.",
            "🎉 Keep that smile — your energy is contagious!",
            "💛 Let today’s joy ripple into tomorrow.",
        ],
        "sad": [
            "🌧️ It’s okay to feel sad. Your emotions matter.",
            "🫂 Sending a warm virtual hug your way.",
            "📖 Every chapter has ups and downs — you’re not alone in this one.",
        ],
        "angry": [
            "🔥 Your feelings are valid. Take a deep breath — or a few.",
            "🪞 Reflect with kindness. You're doing your best.",
            "🌬️ Blow out the frustration like candles. Slow and gentle.",
        ],
        "tired": [
            "🌙 Rest if you can. Even a deep breath counts.",
            "💤 A tired parent is still a loving parent.",
            "🫖 Take a quiet moment, just for you.",
        ],
        "anxious": [
            "🌿 Inhale calm, exhale tension.",
            "🤝 You're not alone. Even tiny steps help.",
            "🧘 Ground yourself: What do you see, hear, and feel right now?",
        ]
    }

    if mood in mood_responses:
        # Optional logging
        with open("mood_logs.json", "a", encoding="utf-8") as f:
            log_entry = {
                "user_id": callback.from_user.id,
                "mood": mood,
                "timestamp": datetime.datetime.now().isoformat()
            }
            f.write(json.dumps(log_entry) + "\n")
        message = random.choice(mood_responses[mood])
        await callback.message.answer(f"📝 Mood logged: {callback.data.split(':')[1].capitalize()}\n{message}")
    else:
        await callback.message.answer("📝 Mood logged.")

    await callback.answer()

@router.callback_query(F.data == "menu:play_ritual")
async def handle_play_ritual(callback: CallbackQuery):
    print(f"🎲 Play Ritual button clicked by user {callback.from_user.id}")
    play_message = random.choice(play_ideas)
    await callback.message.answer(f"🧸 Here’s a cozy Play Ritual idea:\n\n{play_message}")
    await callback.answer()

@router.callback_query(F.data == "menu:memory_spark")
async def handle_memory_spark(callback: CallbackQuery):
    print(f"✨ Memory Spark button clicked by user {callback.from_user.id}")
    memory_sparks = [
        "📸 Take a photo of your child laughing today — this joy is worth keeping.",
        "💌 Write a one-line letter to your child and put it in a memory box.",
        "🖼️ Draw a tiny family portrait together — even stick figures count.",
        "🎵 Choose a song that feels like today and play it during bedtime.",
        "🗣️ Tell your child one memory from when they were a baby before sleep.",
        "🌟 Whisper something you're proud of about them tonight.",
        "👣 Trace your child’s hand or foot and write the date next to it.",
        "📖 Make up a silly bedtime story where your child is the hero.",
        "🪞 Look into their eyes for 5 quiet seconds today — say nothing, just smile.",
        "🧩 Ask: ‘What made you happy today?’ and listen with your whole heart.",
        "🍽️ Let them help you with one thing in the kitchen — even stirring counts.",
        "💬 Start a new tradition: ‘What’s one thing you want to remember from today?’",
        "🌙 Put your phone away for 15 minutes and do whatever your child wants.",
        "🎁 Hide a tiny note in their pocket or lunch with a simple ‘You are loved’.",
        "☀️ Say good morning today with a goofy face or funny voice — watch them giggle.",
        "📦 Open a ‘memory box’ and look at something from the past together.",
        "💛 Tell your child, 'You are my favorite part of today.'",
        "🎈 Let your child choose how to celebrate the evening — dance, song, story?",
        "🖊️ Start a bedtime journal where you write or draw one tiny memory together.",
        "🧸 Take a photo of a toy your child played with today — it's part of their story.",
        "🧡 Sit quietly together and hold hands for 30 seconds — no words, just presence.",
        "📅 Mark today on a calendar with a sticker for a sweet moment you shared.",
        "🎨 Draw how today felt — with scribbles, shapes, or color blobs — and giggle.",
        "🕯️ Light a candle and say 'thank you' for one moment today.",
        "🎤 Record your child saying something funny or sweet — save it as a treasure.",
    ]
    spark = random.choice(memory_sparks)
    await callback.message.answer(f"✨ Memory Spark:\n\n{spark}")
    await callback.answer()

@router.callback_query(F.data == "menu:tip")
async def handle_daily_tip(callback: CallbackQuery):
    print(f"📅 Daily Tip requested by user {callback.from_user.id}")
    birthdates = load_birthdates()
    user_id = str(callback.from_user.id)
    if user_id in birthdates:
        birthdate = datetime.datetime.strptime(birthdates[user_id], "%d.%m.%Y")
        today = datetime.datetime.now()
        age_in_months = (today.year - birthdate.year) * 12 + today.month - birthdate.month
        tip = generate_gpt_tip(age_in_months)
        await callback.message.answer(f"📅 Daily Tip for your {age_in_months}-month-old:\n\n{tip}")
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📝 Update Birthdate", callback_data="menu:update_birthday")]
        ])
        await callback.message.answer(
            "👶 I’d love to share a Daily Tip — but first, I need to know your child’s birthdate. Please tap the button below 💛",
            reply_markup=keyboard
        )
    await callback.answer()

@router.message(F.text == "📊 Mood Log")
async def handle_mood_log_button(message: Message, state: FSMContext):
    print(f"📊 Mood Log (text) requested by user {message.from_user.id}")
    mood_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="😊 Happy", callback_data="mood:happy")],
        [InlineKeyboardButton(text="😢 Sad", callback_data="mood:sad")],
        [InlineKeyboardButton(text="😡 Angry", callback_data="mood:angry")],
        [InlineKeyboardButton(text="😴 Tired", callback_data="mood:tired")],
        [InlineKeyboardButton(text="😰 Anxious", callback_data="mood:anxious")]
    ])
    await message.answer("📊 How are you feeling today?", reply_markup=mood_keyboard)

@router.message(F.text == "👶 Daily Tip")
async def handle_daily_tip_text(message: Message):
    print(f"📅 Daily Tip (text) requested by user {message.from_user.id}")
    birthdates = load_birthdates()
    user_id = str(message.from_user.id)
    if user_id in birthdates:
        birthdate = datetime.datetime.strptime(birthdates[user_id], "%d.%m.%Y")
        today = datetime.datetime.now()
        age_in_months = (today.year - birthdate.year) * 12 + today.month - birthdate.month
        tip = generate_gpt_tip(age_in_months)
        await message.answer(f"📅 Daily Tip for your {age_in_months}-month-old:\n\n{tip}")
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📝 Update Birthdate", callback_data="menu:update_birthday")]
        ])
        await message.answer(
            "👶 I’d love to share a Daily Tip — but first, I need to know your child’s birthdate. Please tap the button below 💛",
            reply_markup=keyboard
        )
@router.message(F.text == "🌟 Challenge")
async def handle_challenge_button(message: Message):
    print(f"🌟 Challenge requested by user {message.from_user.id}")
    challenge = random.choice(challenge_ideas)
    birthdates = load_birthdates()
    user_id = str(message.from_user.id)
    if user_id not in birthdates:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📝 Update Birthdate", callback_data="menu:update_birthday")]
        ])
        await message.answer(
            "🌟 I’d love to share a Challenge — but first, I need to know your child’s birthdate 💛",
            reply_markup=keyboard
        )
        return
    await message.answer(f"🌟 Challenge:\n\n{challenge}")

@router.message(F.text == "🎲 Play Idea")
async def handle_play_idea_button(message: Message):
    print(f"🎲 Play Idea requested by user {message.from_user.id}")
    play = random.choice(play_ideas)
    birthdates = load_birthdates()
    user_id = str(message.from_user.id)
    if user_id not in birthdates:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📝 Update Birthdate", callback_data="menu:update_birthday")]
        ])
        await message.answer(
            "🎲 I’d love to share a Play Idea — but first, I need to know your child’s birthdate 💛",
            reply_markup=keyboard
        )
        return
    await message.answer(f"🎲 Play Idea:\n\n{play}")

if __name__ == "__main__":
    asyncio.run(main())
