import os
import random
import logging
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Настройка логов
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Загружаем токен
load_dotenv()
TOKEN = os.getenv("larp_token")

if not TOKEN:
    raise RuntimeError("❌ ОШИБКА: Не задан BOT_TOKEN в файле .env")

# --- ПУТИ К ЛОКАЛЬНЫМ ФАЙЛАМ ---
BASE_DIR = r"C:\Users\user\Desktop\larp\image"

WIN_IMAGE_PATH = os.path.join(BASE_DIR, "win.png")
LOSE_GIF_PATH = os.path.join(BASE_DIR, "lose.gif")

MONKEY_FILES = {
    "Обычная 🐒": os.path.join(BASE_DIR, "normal.png"),
    "Редкая 🦧": os.path.join(BASE_DIR, "rare.png"),
    "Эпик 👑": os.path.join(BASE_DIR, "epic.png")
}

# --- ИНТЕРНЕТ-КАРТИНКИ ДЛЯ ЗАГОЛОВКОВ НОВОСТЕЙ ---
MONKEY_NEWS_IMAGES = [
    "https://unsplash.com",
    "https://unsplash.com",
    "https://unsplash.com",
    "https://unsplash.com"
]

# --- СПИСОК РАНДОМНЫХ ОБЕЗЬЯНЬИХ НОВОСТЕЙ ---
NEWS_LIST = [
    "⚡️ Срочно! Эпическая бибизяна угнала трактор с банановой плантации. Полиция джунглей объявила план «Перехват».",
    "📈 Курс банана вырос на 14% после того, как вожак стаи Орангутанов официально назвал его главной валютой леса.",
    "🧐 Ученые выяснили: обычные бибизяны работают на 30% эффективнее, если во время сбора бананов им чешут спинку.",
    "🥊 Редкая бибизяна вызвала на дуэль Гориллу из соседнего леса из-за последнего спелого банана. Матч века пройдет сегодня!",
    "⚠️ Внимание! На центральном рынке контейнеров замечены хитрые мартышки, которые подсовывают фальшивую кожуру вместо настоящих бананов.",
    "👑 Главный Эпик леса завел канал в Телеграме и набрал 1 миллион подписчиков за час, просто выложив фотку своего самого большого банана."
]

# --- КЛАВИАТУРА ---
def build_game_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton("Бежать до сваих"), KeyboardButton("Воевать с другими бибизянками")],
        [KeyboardButton("Открыть контейнер (5 🍌)"), KeyboardButton("📰 Бибизяни новости")],
        [KeyboardButton("посмотреть карман")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# --- ИНИЦИАЛИЗАЦИЯ ДАННЫХ ---
def init_user_data(context: ContextTypes.DEFAULT_TYPE) -> None:
    if "bananas" not in context.user_data:
        context.user_data["bananas"] = 0
    if "monkeys" not in context.user_data:
        context.user_data["monkeys"] = {"Обычная 🐒": 0, "Редкая 🦧": 0, "Эпик 👑": 0}

# --- ПАССИВНЫЙ ДОХОД ---
async def passive_income_callback(context: ContextTypes.DEFAULT_TYPE) -> None:
    for user_id, user_data in context.application.user_data.items():
        if "monkeys" in user_data:
            monkeys = user_data["monkeys"]
            income = (
                monkeys.get("Обычная 🐒", 0) * 1 +
                monkeys.get("Редкая 🦧", 0) * 3 +
                monkeys.get("Эпик 👑", 0) * 10
            )
            if income > 0:
                user_data["bananas"] = user_data.get("bananas", 0) + income
                try:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=f"🏪 Пассивный доход принес тебе **+{income} 🍌**!"
                    )
                except Exception:
                    pass

# --- КОМАНДЫ ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    init_user_data(context)
    await update.message.reply_text(
        "🍌 Нажимай кнопки, чтобы добывать бананы, собирать команду бибизян, читать новости или воевать!",
        reply_markup=build_game_keyboard(),
    )

# --- ОБРАБОТЧИК ТЕКСТА ---
async def handler_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return

    init_user_data(context)
    text = update.message.text

    if text == "Бежать до сваих":
        is_win = random.choice([True, False])
        if is_win:
            context.user_data["bananas"] += 1
            current_balance = context.user_data["bananas"]
            try:
                with open(WIN_IMAGE_PATH, "rb") as photo_file:
                    await update.message.reply_photo(photo=photo_file, caption=f"ты дабежал да сваих\nБананов в кармане: {current_balance}")
            except FileNotFoundError:
                await update.message.reply_text(f"ты дабежал да сваих\nБананов в кармане: {current_balance}")
        else:
            current_balance = context.user_data["bananas"]
            try:
                with open(LOSE_GIF_PATH, "rb") as gif_file:
                    await update.message.reply_animation(animation=gif_file, caption=f"ты пагиб🥀\nБананов в кармане: {current_balance}")
            except FileNotFoundError:
                await update.message.reply_text(f"ты пагиб🥀\nБананов в кармане: {current_balance}")

    elif text == "Воевать с другими бибизянками":
        STAKE = 5
        if context.user_data["bananas"] < STAKE:
            await update.message.reply_text(f"❌ Для битвы нужно хотя бы {STAKE} 🍌! У тебя всего {context.user_data['bananas']}.")
            return

        monkeys = context.user_data["monkeys"]
        team = []
        base_lose_chance = 60

        if monkeys["Обычная 🐒"] > 0:
            team.append("Обычная 🐒")
            base_lose_chance -= 5
        if monkeys["Редкая 🦧"] > 0:
            team.append("Редкая 🦧")
            base_lose_chance -= 15
        if monkeys["Эпик 👑"] > 0:
            team.append("Эпик 👑")
            base_lose_chance -= 30

        final_lose_chance = max(10, base_lose_chance)
        team_str = ", ".join(team) if team else "В одиночку 👤"
        await update.message.reply_text(f"⚔️ Ты отправляешься воевать с другими бибизянками!\n👥 Твоя команда: {team_str}\n📉 Риск проиграть: {final_lose_chance}%")

        if random.randint(1, 100) > final_lose_chance:
            context.user_data["bananas"] += STAKE
            await update.message.reply_text(f"🎉 Победа на арене! Ставка удвоена: **+{STAKE} 🍌**\nБананов в кармане: {context.user_data['bananas']}")
        else:
            context.user_data["bananas"] -= STAKE
            loss_msg = f"😢 Ты проиграл битву и потерял {STAKE} 🍌."
            if team and random.randint(1, 100) <= 35:
                dead_monkey = random.choice(team)
                context.user_data["monkeys"][dead_monkey] -= 1
                loss_msg += f"\n\n🥀 Во время жестокого боя твоя **{dead_monkey}** пагиб..."
            loss_msg += f"\nБананов в кармане: {context.user_data['bananas']}"
            await update.message.reply_text(loss_msg)

    elif text == "Открыть контейнер (5 🍌)":
        if context.user_data["bananas"] < 5:
            await update.message.reply_text(f"❌ Не хватает бананов! Нужно 5 🍌, а у тебя всего {context.user_data['bananas']}.")
            return

        context.user_data["bananas"] -= 5
        lootbox_choices = ["Обычная 🐒", "Редкая 🦧", "Эпик 👑"]
        dropped_monkey = random.choices(lootbox_choices, weights=[70, 25, 5], k=1)[0]
        context.user_data["monkeys"][dropped_monkey] += 1
        
        photo_path = MONKEY_FILES[dropped_monkey]
        try:
            with open(photo_path, "rb") as f:
                await update.message.reply_photo(photo=f, caption=f"📦 Из контейнера выпадает: **{dropped_monkey}**!\nБананов осталось: {context.user_data['bananas']}")
        except FileNotFoundError:
            await update.message.reply_text(f"📦 Из контейнера выпадает: **{dropped_monkey}**!\nБананов осталось: {context.user_data['bananas']}")

    elif text == "📰 Бибизяни новости":
        # Берем случайную новость и случайную интернет-картинку обезьяны
        random_news = random.choice(NEWS_LIST)
        random_img = random.choice(MONKEY_NEWS_IMAGES)
        
        try:
            await update.message.reply_photo(
                photo=random_img,
                caption=f"📰 **БИБИЗЯНИ НОВОСТИ** ⚡️\n\n{random_news}",
                parse_mode="Markdown"
            )
        except Exception:
            await update.message.reply_text(f"📰 **БИБИЗЯНИ НОВОСТИ** ⚡️\n\n{random_news}", parse_mode="Markdown")

    elif text == "посмотреть карман":
        bananas = context.user_data["bananas"]
        monkeys = context.user_data["monkeys"]
        current_speed = monkeys['Обычная 🐒'] * 1 + monkeys['Редкая 🦧'] * 3 + monkeys['Эпик 👑'] * 10
        
        info_msg = (
            f"💼 **Содержимое кармана:**\n"
            f"🍌 Бананы: {bananas} ( Доход: +{current_speed} 🍌/мин )\n\n"
            f"🏆 **Твоя стая бибизян:**\n"
            f"◽️ Обычные: {monkeys['Обычная 🐒']}\n"
            f"◽️ Редкие: {monkeys['Редкая 🦧']}\n"
            f"◽️ Эпик: {monkeys['Эпик 👑']}"
        )
        await update.message.reply_text(info_msg, parse_mode="Markdown")
        
    else:
        await update.message.reply_text("Пользуйтесь кнопками на клавиатуре ниже 👇")

# --- ЗАПУСК ---
if __name__ == "__main__":
    print("Запускаю бананового бота...")
    app = ApplicationBuilder().token(TOKEN).build()
    
    job_queue = app.job_queue
    job_queue.run_repeating(passive_income_callback, interval=60, first=10)
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler_text))
    
    print("✅ Бот успешно запущен!")
    app.run_polling()
