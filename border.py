"""
Add a border to the image named in the first parameter.
A new image with {filename}_bordered will be generated.
TODO: Read up on sorting images by appearance https://github.com/Visual-Computing/LAS_FLAS/blob/main/README.md
"""
import os
import math
import argparse
from enum import Enum
from dataclasses import dataclass
from PIL import Image
import text as tm
from exif import get_exif
from filemanager import should_include_file, get_directory_files
from palette import load_image_color_palette, overlay_palette

class BorderType(Enum):
    POLAROID = 'p'
    SMALL = 's'
    MEDIUM = 'm'
    LARGE = 'l'
    INSTAGRAM = 'i'

    def __str__(self):
        return self.value

@dataclass
class Border:
    top: int
    right: int
    bottom: int
    left: int
    border_type: BorderType

def parse_arguments():
    parser = argparse.ArgumentParser(
        prog='python border.py',
        description='Add a border and exif data to jpg or png photos',
        epilog='Made for fun and to solve a little problem.'
    )
    parser.add_argument('path', help='File or directory path')
    parser.add_argument('-e', '--exif', action='store_true', default=False,
                        help='Print photo exif data on the border')
    parser.add_argument('-p', '--palette', action='store_true', default=False,
                        help='Add colour palette to the photo border')
    parser.add_argument('-t', '--border_type', type=BorderType, choices=list(BorderType),
                        default=BorderType.SMALL,
                        help='Border Type: p for polaroid, s for small, m for medium, l for large, i for instagram')
    parser.add_argument('-r', '--recursive', action='store_true', default=False,
                        help='Process directories recursively')
    parser.add_argument('--include', nargs='+', default=['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG'],
                        help='File patterns to include (default: *.jpg *.jpeg *.png, *.JPG, *.JPEG, *.PNG')
    parser.add_argument('--exclude', nargs='+', default=["*_border*"],
                        help='File patterns to exclude (default: *_border*)')
    return parser.parse_args()

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

def calculate_ratio_border(width, height, min_border=0, target_ratio=4/5):
    current_ratio = width / height

    if current_ratio > target_ratio:
        # Image is too wide, add vertical borders
        new_height = max(height, math.ceil(width / target_ratio))
        vertical_border = max((new_height - height) // 2, min_border)
        horizontal_border = min_border
    else:
        # Image is too tall, add horizontal borders
        new_width = max(width, math.ceil(height * target_ratio))
        horizontal_border = max((new_width - width) // 2, min_border)
        vertical_border = min_border

    # Adjust to ensure the final image meets the target ratio
    final_width = width + 2 * horizontal_border
    final_height = height + 2 * vertical_border
    final_ratio = final_width / final_height

    if final_ratio > target_ratio:
        additional_vertical = math.ceil(final_width / target_ratio) - final_height
        vertical_border += additional_vertical // 2
    elif final_ratio < target_ratio:
        additional_horizontal = math.ceil(final_height * target_ratio) - final_width
        horizontal_border += additional_horizontal // 2

    return horizontal_border, vertical_border

def create_border(imgw: int, imgh: int, border_type: Border) -> Border:
    # top, right, bottom, left
    reduceby_map = {
        BorderType.POLAROID: (32, 32, 6, 32),
        BorderType.SMALL: (32, 32, 32, 32),
        BorderType.MEDIUM: (16, 16, 16, 16),
        BorderType.LARGE: (6, 6, 6, 6),
        BorderType.INSTAGRAM: (32, 32, 32, 32)
    }
    rtop, rright, rbottom, rleft = reduceby_map[border_type]
    btop = get_border_size(imgw, imgh, rtop)
    bright = get_border_size(imgw, imgh, rright)
    bbottom = get_border_size(imgw, imgh, rbottom)
    bleft = get_border_size(imgw, imgh, rleft)

    if border_type == BorderType.INSTAGRAM:
        # In the case of instagram, we want to enforce an image ratio of 4/5 with a minimum border so the
        # non-padded sides also have a border.
        ratio_border_horizonal, ratio_border_vertical = calculate_ratio_border(imgw, imgh, min_border=btop)
        btop = ratio_border_vertical
        bright = ratio_border_horizonal
        bbottom = ratio_border_vertical
        bleft = ratio_border_horizonal

    border = Border(btop, bright, bbottom, bleft, border_type)

    return border

def draw_border(img: Image, border: Border) -> Image:
    w = img.width + border.left + border.right
    h = img.height + border.top + border.bottom
    canvas = Image.new("RGB", (w, h), (255, 255, 255, 0))
    canvas.paste(img, (border.left, border.top))

    return canvas

def draw_exif(img: Image, exif: dict, border: Border) -> Image:
    centered = border.border_type in (BorderType.POLAROID, BorderType.LARGE, BorderType.INSTAGRAM)
    multiplier = 0.2 if centered else 0.5
    font_size = tm.get_optimal_font_size("Test string", border.bottom * multiplier)
    heading_font_size = tm.get_optimal_font_size("Test string", border.bottom * (multiplier + 0.02))
    font = tm.create_font(font_size)
    heading_font = tm.create_bold_font(heading_font_size)

    # Vertical align text in bottom border based on total font block height.
    if centered:
         # 3 Lines of text. 1 heading, two normal. Minus heading margins. A bit sketchy but it aligns fine.
        total_font_height = heading_font.size + (2 * font.size) - (heading_font.size / 2)
        y = img.height - border.bottom + \
            (border.bottom / 2) - (total_font_height / 2)
    else:
        # y = img.height - (border.bottom / 2) - (heading_font.size / 3)
        y = img.height - (border.bottom / 2) + (heading_font.size / 3)

    x = border.left

    text = f"{exif['Make']} {exif['Model']}"
    text_img, (x, y) = tm.draw_text_on_image(img, text, (x,y), centered, heading_font, fill=(100, 100, 100))

    text = f"{exif['LensMake']} {exif['LensModel']}"
    text_img, (x, y) = tm.draw_text_on_image(text_img, text, (x,y), centered, font, fill=(128, 128, 128))

    text = f"{exif['FocalLength']}  {exif['FNumber']}  {exif['ISOSpeedRatings']}  {exif['ExposureTime']}"
    text_img, (x, y) = tm.draw_text_on_image(text_img, text, (x,y), centered, font, fill=(128, 128, 128))

    return text_img

def process_image(path: str, add_exif: bool, add_palette: bool, border_type: BorderType) -> str:
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

def main():
    args = parse_arguments()
    paths = []

    # Figure out paths to save based on include/exclude opts and allowable file types
    if os.path.isdir(args.path):
        paths = get_directory_files(args.path, args.recursive, args.include, args.exclude)
    elif os.path.isfile(args.path):
        if should_include_file(args.path, args.include, args.exclude):
            paths.append(args.path)
        else:
            print(f'Skipping {args.path} as it does not match the include/exclude patterns')
    else:
        print(f'Error: {args.path} is not a valid file or directory')

    for path in paths:
        print(f'Adding border to {path}')
        save_path = process_image(path, args.exif, args.palette, args.border_type)
        print(f'Saved as {save_path}')

if __name__ == "__main__":
    main()
