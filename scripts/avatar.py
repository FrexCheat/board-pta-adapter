import hashlib
import shutil
from pathlib import Path

from loguru import logger


def rename_and_copy_images():
    base_path = Path.cwd()
    src_dir = base_path / "vendor" / "avatar-registry" / "png"
    dst_dir = base_path / "output" / "logos"

    dst_dir.mkdir(parents=True, exist_ok=True)

    if not src_dir.exists():
        logger.error(f"Error: {src_dir} does not exist!")
        return

    image_files = list(src_dir.glob("*.png"))

    if not image_files:
        logger.error("Error: No PNG files found in the source directory!")
        return

    logger.info(f"Found {len(image_files)} PNG files. Starting processing...")

    for file_path in image_files:
        original_full_name = file_path.name
        clean_name = file_path.stem

        logger.info(f"Processing: {original_full_name} ...")

        md5_hash = hashlib.md5(clean_name.encode("utf-8")).hexdigest()
        new_filename = f"{md5_hash[:8]}.png"

        target_path = dst_dir / new_filename
        shutil.copy2(file_path, target_path)

        logger.info(f"Renamed to: {new_filename}")

    logger.info(f"Task completed! All files saved to: {dst_dir}")


if __name__ == "__main__":
    rename_and_copy_images()
