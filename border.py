"""
Add a border to the image named in the first parameter.
A new image with border_{filename} will be generated.
"""
import os
import math
import argparse
from fractions import Fraction
from PIL import Image, ImageOps, ImageDraw, ImageFont
from PIL.ExifTags import TAGS

parser = argparse.ArgumentParser(
    prog='PhotoBorder',
    description='Add a border and exif data to a jpg or png photo',
    epilog='Made for fun and to solve a little problem.'
)
parser.add_argument('filename')
parser.add_argument('-e', '--exif', action='store_true', help='print photo exif data on the border')
parser.add_argument('-c', '--colour', default='white', help='the border colour')
args = parser.parse_args()

def decimal_to_fraction(decimal):
    """Convert a decimal value to a fraction display.
    Used to display shutter speed values.
    """
    result = str(Fraction(decimal))

    return result

def get_border_size(img_width, img_height):
    """Calculate an image border size based on the golden ratio.

    Args:
        img_width (number): Source image width
        img_height (number): Source image height

    Returns:
        int: The border size
    """
    # Use golden ratio to determine border size from image size.
    golden_ratio = (1 + 5 ** 0.5) / 2
    img_area = img_width * img_height
    canvas_area = img_area * golden_ratio
    # I find just dividing by 4 too large for me. Tripling it looks better IMO.
    border_size = math.ceil(math.sqrt(canvas_area - img_area) / 12)

    return border_size

def get_exif(img: Image):
    """Load the exif data from an image.

    Args:
        img (Image): Pillow image object.

    Returns:
        dict: dictionary with exif data
    """
    exif_data = img._getexif()
    exif_dict = {}

    if exif_data:
        # Iterate through the EXIF data and store it in the dictionary
        for tag_id in exif_data:
            tag = TAGS.get(tag_id, tag_id)
            data = exif_data.get(tag_id)
            if isinstance(data, bytes):
                data = data.decode()
            exif_dict[tag] = data

    # Print the EXIF data dictionary
    # print(exif_dict)

    return exif_dict

def write_text_on_image(img, text_lines, x, y, font_size=30):
    """Add text to an image

    Args:
        img (Image): Pillow image object
        text_lines ([str]): List of str to be written to image
        x (int): First line starting X position
        y (int): First line starting Y position
        font_size (int, optional): Font pixel size. Defaults to 30.

    Returns:
        _type_: _description_
    """
    # Create a draw object
    draw = ImageDraw.Draw(img)

    # Load a font
    font = ImageFont.truetype("Avenir.ttc", font_size)

    # Iterate through the text lines and draw them on the image
    for line in text_lines:
        draw.text((x, y), line, font=font, fill=(100, 100, 100))
        # Increment the y-coordinate by font_size and portion of font_size padding for the next line
        y += font_size + (font_size / 3)

    return img

def save(path, colour, add_exif):
    """ Add a border to an image
    Supported image types ['jpg', 'jpeg', 'png'].

    Args:
        path (str): The image file path
    """
    filetypes = ['jpg', 'jpeg', 'png']
    [filename, ext] = path.split('.')

    if not ext or ext.lower() not in filetypes:
        print(f'ERROR: image must be one of {filetypes}')
        return

    img = Image.open(path)
    border_size = get_border_size(img.width, img.height)
    img_with_border = ImageOps.expand(img, border=border_size, fill=colour)

    if add_exif:
        exif = get_exif(img)
        # print(exif)
        if exif:
            # exif_keys = ['Make', 'Model', 'LensMake', 'LensModel', 'FNumber', 'FocalLength', 'ISOSpeedRatings']
            exif_print = []
            exif_print.append(f"{exif.get('Make', '').strip()} {exif.get('Model', '').strip()}".strip())
            exif_print.append(f"{exif.get('LensMake', '').strip()} {exif.get('LensModel', '').strip()}".strip())
            exif_print.append(f"{exif.get('FocalLength', '')}mm   F{exif.get('FNumber', '')}   ISO {exif.get('ISOSpeedRatings', '')}   {decimal_to_fraction(exif.get('ExposureTime', '0'))} sec".strip())
            # Add exif text to the bottom left of the image border with 20px top padding
            font_size = border_size / 6
            font_x = border_size
            font_y = img_with_border.height - border_size + (font_size / 2)
            img_with_border = write_text_on_image(img_with_border, exif_print, font_x, font_y, font_size)

    img_with_border.save(f'{filename}_bordered.{ext}')


if os.path.isdir(args.filename):
    for file in os.listdir(args.filename):
        print(f'Adding border to {file}')
        save(os.path.join(args.filename, file), args.colour, args.exif)
else:
    print(f'Adding border to {args.filename}')
    save(args.filename, args.colour, args.exif)

# from PIL import Image, ImageOps
# for i in list-of-images:
#   img = Image.open(i)
#   img_with_border = ImageOps.expand(img,border=300,fill='black')
#   img_with_border.save('bordered-%s' % i)
