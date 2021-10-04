#!/usr/bin/env python3

from datetime import datetime

from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC

from pathlib import Path
import argparse
import shutil
import sys


app_version = "211003.1"

pub_version = "1.0.dev1"

app_title = f"mp3pic.py - version {app_version}"

ack_errors = False


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
        help="Name of the image file to use as the " + "cover picture.",
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

    #  TODO: Support other image types.
    if not image_path.suffix.lower() == ".jpg":
        sys.stderr.write(
            "ERROR: Not a .jpg file name: '{0}'\n".format(args.image_file)
        )
        error_exit()

    return (args.mp3_file, args.image_file)


def main():
    print(f"\n{app_title}\n")

    mp3_file, image_file = get_args()

    print(f"Reading '{mp3_file}'")

    print(f"Adding cover image '{image_file}'")

    p = Path(mp3_file)
    output_path = p.parent.joinpath(
        "{0}__{1}.mp3".format(
            p.stem, datetime.now().strftime("%y%m%d_%H%M%S")
        )
    )

    print(f"Writing '{output_path}'")

    if output_path.exists():
        print("ERROR: Output file already exists.")
        error_exit()

    #  TODO: Use pillow to check image properties and potentially scale
    #  and crop to appropriate dimensions for embedding in the ID3 tag.

    #  Make a copy then modify the copy.

    shutil.copyfile(mp3_file, str(output_path))

    audio = MP3(output_path, ID3=ID3)

    try:
        audio.add_tags()
    except Exception as e:
        if str(e) != "an ID3 tag already exists":
            raise e

    audio.tags.add(
        APIC(
            encoding=3,
            mime="image/jpeg",
            type=3,
            desc="Cover",
            data=open(image_file, "rb").read(),
        )
    )

    audio.save()


if __name__ == "__main__":
    main()
