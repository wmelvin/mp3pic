#!/usr/bin/env python3

from datetime import datetime
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from pathlib import Path
from PIL import Image
from typing import Tuple
import argparse
import shutil
import sys


app_version = "211005.1"

pub_version = "1.0.dev1"

app_title = f"mp3pic.py - version {app_version}"

ack_errors = False

default_image_size = (300, 300)

jpg_quality = 60  # PIL default quality is 75.

keep_tmpimg = True


def error_exit():
    print("*" * 70)
    if ack_errors:
        input("ERRORS: Press [Enter]. ")
    else:
        print("Halted due to errors.")
    sys.exit(1)


def get_args() -> Tuple[Path, Path]:
    ap = argparse.ArgumentParser(
        description="Add a picture tag to a mp3 file."
    )

    ap.add_argument(
        "mp3_file",
        help="Name of the source mp3 file to modify. "
        + "The modified version will be given a new name.",
    )

    ap.add_argument(
        "image_file",
        help="Name of the image file to use as the cover picture. "
        + "File type must be .jpeg, .jpg, or .png.",
    )

    args = ap.parse_args()

    mp3_path = Path(args.mp3_file)

    if not mp3_path.exists():
        sys.stderr.write(f"ERROR: Cannot find '{args.mp3_file}'\n")
        error_exit()

    if not mp3_path.suffix.lower() == ".mp3":
        sys.stderr.write(f"ERROR: Not a mp3 file name: '{args.mp3_file}'\n")
        error_exit()

    image_path = Path(args.image_file)

    if not image_path.exists():
        sys.stderr.write(f"ERROR: Cannot find '{args.image_file}'\n")
        error_exit()

    if not image_path.suffix.lower() in [".jpg", ".jpeg", ".png"]:
        sys.stderr.write(f"ERROR: Not a .jpg file name: '{args.image_file}'\n")
        error_exit()

    return (mp3_path, image_path)


def get_new_size_zoom(current_size, target_size):
    scale_w = target_size[0] / current_size[0]
    scale_h = target_size[1] / current_size[1]
    scale_by = max(scale_w, scale_h)
    return (int(current_size[0] * scale_by), int(current_size[1] * scale_by))


def get_crop_box(current_size, target_size):
    cur_w, cur_h = current_size
    trg_w, trg_h = target_size

    if trg_w < cur_w:
        x1, xm = divmod(cur_w - trg_w, 2)
        x2 = cur_w - (x1 + xm)
    else:
        x1 = 0
        x2 = trg_w

    if trg_h < cur_h:
        y1, ym = divmod(cur_h - trg_h, 2)
        y2 = cur_h - (y1 + ym)
    else:
        y1 = 0
        y2 = trg_h

    return (x1, y1, x2, y2)


def make_temp_image_file(imgage_path: Path, tmpimg_path: Path):
    default_rgb = (255, 255, 255)
    tmp_jpg = Image.new("RGB", default_image_size, default_rgb)

    print(f"Adding cover image '{imgage_path}'")
    cover_image = Image.open(imgage_path)

    if cover_image.size != default_image_size:
        print(f"  Initial image size is {cover_image.size}.")
        new_size = get_new_size_zoom(cover_image.size, default_image_size)
        print(f"  Resizing to {new_size}.")
        cover_image = cover_image.resize(new_size)

        if cover_image.size != default_image_size:
            crop_box = get_crop_box(cover_image.size, default_image_size)
            print(f"  Cropping to box {crop_box}.")
            cover_image = cover_image.crop(crop_box)

        print(f"  New image size is {cover_image.size}.")

    tmp_jpg.paste(cover_image, (0, 0))
    tmp_jpg.save(tmpimg_path, quality=jpg_quality)


def main():
    print(f"\n{app_title}\n")

    run_dt = datetime.now().strftime("%y%m%d_%H%M%S")

    mp3_path, image_path = get_args()

    print(f"Reading '{mp3_path}'")

    output_path = mp3_path.parent.joinpath(f"{mp3_path.stem}__{run_dt}.mp3")

    tmpimg_path = mp3_path.parent.joinpath(f"{image_path.stem}__{run_dt}.jpg")

    print(f"Writing '{output_path}'")

    if output_path.exists():
        print("ERROR: Output file already exists.")
        error_exit()

    make_temp_image_file(image_path, tmpimg_path)

    #  Make a copy of the mp3 file, then modify the copy.

    shutil.copyfile(mp3_path, output_path)

    audio = MP3(output_path, ID3=ID3)

    try:
        audio.add_tags()
    except Exception as e:
        if str(e) != "an ID3 tag already exists":
            raise e

    if image_path.suffix.lower() == ".png":
        mime_type = "image/png"
    else:
        mime_type = "image/jpeg"

    image_data = open(tmpimg_path, "rb").read()

    audio.tags.add(
        APIC(
            encoding=3,
            mime=mime_type,
            type=3,
            desc="Cover Art (front)",
            data=image_data,
        )
    )

    audio.save()

    if not keep_tmpimg:
        tmpimg_path.unlink()


if __name__ == "__main__":
    main()
