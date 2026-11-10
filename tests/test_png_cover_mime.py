"""PNG cover art must be tagged with the JPEG MIME type.

`main` converts every source image to JPEG (via the temporary image file)
before embedding it, but it used to declare the MIME type from the *source*
file suffix. A PNG source was therefore embedded as JPEG bytes labeled
`image/png`, which players that trust the MIME type cannot display.
"""

from __future__ import annotations

from pathlib import Path

from mutagen.id3 import ID3
from PIL import Image

import mp3pic

# One MPEG-1 Layer III frame header (128 kbps, 44.1 kHz, no padding)
# plus filler: just enough well-formed audio for mutagen to sync to.
_MP3_FRAME = bytes.fromhex("fffb9000") + bytes(413)


def _write_test_mp3(path: Path) -> None:
    path.write_bytes(_MP3_FRAME * 20)


def _run_main(tmp_path: Path, image_name: str) -> ID3:
    src_mp3 = tmp_path / "example.mp3"
    _write_test_mp3(src_mp3)
    src_img = tmp_path / image_name
    Image.new("RGB", (400, 200), (255, 0, 0)).save(src_img)
    out_mp3 = tmp_path / "example-with-cover.mp3"

    assert mp3pic.main([str(src_mp3), str(src_img), "-o", str(out_mp3)]) == 0
    return ID3(str(out_mp3))


def test_png_cover_is_tagged_as_jpeg(tmp_path: Path):
    tags = _run_main(tmp_path, "cover.png")
    apic = tags["APIC:Cover Art (front)"]
    assert apic.mime == "image/jpeg"
    assert apic.data[:3] == bytes.fromhex("ffd8ff")


def test_jpeg_cover_mime_unchanged(tmp_path: Path):
    tags = _run_main(tmp_path, "cover.jpg")
    apic = tags["APIC:Cover Art (front)"]
    assert apic.mime == "image/jpeg"
    assert apic.data[:3] == bytes.fromhex("ffd8ff")
