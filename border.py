"""
Add a border to the image named in the first parameter.
A new image with {filename}_bordered will be generated.
TODO: Add thin border option with diff exif layout
TODO: Fix Shutter Speed fraction for weird shutter speeds such as from phones.
TODO: Add directory recursion option with the idea to process 100's or 1000's of images.
TODO: Add file path pattern filtering blacklist/whitelist options.
"""
import os
import math
import argparse
from dataclasses import dataclass
from PIL import Image
from exif import get_exif
from palette import load_image_color_palette, overlay_palette
from text import create_font, create_bold_font, write_centred_text_on_image

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
args = parser.parse_args()





def get_border_size(img_width, img_height, reduceby=4):
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


@dataclass
class Border:
    top: int
    right: int
    bottom: int
    left: int

def create_polaroid_border(img: Image) -> tuple[Image.Image, Border]:
    border_size = get_border_size(img.width, img.height, 32)
    border_bottom_size = get_border_size(img.width, img.height, 6)
    border = Border(border_size, border_size, border_bottom_size, border_size)
    w = img.width + border.left + border.right
    h = img.height + border.top + border.bottom
    canvas = Image.new("RGB", (w, h), (255, 255, 255, 0))
    canvas.paste(img, (border.left, border.top))

    return canvas, border


def draw_polaroid_exif(img: Image, exif: dict, border: Border) -> Image:
    heading_font_size = round(border.bottom / 6)
    font_size = round(border.bottom / 8)
    margin = heading_font_size / 2
    total_font_height = heading_font_size + (2 * margin) + (2 * font_size)

    # text = f"Shot on {exif.get('Make', '').strip()} {exif.get('Model', '').strip()}".strip()
    text = f"{exif['Make']} {exif['Model']}"
    # Vertical align text in bottom border based on total font block height.
    y = img.height - border.bottom + \
        (border.bottom / 2) - (total_font_height / 2)
    bold_font = create_bold_font(heading_font_size)
    text_img = write_centred_text_on_image(
        img, text, y, bold_font, fill=(100, 100, 100))
    y += heading_font_size + margin

    font = create_font(font_size)
    text = f"{exif['LensModel']}"
    # f"{exif.get('LensMake', '').strip()} {exif.get('LensModel', '').strip()}".strip())
    text_img = write_centred_text_on_image(text_img,
                                           text=text,
                                           y=y,
                                           font=font,
                                           fill=(128, 128, 128))
    y += font_size + margin
    text = f"{exif['FocalLength']} {exif['FNumber']} {exif['ISOSpeedRatings']} {exif['ExposureTime']}"
    text_img = write_centred_text_on_image(text_img,
                                           text=text,
                                           y=y,
                                           font=font,
                                           fill=(128, 128, 128))

    return text_img


def save(path, add_exif, add_palette):
    """ Add a border to an image
    Supported image types ['jpg', 'jpeg', 'png'].

    Args:
        path (str): The image file path
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
    # img_with_border = ImageOps.expand(img, border=border_size, fill=colour)
    img_with_border, border = create_polaroid_border(img)

    if add_exif:
        exif = get_exif(img)
        if exif:
            img_with_border = draw_polaroid_exif(img_with_border, exif, border)

    if add_palette:
        palette_size = round(border.bottom / 3)
        color_palette = load_image_color_palette(img, palette_size)
        # Position palette on right side of bottom border
        palette_x = img_with_border.width - border.right - color_palette.width
        palette_y = img_with_border.height - round(border.bottom / 2) - round(color_palette.height / 2)
        img_with_border = overlay_palette(img=img_with_border,
                                          color_palette=color_palette,
                                          offset=(palette_x, palette_y))

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
    save_as = filename.replace('_border', '').replace('_exif', '')
    save_as = f'{save_as}_border' + ('_exif' if exif else '')
    save_path = f'{save_as}.{ext}'
    img_with_border.save(save_path, subsampling=0, quality=95)

    # Clean up
    img_with_border.close()
    img.close()

    return save_path


if os.path.isdir(args.filename):
    for file in os.listdir(args.filename):
        print(f'Adding border to {file}')
        save(os.path.join(args.filename, file), args.exif, args.palette)
else:
    # print(f'Adding border to {args.filename}')
    save_path = save(args.filename, args.exif, args.palette)
    print(save_path)

# from PIL import Image, ImageOps
# for i in list-of-images:
#   img = Image.open(i)
#   img_with_border = ImageOps.expand(img,border=300,fill='black')
#   img_with_border.save('bordered-%s' % i)
