# Photo Border Thing

A small script to add a border to a jpeg or png photo.

Exif data can also be extracted and added to the border if the mood strikes.

A colour palette can be added to the border as well.

## Installation

```git clone https://github.com/stevequinn/photoborder```

```cd photoborder```

```pip install -r requirements.txt```

## Usage

```bash
usage: python main.py [-h] [-e] [-p] [-t{s,m,l,p,i}] filename

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

## Examples

![alt text](doc/images/20241108_20241108DSCF0043_border-p_exif_palette.jpeg)
*`> python main.py -t p -e -p image.jpeg`*

![alt text](doc/images/20241108_20241108DSCF0043_border-s_exif.jpeg)
*`> python main.py -t s -e image.jpeg`*

![alt text](doc/images/20241108_20241108DSCF0043_border-m_exif.jpeg)
*`> python main.py -t m -e image.jpeg`*

![alt text](doc/images/20241108_20241108DSCF0043_border-l_exif.jpeg)
*`> python main.py -t l -e image.jpeg`*

![alt text](doc/images/20241108_20241108DSCF0043_border-i_exif.jpeg)
*`> python main.py -t i -e image.jpeg`*
