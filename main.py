import re
import random
import json
from difflib import SequenceMatcher

from pyrogram import Client, filters

# Загрузка конфигурации
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# Инициализация клиента
app = Client("my_account", api_id=config['api_id'], api_hash=config['api_hash'])

# Фильтр для проверки, находится ли чат в списке разрешенных
def allowed_chat(_, __, message):
    return message.chat.id in config['allowed_chats']

# Загрузка датасета
with open(config['dataset_path'], 'r', encoding='utf-8') as f:
    dataset = [line.strip().split(' / ') for line in f]

# Удаление цифр в начале датасетов
dataset = [(re.sub(r'^\d+\.', '', trigger).strip(), response) for trigger, response in dataset]

# Преобразование датасета в словарь для более удобного поиска
# Каждый триггер может иметь несколько ответов
responses = {}
for trigger, response in dataset:
    trigger = re.sub(r'[^\w\s]', '', trigger).lower()
    if trigger in responses:
        responses[trigger].append(response)
    else:
        responses[trigger] = [response]

# Функция для вычисления сходства между двумя строками
def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

# Функция для проверки, упоминается ли бот в сообщении
def is_mentioned(message):
    bot_names = config['bot_names']
    text = re.sub(r'[^\w\s]', '', message.text).lower().split()
    for word in text:
        for name in bot_names:
            if similarity(name, word) > 0.8:
                print(f"\033[93mИмя бота найдено по проценту сходства:\033[0m {name}, \033[92mпроцент сходства:\033[0m {similarity(name, word) * 100:.2f}%")
                return True
    print("\033[91mИмя бота не найдено в сообщении\033[0m")
    return False

# Обработчик входящих сообщений
@app.on_message(filters.text & filters.create(allowed_chat))
def auto_reply(client, message):
    if message.reply_to_message and message.reply_to_message.from_user.is_self:
        text = re.sub(r'[^\w\s]', '', message.text).lower()
        print(f"\033[94mПолучен ответ:\033[0m {message.text}")
        best_match = max(responses.keys(), key=lambda x: similarity(text, x))
        match_percent = similarity(text, best_match) * 100
        print(f"\033[92mПроцент совпадения:\033[0m {match_percent:.2f}%")
        response = random.choice(responses[best_match])
        message.reply(response)
    elif is_mentioned(message):
        text = re.sub(r'[^\w\s]', '', message.text).lower()
        print(f"\033[94mПолучено сообщение с упоминанием:\033[0m {message.text}")
        best_match = max(responses.keys(), key=lambda x: similarity(text, x))
        match_percent = similarity(text, best_match) * 100
        print(f"\033[92mПроцент совпадения:\033[0m {match_percent:.2f}%")
        response = random.choice(responses[best_match])
        message.reply(response)

# Запуск клиента
app.run()
