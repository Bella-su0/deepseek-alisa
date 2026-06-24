import os
from fastapi import FastAPI, Request
import openai

app = FastAPI()

# Настраиваем клиент для LLM7.io
client = openai.OpenAI(
    base_url="https://api.llm7.io/v1",
    api_key=os.getenv("LLM7_TOKEN", "unused")  # если переменная не задана, использует "unused"
)

@app.post("/")
async def main(request: Request):
    body = await request.json()
    user_text = body["request"]["original_utterance"]

    try:
        response = client.chat.completions.create(
            model="default",  # или "deepseek-r1", "default", "fast"
            messages=[{"role": "user", "content": user_text}],
            max_tokens=1000,
        )
        answer = response.choices[0].message.content
    except Exception as e:
        print(f"Ошибка LLM7: {e}")
        answer = "Извините, произошла ошибка при обращении к нейросети."

    return {
        "version": body["version"],
        "session": body["session"],
        "response": {
            "end_session": False,
            "text": answer
        }
    }
