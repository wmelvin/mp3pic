#!/usr/bin/env python3

from pathlib import Path
import argparse
import sys


app_version = "211003.1"

pub_version = "1.0.dev1"

app_title = f"mp3pic.py - version {app_version}"

confirm_errors = True


def error_exit():
    print("*" * 70)
    if confirm_errors:
        input("ERRORS: Press [Enter] to acknowledge. ")
    else:
        print("Halted due to errors.")
    sys.exit(1)


def main():
    print(f"\n{app_title}\n")

    ap = argparse.ArgumentParser(
        description="Add a picture tag to a mp3 file."
    )

    ap.add_argument(
        "mp3_file", help="Name of the source mp3 file to modify. "
        + "The modified version will be given a new name."
    )

    ap.add_argument(
        "image_file", help="Name of the image file to use as the "
        + "cover picture."
    )

    args = ap.parse_args()

    if not Path(args.mp3_file).exists():
        sys.stderr.write("ERROR: Cannot find '{0}'\n".format(args.mp3_file))
        error_exit()

    if not Path(args.image_file).exists():
        sys.stderr.write("ERROR: Cannot find '{0}'\n".format(args.image_file))
        error_exit()


if __name__ == "__main__":
    main()
