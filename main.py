import os
from fastapi import FastAPI, Request
import requests
import json

app = FastAPI()

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

@app.post("/")
async def main(request: Request):
    body = await request.json()
    user_text = body["request"]["original_utterance"]

    # 1. Отправляем запрос к DeepSeek
    response = requests.post(
        DEEPSEEK_API_URL,
        headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
        json={
            "model": "deepseek-chat",  # если не работает, попробуйте "deepseek-v3"
            "messages": [{"role": "user", "content": user_text}],
        }
    )

    # 2. Логируем статус и тело ответа (это появится в логах Render)
    print(f"Status code: {response.status_code}")
    print(f"Response text: {response.text}")

    # 3. Проверяем, успешен ли запрос
    if response.status_code != 200:
        error_msg = f"Ошибка API DeepSeek: {response.status_code} - {response.text}"
        print(error_msg)
        return {
            "version": body["version"],
            "session": body["session"],
            "response": {
                "end_session": False,
                "text": "Извините, произошла ошибка при обращении к DeepSeek. Проверьте баланс или ключ."
            }
        }

    # 4. Парсим JSON и проверяем наличие ключа "choices"
    data = response.json()
    if "choices" not in data:
        error_msg = f"Ответ DeepSeek не содержит 'choices': {data}"
        print(error_msg)
        return {
            "version": body["version"],
            "session": body["session"],
            "response": {
                "end_session": False,
                "text": "DeepSeek вернул неожиданный ответ. Проверьте логи."
            }
        }

    # 5. Получаем ответ
    answer = data["choices"][0]["message"]["content"]

    return {
        "version": body["version"],
        "session": body["session"],
        "response": {
            "end_session": False,
            "text": answer
        }
    }
