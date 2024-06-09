import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor

import os
import json
from elasticsearch import Elasticsearch

import asyncio
import bot_data_prep

# Установка уровня логирования
logging.basicConfig(level=logging.INFO)

bot = Bot(token="")
dp = Dispatcher(bot)

# Инициализация остальных сущностей делалась отдельно


# Функция для отправки данных в Elasticsearch
async def send_to_elasticsearch(text):
    # Test the connection by retrieving cluster health
    health = es.cluster.health()
    print(health)

    search_query = {
        "query": {
            "match": {
                "data.text": text
            }
        }
    }

    search_results = es.search(index="my_index", body=search_query)
    prompt = str(search_results['hits']['hits'][0]['_source'])
    return prompt, search_results['hits']['hits'][0]['_source']['url']

# Функция запроса к нейросети
async def query_neural_network(text):
    data = {
        "prompt": text,
        "system_prompt": "You are a friendly chatbot that translates texts into the style of Shakespearean.",
        "config": {
            "do_sample": True,
            "max_new_tokens": 300,
            "temperature": 0.2,
            "top_p": 0.5,
        },
    }

    res = api.deployment_requests_create(
        project_name=PROJECT_NAME, deployment_name=DEPLOYMENT_NAME, data=data, timeout=3600
    ).result
    return res

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply("Привет! Я бот для абитуриентов ВШЭ. Используй /help для получения списка команд.")

@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    help_text = "Список команд:\n/help - список команд\n/text <текст> - так нужно задавать вопрос боту. Далее ждите ответа системы"
    await message.reply(help_text, parse_mode=ParseMode.MARKDOWN)

# Обработчик команды /text
@dp.message_handler(commands=['text'])
async def text_command(message: types.Message):
    text = ' '.join(message.get_args())
    result_elasticsearch, url = await send_to_elasticsearch(text)
    result_processing = await bot_data_prep.extract_key_sentences_tfidf(text)
    result_neural_network = await query_neural_network(text)

    response_text = f"{result_elasticsearch}\n{result_processing}\n{result_neural_network}\n{url}"
    await message.reply(response_text)

async def main():
    await dp.start_polling()

if __name__ == '__main__':
    asyncio.run(main())
