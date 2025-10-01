import logging
import os
import requests
from openai import OpenAI

# --- Конфигурация ---
MODEL_URL = "https://huggingface.co/lmstudio-ai/gemma-2b-it-GGUF/resolve/main/gemma-2b-it-q8_0.gguf"
MODEL_PATH = "model.gguf"

# --- Загрузка модели ---
def download_model(url, dest_path):
    """Загружает файл по URL, если он не существует."""
    if os.path.exists(dest_path):
        print(f"✅ Файл модели '{dest_path}' уже существует. Пропускаю загрузку.")
        return

    print(f"📥 Загрузка модели из {url}...")
    try:
        response = requests.get(url, allow_redirects=True, stream=True)
        response.raise_for_status()  # Вызовет исключение для плохих ответов (4xx или 5xx)

        total_size = int(response.headers.get('content-length', 0))
        
        with open(dest_path, 'wb') as f:
            if total_size > 0:
                print(f"Размер файла: {total_size / 1024 / 1024:.2f} MB")
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            else: # Если размер не указан, просто скачиваем
                f.write(response.content)

        print(f"✅ Модель успешно загружена в '{dest_path}'.")

    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при загрузке модели: {e}")
        if os.path.exists(dest_path):
            os.remove(dest_path) # Удаляем частично загруженный файл
    except IOError as e:
        print(f"❌ Ошибка при записи файла модели: {e}")

# --- Настройка клиента OpenAI ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

client = OpenAI(
    base_url="http://127.0.0.1:8080/v1",
    api_key="no-api-key-needed"
)

# --- Основные функции API ---
def generate(prompt, max_tokens=400):
    """Генерирует текст на основе промпта."""
    try:
        response = client.completions.create(
            model=MODEL_PATH,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=0.7,
            top_p=0.9
        )
        return {
            "response": response.choices[0].text.strip(),
            "usage": response.usage
        }
    except Exception as e:
        logging.error(f"Ошибка в функции generate: {str(e)}")
        return {"error": str(e)}

def chat(message):
    """Общается с моделью в режиме чата."""
    try:
        response = client.chat.completions.create(
            model=MODEL_PATH,
            messages=[{"role": "user", "content": message}],
            max_tokens=256,
            temperature=0.7,
            stop=["<end_of_turn>"]
        )
        return {
            "response": response.choices[0].message.content.strip(),
            "usage": response.usage
        }
    except Exception as e:
        logging.error(f"Ошибка в функции chat: {str(e)}")
        return {"error": str(e)}

# --- Функции консольного интерфейса ---
def print_help():
    """Выводит меню помощи."""
    print("\n📋 Помощь:")
    print("  /chat - Переключиться в режим чата")
    print("  /gen  - Переключиться в режим генерации текста")
    print("  /help - Показать это сообщение")
    print("  /exit - Выйти из программы")

def handle_gen_mode(user_input):
    """Обрабатывает логику для режима генерации."""
    try:
        tokens_input = input("Количество токенов для генерации [100]: ").strip()
        max_tokens = int(tokens_input) if tokens_input else 100
    except ValueError:
        max_tokens = 100
        print("⚠️ Неверный ввод. Используется значение по умолчанию: 100 токенов.")

    print("\n🔄 Генерирую текст...")
    result = generate(user_input, max_tokens=max_tokens)

    if "error" in result:
        print(f"❌ Ошибка: {result['error']}")
    else:
        print(f"📝 Результат: {result['response']}")
        if result.get('usage'):
            print(f"📊 Использовано токенов: {result['usage'].total_tokens}")

def handle_chat_mode(user_input):
    """Обрабатывает логику для режима чата."""
    print("\n🔄 Генерирую ответ...")
    result = chat(user_input)

    if "error" in result:
        print(f"❌ Ошибка: {result['error']}")
    else:
        print(f"🤖 Модель: {result['response']}")
        if result.get('usage'):
            print(f"📊 Использовано токенов: {result['usage'].total_tokens}")

def interactive_console():
    """Запускает основной интерактивный цикл консоли."""
    print("=" * 60)
    print("🤖 Локальная модель готова к работе!")
    print("Доступные команды: /chat, /gen, /help, /exit")
    print("=" * 60)

    current_mode = "chat"

    while True:
        try:
            prompt = f"\n[{current_mode.upper()}] Введите сообщение: "
            user_input = input(prompt).strip()

            if not user_input:
                continue

            if user_input.lower().startswith('/'):
                command = user_input.lower()
                if command in ['/exit', '/quit']:
                    print("👋 До свидания!")
                    break
                elif command == '/chat':
                    current_mode = "chat"
                    print("✅ Режим изменен на 'чат'.")
                elif command == '/gen':
                    current_mode = "gen"
                    print("✅ Режим изменен на 'генерация текста'.")
                elif command == '/help':
                    print_help()
                else:
                    print(f"❓ Неизвестная команда: {command}. Введите /help для помощи.")
                continue

            if current_mode == "chat":
                handle_chat_mode(user_input)
            elif current_mode == "gen":
                handle_gen_mode(user_input)

        except KeyboardInterrupt:
            print("\n\n👋 Выход по запросу пользователя.")
            break
        except Exception as e:
            print(f"❌ Произошла неожиданная ошибка: {str(e)}")

def quick_mode():
    """Запускает упрощенный режим непрерывного чата."""
    print("🚀 Быстрый режим чата")
    print("Просто вводите сообщения. Для выхода введите /exit или /quit.")
    print("-" * 40)

    while True:
        try:
            user_input = input("\n💬 Вы: ").strip()

            if user_input.lower() in ['/exit', '/quit']:
                break
            if not user_input:
                continue

            print("⏳ Обработка...")
            result = chat(user_input)

            if "error" in result:
                print(f"❌ Ошибка: {result['error']}")
            else:
                print(f"🤖 Модель: {result['response']}")

        except KeyboardInterrupt:
            print("\n👋 Выход.")
            break

# --- Основное выполнение ---
if __name__ == '__main__':
    # 1. Убедимся, что файл модели загружен
    download_model(MODEL_URL, MODEL_PATH)

    # 2. Даем пользователю выбрать режим взаимодействия
    print("\nВыберите режим работы:")
    print("1 - Интерактивная консоль (с командами)")
    print("2 - Быстрый чат (только диалог)")

    try:
        choice = input("Ваш выбор [1]: ").strip()
        if choice == "2":
            quick_mode()
        else:
            interactive_console()
    except KeyboardInterrupt:
        print("\n👋 Программа завершена.")
