#!/usr/bin/env python3
"""
Асинхронний сортувальник файлів, який розподіляє файли по папках на основі їх розширень.
"""

import os
import sys
import asyncio
import logging
import argparse
from pathlib import Path


# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("file_sorter.log")],
)
logger = logging.getLogger(__name__)


async def copy_file(source_path, dest_folder):
    """
    Асинхронно копіює файл з вихідної папки до папки призначення на основі розширення файлу.

    Args:
        source_path (Path): Шлях до вихідного файлу
        dest_folder (Path): Базова папка призначення
    """
    try:
        # Отримуємо розширення файлу (без крапки) або 'no_extension' якщо розширення відсутнє
        file_ext = (
            source_path.suffix[1:].lower() if source_path.suffix else "no_extension"
        )

        # Створюємо підпапку для цього розширення, якщо вона ще не існує
        ext_folder = dest_folder / file_ext
        os.makedirs(ext_folder, exist_ok=True)

        # Формуємо шлях призначення
        dest_path = ext_folder / source_path.name

        # Перевірка на випадок, якщо файл уже існує
        if dest_path.exists():
            base_name = source_path.stem
            suffix = source_path.suffix
            counter = 1
            while dest_path.exists():
                new_name = f"{base_name}_{counter}{suffix}"
                dest_path = ext_folder / new_name
                counter += 1

        # Асинхронне читання та запис файлу
        loop = asyncio.get_event_loop()

        # Читаємо дані з вихідного файлу
        with open(source_path, "rb") as src_file:
            content = await loop.run_in_executor(None, src_file.read)

        # Записуємо дані у файл призначення
        with open(dest_path, "wb") as dest_file:
            await loop.run_in_executor(None, dest_file.write, content)

        logger.info(f"Скопійовано: {source_path} -> {dest_path}")

    except Exception as e:
        logger.error(f"Помилка копіювання файлу {source_path}: {str(e)}")


async def read_folder(source_folder, dest_folder, recursive=True):
    """
    Асинхронно читає всі файли у вихідній папці та її підпапках.

    Args:
        source_folder (Path): Шлях до вихідної папки
        dest_folder (Path): Шлях до папки призначення
        recursive (bool): Чи обробляти підпапки рекурсивно
    """
    try:
        tasks = []

        # Рекурсивно обходимо всі файли в папці
        for item in source_folder.iterdir():
            if item.is_file():
                # Для кожного файлу створюємо завдання на копіювання
                task = asyncio.create_task(copy_file(item, dest_folder))
                tasks.append(task)
            elif item.is_dir() and recursive:
                # Рекурсивно обробляємо підпапки
                subtask = asyncio.create_task(read_folder(item, dest_folder, recursive))
                tasks.append(subtask)

        # Чекаємо завершення всіх завдань
        if tasks:
            await asyncio.gather(*tasks)

    except Exception as e:
        logger.error(f"Помилка читання папки {source_folder}: {str(e)}")


async def main():
    """
    Головна асинхронна функція, яка обробляє аргументи та запускає сортування файлів.
    """
    parser = argparse.ArgumentParser(
        description="Асинхронний сортувальник файлів за розширеннями."
    )
    parser.add_argument("-s", "--source", required=True, help="Вихідна папка з файлами")
    parser.add_argument(
        "-d",
        "--destination",
        required=True,
        help="Папка призначення для сортованих файлів",
    )
    parser.add_argument(
        "-r", "--recursive", action="store_true", help="Рекурсивно обробляти підпапки"
    )

    args = parser.parse_args()

    source_path = Path(args.source)
    dest_path = Path(args.destination)

    # Перевірка вхідних даних
    if not source_path.exists() or not source_path.is_dir():
        logger.error(f"Вихідна папка не існує або не є папкою: {source_path}")
        return

    # Створюємо папку призначення, якщо вона не існує
    os.makedirs(dest_path, exist_ok=True)

    logger.info(f"Початок сортування файлів з {source_path} до {dest_path}")

    # Запускаємо читання папки
    await read_folder(source_path, dest_path, args.recursive)

    logger.info("Сортування файлів завершено")


if __name__ == "__main__":
    # Запускаємо головну асинхронну функцію
    asyncio.run(main())
