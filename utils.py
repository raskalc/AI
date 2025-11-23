import os
import sys

import requests


def download_model(url, dest_path):
    if os.path.exists(dest_path):
        print(f"✅ Файл модели '{dest_path}' уже существует. Пропускаю загрузку.")
        return

    print(f"📥 Загрузка модели из {url}...")
    try:
        response = requests.get(url, allow_redirects=True, stream=True)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        with open(dest_path, 'wb') as f:
            chunk_size = 8192
            if total_size > 0:
                print(f"Размер файла: {total_size / 1024 / 1024:.2f} MB")
                for chunk in response.iter_content(chunk_size=chunk_size):
                    f.write(chunk)
                    downloaded += len(chunk)
                    done = int(50 * downloaded / total_size)
                    sys.stdout.write(
                        f"\r[{'#' * done}{'.' * (50 - done)}] {downloaded / 1024 / 1024:.2f} MB / {total_size / 1024 / 1024:.2f} MB")
                    sys.stdout.flush()
                print()
            else:
                print("Размер файла не указан, скачиваю без прогресса...")
                f.write(response.content)
        print(f"✅ Модель успешно загружена в '{dest_path}'.")
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при загрузке модели: {e}")
        if os.path.exists(dest_path):
            os.remove(dest_path)
    except IOError as e:
        print(f"❌ Ошибка при записи файла модели: {e}")
