#!/usr/bin/env python3
"""
Asynchronous file sorter that distributes files into folders based on their extensions.
"""

import os
import sys
import asyncio
import logging
import argparse
from pathlib import Path


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("file_sorter.log")],
)
logger = logging.getLogger(__name__)


async def copy_file(source_path, dest_folder):
    """
    Asynchronously copies a file from the source folder to the destination folder based on the file extension.

    Args:
        source_path (Path): Path to the source file
        dest_folder (Path): Base destination folder
    """
    try:
        # Get file extension (without dot) or 'no_extension' if none exists
        file_ext = (
            source_path.suffix[1:].lower() if source_path.suffix else "no_extension"
        )

        # Create subfolder for this extension if it doesn't exist yet
        ext_folder = dest_folder / file_ext
        os.makedirs(ext_folder, exist_ok=True)

        # Construct destination path
        dest_path = ext_folder / source_path.name

        # Check if file already exists
        if dest_path.exists():
            base_name = source_path.stem
            suffix = source_path.suffix
            counter = 1
            while dest_path.exists():
                new_name = f"{base_name}_{counter}{suffix}"
                dest_path = ext_folder / new_name
                counter += 1

        # Asynchronous file reading and writing
        loop = asyncio.get_event_loop()

        # Read data from source file
        with open(source_path, "rb") as src_file:
            content = await loop.run_in_executor(None, src_file.read)

        # Write data to destination file
        with open(dest_path, "wb") as dest_file:
            await loop.run_in_executor(None, dest_file.write, content)

        logger.info(f"Copied: {source_path} -> {dest_path}")

    except Exception as e:
        logger.error(f"Error copying file {source_path}: {str(e)}")


async def read_folder(source_folder, dest_folder, recursive=True):
    """
    Asynchronously reads all files in the source folder and its subfolders.

    Args:
        source_folder (Path): Path to the source folder
        dest_folder (Path): Path to the destination folder
        recursive (bool): Whether to process subfolders recursively
    """
    try:
        tasks = []

        # Recursively iterate through all files in the folder
        for item in source_folder.iterdir():
            if item.is_file():
                # Create a copying task for each file
                task = asyncio.create_task(copy_file(item, dest_folder))
                tasks.append(task)
            elif item.is_dir() and recursive:
                # Recursively process subfolders
                subtask = asyncio.create_task(read_folder(item, dest_folder, recursive))
                tasks.append(subtask)

        # Wait for all tasks to complete
        if tasks:
            await asyncio.gather(*tasks)

    except Exception as e:
        logger.error(f"Error reading folder {source_folder}: {str(e)}")


async def main():
    """
    Main asynchronous function that processes arguments and starts file sorting.
    """
    parser = argparse.ArgumentParser(
        description="Asynchronous file sorter by extensions."
    )
    parser.add_argument(
        "-s", "--source", required=True, help="Source folder with files"
    )
    parser.add_argument(
        "-d",
        "--destination",
        required=True,
        help="Destination folder for sorted files",
    )
    parser.add_argument(
        "-r", "--recursive", action="store_true", help="Process subfolders recursively"
    )

    args = parser.parse_args()

    source_path = Path(args.source)
    dest_path = Path(args.destination)

    # Input validation
    if not source_path.exists() or not source_path.is_dir():
        logger.error(f"Source folder doesn't exist or is not a folder: {source_path}")
        return

    # Create destination folder if it doesn't exist
    os.makedirs(dest_path, exist_ok=True)

    logger.info(f"Starting file sorting from {source_path} to {dest_path}")

    # Start folder reading
    await read_folder(source_path, dest_path, args.recursive)

    logger.info("File sorting completed")


if __name__ == "__main__":
    # Run the main asynchronous function
    asyncio.run(main())
