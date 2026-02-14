import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.filters import CommandStart
from aiohttp import web

# === Переменные окружения ===
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "supersecret")
BASE_URL = os.getenv("RENDER_EXTERNAL_URL")
PORT = int(os.getenv("PORT", 10000))

WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{BASE_URL}{WEBHOOK_PATH}"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# === Хранилище последнего меню ===
user_last_menu = {}

# === Главное меню ===
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Открыть меню")]
    ],
    resize_keyboard=True
)

# === Inline-кнопки (2 столбца, 8 магазинов) ===
shops_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Пятёрочка", url="https://5ka.ru"),
            InlineKeyboardButton(text="Магнит", url="https://magnit.ru")
        ],
        [
            InlineKeyboardButton(text="Лента", url="https://lenta.com"),
            InlineKeyboardButton(text="Перекрёсток", url="https://perekrestok.ru")
        ],
        [
            InlineKeyboardButton(text="Ашан", url="https://auchan.ru"),
            InlineKeyboardButton(text="ВкусВилл", url="https://vkusvill.ru")
        ],
        [
            InlineKeyboardButton(text="О'КЕЙ", url="https://okmarket.ru"),
            InlineKeyboardButton(text="METRO", url="https://online.metro-cc.ru")
        ]
    ]
)

# === /start ===
@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "Добро пожаловать! Нажмите кнопку ниже 👇",
        reply_markup=main_keyboard
    )

# === Открытие меню ===
@dp.message(F.text == "Открыть меню")
async def open_menu(message: Message):
    user_id = message.from_user.id

    # Удаляем старое меню
    if user_id in user_last_menu:
        try:
            await bot.delete_message(
                chat_id=message.chat.id,
                message_id=user_last_menu[user_id]
            )
        except:
            pass

    sent_message = await message.answer(
        "🛒 Выберите магазин:",
        reply_markup=shops_keyboard
    )

    user_last_menu[user_id] = sent_message.message_id


# =============================
# 🔥 Anti-Sleep Endpoint
# =============================
async def health_check(request):
    return web.Response(text="OK")


# =============================
# Webhook
# =============================
async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL, secret_token=WEBHOOK_SECRET)

async def on_shutdown(app):
    await bot.delete_webhook()

def main():
    app = web.Application()

    # Webhook маршрут
    app.router.add_post(WEBHOOK_PATH, dp.webhook_handler)

    # Anti-sleep маршрут
    app.router.add_get("/health", health_check)

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    web.run_app(app, host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    main()
