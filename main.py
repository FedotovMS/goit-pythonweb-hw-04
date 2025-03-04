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

#Асинхронне копіювання файлу у відповідну підпапку на основі розширення.
async def copy_file(file: Path, output_folder: Path):
    try:
        extension = file.suffix[1:].lower() or "unknown"  
        target_dir = output_folder / extension
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / file.name

        # Асинхронне копіювання файлу
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, shutil.copy2, file, target_file)

        logger.info(f"Скопійовано: {file.name} → {target_dir}")
    except Exception as e:
        logger.error(f"Помилка копіювання {file}: {e}")

#Асинхронно рекурсивно читає та копіює файли
async def read_folder(source_folder: Path, output_folder: Path):
    tasks = [
        asyncio.create_task(copy_file(file, output_folder))
        for file in source_folder.rglob("*") if file.is_file()
    ]
    await asyncio.gather(*tasks)  


def main():
    parser = argparse.ArgumentParser(description="Асинхронне сортування файлів за розширенням.")
    parser.add_argument("source_folder", type=str, help="Шлях до вихідної папки")
    parser.add_argument("output_folder", type=str, help="Шлях до цільової папки")

    args = parser.parse_args()
    source_folder = Path(args.source_folder).resolve()
    output_folder = Path(args.output_folder).resolve()

    if not source_folder.is_dir():
        logger.error(f"Вихідна папка '{source_folder}' не існує!")
        return

    output_folder.mkdir(parents=True, exist_ok=True)

    logger.info(f"Початок сортування з {source_folder} → {output_folder}")
    asyncio.run(read_folder(source_folder, output_folder))
    logger.info("Сортування завершено.")


if __name__ == "__main__":
    main()
