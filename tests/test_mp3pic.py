"""
Rather than trying to mock all the things, these tests require some local test
data files.

The location of those files is configured in a '.env' file with the following
variables:

TEST_MP3_FILE="<path-to-file>.mp3"
TEST_IMG_300="<path-to-image-300x300px>.<jpg|png>"
TEST_IMG_GT_300="<path-to-image-greater-than-300x300px>.<jpg|png>"
TEST_IMG_LT_300="<path-to-image-less-than-300x300px>.<jpg|png>"
TEST_IMG_HT_GT_300="<path-to-image-height-greater-than-300px-width-300px>.<jpg|png>"
TEST_IMG_WD_LT_300="<path-to-image-width-less-than-300px-height-300px>.<jpg|png>"

Only basic operation (files are created) is tested. The temporary output
can be reviewed visually to make sure the added images look correct in
the resulting mp3 files.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

import dotenv
import pytest

import mp3pic

dotenv.load_dotenv()


def skipif_test_env_not_ready():
    """
    Skip test if any required environment variable is not set, or a specified
    file is not found. Stops checking on the first missing item.
    """
    env_vars = [
        "TEST_MP3_FILE",
        "TEST_IMG_300",
        "TEST_IMG_GT_300",
        "TEST_IMG_LT_300",
        "TEST_IMG_HT_GT_300",
        "TEST_IMG_WD_LT_300",
    ]
    err = ""
    for v in env_vars:
        fn = os.environ.get(v)
        if fn:
            if not Path(fn).expanduser().resolve().exists():
                err = f"Test file not found: {fn}"
                break
        else:
            err = f"Environment variable not set: {v}"
            break

    return pytest.mark.skipif(bool(err), reason=err)


@pytest.fixture(scope="module")
def temp_mp3file(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, Path]:
    dir_path = tmp_path_factory.mktemp("test_mp3")
    mp3_path = dir_path / "example.mp3"
    if not mp3_path.exists():
        s = os.environ.get("TEST_MP3_FILE")
        src_mp3 = Path(s).expanduser().resolve()
        assert src_mp3.exists()
        shutil.copy(str(src_mp3), str(mp3_path))
    assert mp3_path.exists()
    return dir_path, mp3_path


@skipif_test_env_not_ready()
def test_example_mp3_exists(temp_mp3file: tuple[Path, Path]):
    test_dir, mp3_path = temp_mp3file
    assert mp3_path.exists()

    #  Write the temporary directory path to a text file in the project
    #  directory for convenience when reviewing the temporary output.
    (Path.cwd() / "_test_output.txt").write_text(str(test_dir))


@skipif_test_env_not_ready()
def test_mp3pic_default(temp_mp3file: tuple[Path, Path], tmp_path: Path):
    test_dir, mp3 = temp_mp3file
    img = os.environ.get("TEST_IMG_300")
    assert Path(img).exists()
    n_mp3 = len(list(test_dir.glob("*.mp3")))
    args = [str(mp3), img]
    mp3pic.main(args)
    assert len(list(test_dir.glob("*.mp3"))) == n_mp3 + 1


@skipif_test_env_not_ready()
def test_mp3pic_output(temp_mp3file: tuple[Path, Path], tmp_path: Path):
    _, mp3 = temp_mp3file
    out_mp3 = tmp_path / "example-with-cover-art.mp3"
    img = os.environ.get("TEST_IMG_300")
    args = [str(mp3), img, "--output-file", str(out_mp3)]
    mp3pic.main(args)
    files = list(out_mp3.parent.glob("*.mp3"))
    assert len(files) == 1
    assert out_mp3.name in [x.name for x in files]


@skipif_test_env_not_ready()
def test_mp3pic_scale_down(temp_mp3file: tuple[Path, Path], tmp_path: Path):
    _, src_mp3 = temp_mp3file
    out_mp3 = tmp_path / "example-scale-down.mp3"
    src_img = Path(os.environ.get("TEST_IMG_GT_300"))

    #  Make a copy of the original image for review under tmp.
    img_copy = tmp_path / f"{src_img.stem}-orig{src_img.suffix}"
    shutil.copy(str(src_img), str(img_copy))

    args = [str(src_mp3), str(src_img), "-k", "--output-file", str(out_mp3)]
    mp3pic.main(args)
    files = list(out_mp3.parent.glob("*.mp3"))
    assert len(files) == 1
    assert out_mp3.name in [x.name for x in files]

    #  The '-k' switch means keep the temporary image file.
    #  It should be in the output location.
    assert len(list(out_mp3.parent.glob(f"*{src_img.suffix}"))) == 1


@skipif_test_env_not_ready()
def test_mp3pic_scale_up(temp_mp3file: tuple[Path, Path], tmp_path: Path):
    _, src_mp3 = temp_mp3file
    out_mp3 = tmp_path / "example-scale-up.mp3"
    src_img = Path(os.environ.get("TEST_IMG_LT_300"))

    #  Make a copy of the original image for review under tmp.
    img_copy = tmp_path / f"{src_img.stem}-orig{src_img.suffix}"
    shutil.copy(str(src_img), str(img_copy))

    args = [str(src_mp3), str(src_img), "--keep-image", "--output-file", str(out_mp3)]
    mp3pic.main(args)
    files = list(out_mp3.parent.glob("*.mp3"))
    assert len(files) == 1
    assert out_mp3.name in [x.name for x in files]


@skipif_test_env_not_ready()
def test_mp3pic_crop_height_and_delete_tags(
    temp_mp3file: tuple[Path, Path], tmp_path: Path
):
    _, src_mp3 = temp_mp3file
    out_mp3 = tmp_path / "example-crop-height.mp3"
    src_img = Path(os.environ.get("TEST_IMG_HT_GT_300"))

    #  Make a copy of the original image for review under tmp.
    img_copy = tmp_path / f"{src_img.stem}-orig{src_img.suffix}"
    shutil.copy(str(src_img), str(img_copy))

    args = [
        str(src_mp3),
        str(src_img),
        "--delete-tags",
        "--keep-image",
        "--output-file",
        str(out_mp3),
    ]
    mp3pic.main(args)
    files = list(out_mp3.parent.glob("*.mp3"))
    assert len(files) == 1
    assert out_mp3.name in [x.name for x in files]


@skipif_test_env_not_ready()
def test_mp3pic_crop_width_and_delete_tags(
    temp_mp3file: tuple[Path, Path], tmp_path: Path
):
    _, src_mp3 = temp_mp3file
    out_mp3 = tmp_path / "example-crop-width.mp3"
    src_img = Path(os.environ.get("TEST_IMG_WD_LT_300"))

    #  Make a copy of the original image for review under tmp.
    img_copy = tmp_path / f"{src_img.stem}-orig{src_img.suffix}"
    shutil.copy(str(src_img), str(img_copy))

    args = [str(src_mp3), str(src_img), "-d", "-k", "--output-file", str(out_mp3)]
    mp3pic.main(args)
    files = list(out_mp3.parent.glob("*.mp3"))
    assert len(files) == 1
    assert out_mp3.name in [x.name for x in files]
