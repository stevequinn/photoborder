# Photo Border Thing

A small script to add a border to a jpeg or png photo.

Exif data can also be extracted and added to the border if the mood strikes.

A colour palette can be added to the border as well.

## Usage

```bash
usage: python border.py [-h] [-e] [-p] filename

Add a border and exif data to a jpg or png photo

positional arguments:
  filename

options:
  -h, --help            show this help message and exit
  -e, --exif            print photo exif data on the border
  -p, --palette         Add colour palette to the photo border
  -t, --border_type     Border Type: p for polaroid, s for small, m for medium, l for large, i for instagram (default: s)
  --include             File patterns to include (default: *.jpg *.jpeg *.png, *.JPG, *.JPEG, *.PNG)
  --exclude             File patterns to exclude (default: *_border*)
Made for fun and to solve a little problem.
```

---

> Note: This is a hacked together little script. Use at your own peril...
