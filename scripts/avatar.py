import argparse
import hashlib
import json
import shutil
from pathlib import Path

from loguru import logger


def process(type: str = "xcpcio", ext: str = "png") -> None:
    base_path = Path.cwd()
    src_dir = base_path / "vendor" / "avatars" / "dist"
    dst_dir = base_path / "output" / type / "logos"
    xcpcio_org_path = base_path / "output" / "xcpcio" / "organizations.json"
    gplt_team_path = base_path / "output" / "gplt" / "teams.json"

    dst_dir.mkdir(parents=True, exist_ok=True)
    if not src_dir.exists():
        logger.error(f"Error: {src_dir} does not exist!")
        return

    if type == "xcpcio" and not xcpcio_org_path.exists():
        logger.error(
            f"Error: {xcpcio_org_path} does not exist! Please run the CLI to generate the organizations.json file first."
        )
        return

    if type == "gplt" and not gplt_team_path.exists():
        logger.error(
            f"Error: {gplt_team_path} does not exist! Please run the CLI to generate the teams.json file first."
        )
        return

    shutil.rmtree(dst_dir)
    dst_dir.mkdir(parents=True, exist_ok=True)

    orgs = []

    if type == "xcpcio":
        with open(xcpcio_org_path, "r", encoding="utf-8") as f:
            _orgs = json.load(f)
            orgs = list({org["name"] for org in _orgs})
    elif type == "gplt":
        with open(gplt_team_path, "r", encoding="utf-8") as f:
            _teams = json.load(f)
            orgs = list(set({team["school"] for team in _teams}))

    for org in orgs:
        _hash = hashlib.md5(org.encode("utf-8")).hexdigest()[:8]
        src_file = src_dir / f"{_hash}.{ext}"
        if src_file.exists():
            shutil.copy2(src_dir / f"{_hash}.{ext}", dst_dir / f"{_hash}.{ext}")
        else:
            logger.warning(f"Warning: {src_file} does not exist! {org} will use a default avatar.")
            shutil.copy2(src_dir / f"a6b83b4d.{ext}", dst_dir / f"{_hash}.{ext}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rename and copy image files.")
    parser.add_argument("-t", "--type", default="xcpcio", help="Type of images to process")
    parser.add_argument("-e", "--ext", default="png", help="Type of images to copy")
    args = parser.parse_args()
    if args.type not in ["xcpcio", "gplt"]:
        logger.error("Invalid type specified. Use 'xcpcio' or 'gplt'.")
    elif args.ext not in ["png", "webp"]:
        logger.error("Invalid extension specified. Use 'png' or 'webp'.")
    else:
        process(type=args.type, ext=args.ext)
