import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from openai import AsyncOpenAI

from bot.config import BOT_TOKEN, OPENAI_API_KEY

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

async def search_products(query: str):
    return [
        {"name": "Sony WH-CH520", "price": 3990, "rating": 4.7, "platform": "Ozon"},
        {"name": "JBL Tune 760NC", "price": 4890, "rating": 4.5, "platform": "Wildberries"},
    ]

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я ShopAI — твой ИИ-помощник в покупках.\n\n"
        "Просто напиши, что ищешь. Например:\n"
        "«Наушники до 5000₽, хороший звук, удобные»"
    )

@dp.message()
async def handle_query(message: types.Message):
    await bot.send_chat_action(message.chat.id, "typing")
    
    intent_prompt = f"""
    Пользователь ищет товар: "{message.text}"
    Определи: категория, бюджет, ключевые требования.
    Ответь JSON: {{"category": "...", "budget": ..., "features": [...]}}
    """
    
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": intent_prompt}],
        response_format={"type": "json_object"}
    )
    
    intent = response.choices[0].message.content
    products = await search_products(message.text)
    
    reply = "🔍 Вот что нашёл:\n\n"
    for i, p in enumerate(products, 1):
        reply += f"**{i}. {p['name']}** — {p['price']}₽\n"
        reply += f"⭐ {p['rating']}/5 | {p['platform']}\n\n"
    
    reply += "💡 Скоро я буду анализировать реальные отзывы и цены!"
    
    await message.answer(reply, parse_mode="Markdown")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())