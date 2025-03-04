import argparse
import asyncio
import logging
import shutil
from pathlib import Path

# Налаштування логування
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Асинхронне копіювання файлів у відповідні підпапки на основі розширення
async def copy_file(file: Path, output_folder: Path):
    try:
        if not file.is_file():
            return

        extension = (
            file.suffix.lower().strip(".") or "unknown"
        )  
        target_dir = output_folder / extension
        target_dir.mkdir(
            parents=True, exist_ok=True
        )  
        target_file = target_dir / file.name

        # Використовуємо run_in_executor для асинхронного копіювання
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, shutil.copy2, file, target_file)

        logger.info(f"Файл {file.name} скопійовано в {target_dir}")
    except Exception as e:
        logger.error(f"Помилка копіювання {file.name}: {e}")

# Асинхронно читає файли з вихідної папки та передає їх у функцію копіювання
async def read_folder(source_folder: Path, output_folder: Path):

    tasks = []
    for file in source_folder.rglob("*"):  
        if file.is_file():
            tasks.append(copy_file(file, output_folder))

    if tasks:
        await asyncio.gather(*tasks)  

# Головна функція для обробки аргументів та запуску асинхронної обробки
def main():
    parser = argparse.ArgumentParser(
        description="Асинхронне сортування файлів за розширенням."
    )
    parser.add_argument("source_folder", type=str, help="Шлях до вихідної папки")
    parser.add_argument("output_folder", type=str, help="Шлях до цільової папки")

    args = parser.parse_args()
    source_folder = Path(args.source_folder).resolve()
    output_folder = Path(args.output_folder).resolve()

    # Перевірка наявності вихідної папки
    if not source_folder.exists() or not source_folder.is_dir():
        logger.error(f"Вихідна папка '{source_folder}' не існує!")
        return

    # Перевірка наявності або створення цільової папки
    if not output_folder.exists():
        output_folder.mkdir(parents=True, exist_ok=True)

    logger.info(f"Розпочато сортування файлів з {source_folder} в {output_folder}")
    asyncio.run(read_folder(source_folder, output_folder))
    logger.info("Сортування завершено.")

if __name__ == "__main__":
    main()