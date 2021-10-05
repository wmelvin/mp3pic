
#mp3pic.py

This utility script adds a cover picture to a mp3 file. It was initially built to add cover art to mp3 files that already have ID3 tags with other metadata (though it will add the ID3 tag if one does not exist), so it does not currently provide for adding or updating any other metadata.

The [mutagen](https://pypi.org/project/mutagen/) library is used to modify the ID3 tag in the mp3 file.

The [Pillow](https://pypi.org/project/Pillow/) library is used to modify the image, if needed, prior to adding it to the mp3 file.


##Reference

###ID3

Wikipedia: [ID3](https://en.wikipedia.org/wiki/ID3)

###Mutagen

Mutagen docs for the [Main Module](https://mutagen.readthedocs.io/en/latest/api/base.html#module-mutagen)


[MP3](https://mutagen.readthedocs.io/en/latest/api/mp3.html#mutagen.mp3.MP3) class

[ID3](https://mutagen.readthedocs.io/en/latest/api/id3.html) class

[mutagen.id3.APIC](https://mutagen.readthedocs.io/en/latest/api/id3_frames.html#mutagen.id3.APIC) - Frame Base Classes for Picture

[mutagen.id3.Encoding](https://mutagen.readthedocs.io/en/latest/api/id3.html#mutagen.id3.Encoding)

[mutagen.id3.PictureType](https://mutagen.readthedocs.io/en/latest/api/id3.html#mutagen.id3.PictureType)

User Guide: [Dealing with Frame Uniqueness of ID3 Frames](https://mutagen.readthedocs.io/en/latest/user/id3.html#dealing-with-frame-uniqueness-of-id3-frames)

###Pillow

Pillow — Pillow (PIL Fork) [documentation](https://pillow.readthedocs.io/en/stable/)

[Image.resize](https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.resize)

[Image.crop](https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.crop)

---
Updated 2021-10-06