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
from fnmatch import fnmatch
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
                        default=BorderType.SMALL, help='Border Type: p for polaroid, s for small, m for medium, l for large')
    parser.add_argument('-r', '--recursive', action='store_true', default=False,
                        help='Process directories recursively')
    parser.add_argument('--include', nargs='+', default=['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG'],
                        help='File patterns to include (default: *.jpg *.jpeg *.png)')
    parser.add_argument('--exclude', nargs='+', default=["*_border*"],
                        help='File patterns to exclude')
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

def create_border(imgw: int, imgh: int, border_type: Border) -> Border:
    reduceby_map = {
        BorderType.POLAROID: (32, 6),
        BorderType.SMALL: (32, 32),
        BorderType.MEDIUM: (16, 16),
        BorderType.LARGE: (6, 6),
    }
    reduceby, reduceby_bottom = reduceby_map[border_type]

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
    font = create_font(max(round(border.bottom / 8), 11)) # min font size of 10
    heading_font = create_bold_font(max(round(border.bottom / 6), 12)) # min font size of 12

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
    text_img, (x, y) = draw_text_on_image(img, text, (x,y), centered, heading_font, fill=(100, 100, 100))

    text = f"{exif['LensMake']} {exif['LensModel']}"
    text_img, (x, y) = draw_text_on_image(text_img, text, (x,y), centered, font, fill=(128, 128, 128))

    text = f"{exif['FocalLength']}  {exif['FNumber']}  {exif['ISOSpeedRatings']}  {exif['ExposureTime']}"
    text_img, (x, y) = draw_text_on_image(text_img, text, (x,y), centered, font, fill=(128, 128, 128))

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

def should_process_file(filename: str, include_patterns: list[str], exclude_patterns: list[str]) -> bool:
    return any(fnmatch(filename, pattern) for pattern in include_patterns) and \
           not any(fnmatch(filename, pattern) for pattern in exclude_patterns)

def process_directory(directory: str, add_exif: bool, add_palette: bool, border_type: BorderType, recursive: bool, include_patterns: list[str], exclude_patterns: list[str]):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if should_process_file(file, include_patterns, exclude_patterns):
                file_path = os.path.join(root, file)
                print(f'Adding border to {file_path}')
                save_path = process_image(file_path, add_exif, add_palette, border_type)
                print(f'Saved as {save_path}')

        if not recursive:
            break

def main():
    args = parse_arguments()

    if os.path.isdir(args.path):
        process_directory(args.path, args.exif, args.palette, args.border_type, args.recursive, args.include, args.exclude)
    elif os.path.isfile(args.path):
        if should_process_file(args.path, args.include, args.exclude):
            save_path = process_image(args.path, args.exif, args.palette, args.border_type)
            print(f'Saved as {save_path}')
        else:
            print(f'Skipping {args.path} as it does not match the include/exclude patterns')
    else:
        print(f'Error: {args.path} is not a valid file or directory')

if __name__ == "__main__":
    main()
