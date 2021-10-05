#!/usr/bin/env python3

from datetime import datetime
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from pathlib import Path
from PIL import Image
import argparse
import shutil
import sys


app_version = "211004.1"

pub_version = "1.0.dev1"

app_title = f"mp3pic.py - version {app_version}"

ack_errors = False

default_image_size = (300, 300)

keep_tmp_jpg = False


def error_exit():
    print("*" * 70)
    if ack_errors:
        input("ERRORS: Press [Enter] to acknowledge. ")
    else:
        print("Halted due to errors.")
    sys.exit(1)


def get_args():
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
        sys.stderr.write("ERROR: Cannot find '{0}'\n".format(args.mp3_file))
        error_exit()

    if not mp3_path.suffix.lower() == ".mp3":
        sys.stderr.write(
            "ERROR: Not a mp3 file name: '{0}'\n".format(args.mp3_file)
        )
        error_exit()

    image_path = Path(args.image_file)

    if not image_path.exists():
        sys.stderr.write("ERROR: Cannot find '{0}'\n".format(args.image_file))
        error_exit()

    if not image_path.suffix.lower() in [".jpg", ".jpeg", ".png"]:
        sys.stderr.write(
            "ERROR: Not a .jpg file name: '{0}'\n".format(args.image_file)
        )
        error_exit()

    return (mp3_path, image_path)


def make_temp_image_file(source_path, temp_path):
    #  TODO: Check image properties and potentially scale and crop to
    #  appropriate dimensions for embedding in the ID3 tag.

    tmp_jpg = Image.new("RGB", default_image_size, (255, 255, 255))

    cover_image = Image.open(source_path)

    # TODO: Replace this brute-force resize with scale and crop.
    cover_image = cover_image.resize(default_image_size)

    tmp_jpg.paste(cover_image, (0, 0))

    tmp_jpg.save(temp_path)


def main():
    print(f"\n{app_title}\n")

    run_dt = datetime.now().strftime("%y%m%d_%H%M%S")

    mp3_path, image_path = get_args()

    print(f"Reading '{mp3_path}'")

    print(f"Adding cover image '{image_path}'")

    output_path = mp3_path.parent.joinpath(
        "{0}__{1}.mp3".format(mp3_path.stem, run_dt)
    )

    tmp_jpg_path = mp3_path.parent.joinpath(
        "{0}__{1}.jpg".format(image_path.stem, run_dt)
    )

    print(f"Writing '{output_path}'")

    if output_path.exists():
        print("ERROR: Output file already exists.")
        error_exit()

    make_temp_image_file(image_path, tmp_jpg_path)

    #  Make a copy then modify the copy.

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

    image_data = open(tmp_jpg_path, "rb").read()

    audio.tags.add(
        APIC(
            encoding=3,
            mime=mime_type,
            type=3,
            desc="Cover",
            data=image_data,
        )
    )

    audio.save()

    if not keep_tmp_jpg:
        tmp_jpg_path.unlink()


if __name__ == "__main__":
    main()
