
# mp3pic

The mp3pic.py command-line tool adds a cover picture to a mp3 file. It was initially built to add cover art to mp3 files that already have ID3 tags with other metadata (though it will add the ID3 tag if one does not exist), so it does not currently provide for adding or updating any other metadata.

The [mutagen](https://pypi.org/project/mutagen/) library is used to modify the ID3 tag in the mp3 file.

The [Pillow](https://pypi.org/project/Pillow/) library is used to modify the image, if needed, prior to adding it to the mp3 file.

## Usage

```
usage: mp3pic.py [-h] [-o OUTPUT_FILE] [-d] [-k] mp3_file image_file

Add a picture tag to a mp3 file.

positional arguments:
  mp3_file              Name of the source mp3 file to modify. The modified
                        version will be given a new name.
  image_file            Name of the image file to use as the cover picture.
                        File type must be .jpeg, .jpg, or .png.

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        Optional. Name of output file. Default output file
                        name is the source file name with a date_time stamp
                        added on the right. If the specified output file
                        already exists it will not be replaced.
  -d, --delete-tags     Optional. Delete existing ID3 tags before adding the
                        picture tag.
  -k, --keep-image      Optional. Keep the temporary image (jpg) file used to
                        add the picture tag.
```

## Reference

### ID3

Wikipedia: [ID3](https://en.wikipedia.org/wiki/ID3)

### Mutagen

Mutagen docs for the [Main Module](https://mutagen.readthedocs.io/en/latest/api/base.html#module-mutagen)


[MP3](https://mutagen.readthedocs.io/en/latest/api/mp3.html#mutagen.mp3.MP3) class

[ID3](https://mutagen.readthedocs.io/en/latest/api/id3.html) class

[mutagen.id3.APIC](https://mutagen.readthedocs.io/en/latest/api/id3_frames.html#mutagen.id3.APIC) - Frame Base Classes for Picture

[mutagen.id3.Encoding](https://mutagen.readthedocs.io/en/latest/api/id3.html#mutagen.id3.Encoding)

[mutagen.id3.PictureType](https://mutagen.readthedocs.io/en/latest/api/id3.html#mutagen.id3.PictureType)

User Guide: [Dealing with Frame Uniqueness of ID3 Frames](https://mutagen.readthedocs.io/en/latest/user/id3.html#dealing-with-frame-uniqueness-of-id3-frames)

### Pillow

Pillow — Pillow (PIL Fork) [documentation](https://pillow.readthedocs.io/en/stable/)

[Image.resize](https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.resize)

[Image.crop](https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.crop)

