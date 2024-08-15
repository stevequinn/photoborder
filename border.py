"""
Add a border to the image named in the first parameter.
A new image with {filename}_bordered will be generated.
TODO: Improve font sizing for small and medium border sizing. It's too small at the moment.
TODO: Fix Shutter Speed fraction for weird shutter speeds such as from phones.
TODO: Add directory recursion option with the idea to process 100's or 1000's of images.
TODO: Add file path pattern filtering blacklist/whitelist options.
"""
import os
import math
import argparse
from enum import Enum
from dataclasses import dataclass
from PIL import Image
from exif import get_exif
from palette import load_image_color_palette, overlay_palette
from text import create_font, create_bold_font, draw_text_on_image

class BorderType(Enum):
    POLAROID = 'p'
    SMALL = 's'
    MEDIUM = 'm'
    LARGE = 'l'

    def __str__(self):
        return self.value

@dataclass
class Border:
    top: int
    right: int
    bottom: int
    left: int
    border_type: BorderType

parser = argparse.ArgumentParser(
    prog='python border.py',
    description='Add a border and exif data to a jpg or png photo',
    epilog='Made for fun and to solve a little problem.'
)
parser.add_argument('filename')
parser.add_argument('-e', '--exif', action='store_true',
                    help='print photo exif data on the border')
parser.add_argument('-p', '--palette', action='store_true',
                    help='Add colour palette to the photo border')
parser.add_argument('-t', '--border_type', type=BorderType, choices=list(BorderType),
                    default=BorderType.SMALL, help='Border Type: p for polaroid, s for small, m for medium, l for large')
args = parser.parse_args()

def get_border_size(img_width: int, img_height: int, reduceby: int=4) -> int:
    """Calculate an image border size based on the golden ratio.

    Args:
        img_width (number): Source image width
        img_height (number): Source image height
        reduceby (int): Reduce the border by a factor of this

    Returns:
        int: The border size
    """
    # Use golden ratio to determine border size from image size.
    golden_ratio = (1 + 5 ** 0.5) / 2
    img_area = img_width * img_height
    canvas_area = img_area * golden_ratio
    border_size = math.ceil(math.sqrt(canvas_area - img_area) / reduceby)

    return border_size

def create_border(imgw: int, imgh: int, border_type: Border) -> Border:
    border = None
    reduceby = None
    reduceby_bottom = None

    if border_type == BorderType.POLAROID:
        reduceby = 32
        reduceby_bottom = 6
    elif border_type == BorderType.SMALL:
        reduceby = 32
        reduceby_bottom = reduceby
    elif border_type == BorderType.MEDIUM:
        reduceby = 16
        reduceby_bottom = reduceby
    elif border_type == BorderType.LARGE:
        reduceby = 6
        reduceby_bottom = reduceby

    border_size = get_border_size(imgw, imgh, reduceby)
    border_size_bottom = get_border_size(imgw, imgh, reduceby_bottom)
    border = Border(border_size, border_size, border_size_bottom, border_size, border_type)

    return border

def draw_border(img: Image, border: Border) -> Image:
    w = img.width + border.left + border.right
    h = img.height + border.top + border.bottom
    canvas = Image.new("RGB", (w, h), (255, 255, 255, 0))
    canvas.paste(img, (border.left, border.top))

    return canvas

def draw_exif(img: Image, exif: dict, border: Border) -> Image:
    centered = border.border_type in (BorderType.POLAROID, BorderType.LARGE)
    font = create_font(round(border.bottom / 8))
    heading_font = create_bold_font(round(border.bottom / 6))
    margin = heading_font.size / 2
    # 3 Lines of text. 1 heading, two normal.
    total_font_height = heading_font.size + (2 * margin) + (2 * font.size)

    # Vertical align text in bottom border based on total font block height.
    y = img.height - border.bottom + \
        (border.bottom / 2) - (total_font_height / 2)

    x = border.left

    text = f"{exif['Make']} {exif['Model']}"
    text_img, y = draw_text_on_image(img, text, (x,y), centered, heading_font, fill=(100, 100, 100))

    text = f"{exif['LensModel']}"
    text_img, y = draw_text_on_image(text_img, text, (x,y), centered, font, fill=(128, 128, 128))

    text = f"{exif['FocalLength']} {exif['FNumber']} {exif['ISOSpeedRatings']} {exif['ExposureTime']}"
    text_img, y = draw_text_on_image(text_img, text, (x,y), centered, font, fill=(128, 128, 128))

    return text_img

def save(path: str, add_exif: bool, add_palette: bool, border_type: BorderType) -> str:
    """ Add a border to an image
    Supported image types ['jpg', 'jpeg', 'png'].

    Args:
        path (str): The image file path
        add_exif (bool): Add photo exif information to the border
        add_palette (bool): Add colour palette information to the border.
                            Currently only supported on Polaroid border types.
        border_type (BorderType): The type of border to add to the photo.

    """
    filetypes = ['jpg', 'jpeg', 'png']
    path_dot_parts = path.split('.')
    ext = path_dot_parts[-1:][0]
    filename = ".".join(path_dot_parts[:-1])

    if not ext or ext.lower() not in filetypes:
        print(f'ERROR: image must be one of {filetypes}')
        return

    exif = None
    img = Image.open(path)
    border = create_border(img.width, img.height, border_type)
    img_with_border = draw_border(img, border)
    save_as = f'{filename}_border-{border.border_type}'

    if add_exif:
        exif = get_exif(img)
        if exif:
            img_with_border = draw_exif(img_with_border, exif, border)
            save_as = f'{save_as}_exif'

    if add_palette:
        palette_size = round(border.bottom / 3)
        color_palette = load_image_color_palette(img, palette_size)
        # Position palette on right side of bottom border
        palette_x = img_with_border.width - border.right - color_palette.width
        palette_y = img_with_border.height - round(border.bottom / 2) - round(color_palette.height / 2)
        img_with_border = overlay_palette(img=img_with_border,
                                          color_palette=color_palette,
                                          offset=(palette_x, palette_y))
        save_as = f'{save_as}_palette'

    # There are two parts to JPEG quality. The first is the quality setting.
    #
    # JPEG also uses chroma subsampling, assuming that color hue changes are
    # less important than lightness changes and some information can be safely
    # thrown away. Unfortunately in demanding applications this isn't always true,
    # and you can most easily notice this on red edges. PIL didn't originally expose
    # a documented setting to control this aspect.
    #
    # Pascal Beyeler discovered the option which disables chroma subsampling. You can set
    # subsampling=0 when saving an image and the image looks way sharper!
    #
    # Note also that the documentation claims quality=95 is the best quality setting and
    # that anything over 95 should be avoided. This may be a change from earlier versions of PIL.
    #
    # ref: https://stackoverflow.com/a/19303889
    save_path = f'{save_as}.{ext}'
    img_with_border.save(save_path, subsampling=0, quality=95)

    # Clean up
    img_with_border.close()
    img.close()

    return save_path


if os.path.isdir(args.filename):
    for file in os.listdir(args.filename):
        print(f'Adding border to {file}')
        save(os.path.join(args.filename, file), args.exif, args.palette, BorderType(args.border_type))
else:
    # print(f'Adding border to {args.filename}')
    save_path = save(args.filename, args.exif, args.palette, BorderType(args.border_type))
    print(save_path)

# from PIL import Image, ImageOps
# for i in list-of-images:
#   img = Image.open(i)
#   img_with_border = ImageOps.expand(img,border=300,fill='black')
#   img_with_border.save('bordered-%s' % i)
