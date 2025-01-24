import openai
import logging

# Инициализация OpenAI
openai.api_key = "добавить ключ"

async def rewrite_text(text: str) -> str:
    """
    Асинхронно переписывает текст с помощью OpenAI.
    """
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты помощник, который переписывает тексты."},
                {"role": "user", "content": text},
            ],
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        logging.error(f"Ошибка при запросе к OpenAI API: {e}")
        return "Не удалось переписать текст. Попробуйте позже."