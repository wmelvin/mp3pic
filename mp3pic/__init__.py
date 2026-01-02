#!/usr/bin/env python3

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import NamedTuple

from mutagen.id3 import APIC, ID3
from mutagen.mp3 import MP3
from PIL import Image

#  Using calver (YYYY.0M.MICRO).
__version__ = "2026.01.1"

app_title = f"mp3pic.py (v{__version__})"

ack_errors = False

default_image_size = (300, 300)

jpg_quality = 60  # PIL default quality is 75.


class AppOptions(NamedTuple):
    mp3_path: Path
    image_path: Path
    out_path: Path | None
    del_tags: bool
    keep_tmpimg: bool


def error_exit():
    print("*" * 70)
    if ack_errors:
        input("ERRORS: Press [Enter]. ")
    else:
        print("Halted due to errors.")
    sys.exit(1)


def get_options(arglist=None) -> AppOptions:
    ap = argparse.ArgumentParser(description="Add a picture tag to a mp3 file.")

    ap.add_argument(
        "mp3_file",
        help="Name of the source mp3 file to modify. "
        "The modified version will be given a new name.",
    )

    ap.add_argument(
        "image_file",
        help="Name of the image file to use as the cover picture. "
        "File type must be .jpeg, .jpg, or .png.",
    )

    ap.add_argument(
        "-o",
        "--output-file",
        dest="output_file",
        action="store",
        help="Optional. Name of output file. Default output file name is the "
        "source file name with a date_time stamp added on the right. "
        "If the specified output file already exists it will not be "
        "replaced.",
    )

    ap.add_argument(
        "-d",
        "--delete-tags",
        dest="del_tags",
        action="store_true",
        help="Optional. Delete existing ID3 tags before adding the picture tag.",
    )

    ap.add_argument(
        "-k",
        "--keep-image",
        dest="keep_image",
        action="store_true",
        help="Optional. Keep the temporary image (jpg) file used to add the "
        "picture tag.",
    )

    args = ap.parse_args(arglist)

    mp3_path = Path(args.mp3_file)

    if not mp3_path.exists():
        sys.stderr.write(f"ERROR: Cannot find '{args.mp3_file}'\n")
        error_exit()

    if mp3_path.suffix.lower() != ".mp3":
        sys.stderr.write(f"ERROR: Not a mp3 file name: '{args.mp3_file}'\n")
        error_exit()

    image_path = Path(args.image_file)

    if not image_path.exists():
        sys.stderr.write(f"ERROR: Cannot find '{args.image_file}'\n")
        error_exit()

    if image_path.suffix.lower() not in [".jpg", ".jpeg", ".png"]:
        sys.stderr.write(
            f"ERROR: Not a supported image file type: '{args.image_file}'\n"
        )
        error_exit()

    if args.output_file is None:
        out_path = None
    else:
        out_path = Path(args.output_file)
        if out_path.exists():
            sys.stderr.write(f"ERROR: Cannot overwrite: '{args.output_file}'\n")
            error_exit()

    return AppOptions(
        mp3_path,
        image_path,
        out_path,
        bool(args.del_tags),
        bool(args.keep_image),
    )


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


def main(arglist=None):  # noqa: PLR0912
    print(f"\n{app_title}\n")

    run_dt = datetime.now().strftime("%y%m%d_%H%M%S")

    opt = get_options(arglist)

    print(f"Reading '{opt.mp3_path}'")

    if opt.out_path is None:
        output_path = opt.mp3_path.parent.joinpath(f"{opt.mp3_path.stem}__{run_dt}.mp3")
    else:
        output_path = opt.out_path

    tmpimg_path = output_path.parent.joinpath(f"{opt.image_path.stem}__{run_dt}.jpg")

    print(f"Writing '{output_path}'")

    if output_path.exists():
        print("ERROR: Output file already exists.")
        error_exit()

    make_temp_image_file(opt.image_path, tmpimg_path)

    #  Make a copy of the mp3 file, then modify the copy.

    shutil.copyfile(opt.mp3_path, output_path)

    if opt.del_tags:
        a = MP3(output_path, ID3=ID3)
        if a.tags is None:
            print("No existing tags.")
        else:
            print("Delete existing tags.")
            tags = ID3(output_path)
            tags.delete(None, delete_v1=True, delete_v2=True)
            tags.save()

    audio = MP3(output_path, ID3=ID3)

    try:
        audio.add_tags()
        print("Added tags.")
    except Exception as e:
        if str(e) != "an ID3 tag already exists":
            raise e

    mime_type = "image/png" if opt.image_path.suffix.lower() == ".png" else "image/jpeg"

    image_data = tmpimg_path.open("rb").read()

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

    if opt.keep_tmpimg:
        print(f"Temporary image '{tmpimg_path}' not deleted.")
    else:
        tmpimg_path.unlink()

    return 0


if __name__ == "__main__":
    main()
