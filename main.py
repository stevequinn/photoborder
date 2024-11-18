"""
 Add a border to the image named in the first parameter.
 A new image with {filename}_bordered will be generated.
 TODO: Read up on sorting images by appearance https://github.com/Visual-Computing/LAS_FLAS/blob/main/README.md
 """

import os
import argparse
import logging
from PIL import Image
from exif import get_exif
from filemanager import should_include_file, get_directory_files
from palette import load_image_color_palette, overlay_palette
from border import BorderType, create_border, draw_border, draw_exif
from text import validate_font

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

def parse_arguments():
    parser = argparse.ArgumentParser(
        prog='python border.py',
        description='Add a border and exif data to jpg or png photos',
        epilog='Made for fun and to solve a little problem.'
    )
    parser.add_argument('path',
                        help='File or directory path')
    parser.add_argument('-e', '--exif', action='store_true', default=False,
                        help='Print photo exif data on the border')
    parser.add_argument('-p', '--palette', action='store_true', default=False,
                        help='Add colour palette to the photo border')
    parser.add_argument('-t', '--border_type', type=BorderType, choices=list(BorderType), default=BorderType.SMALL,
                        help='Border Type: p for polaroid, s for small, m for medium, l for large, i for instagram')
    parser.add_argument('-r', '--recursive', action='store_true', default=False,
                        help='Process directories recursively')
    parser.add_argument('--include', nargs='+', default=['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG'],
                        help='File patterns to include (default: *.jpg *.jpeg *.png, *.JPG, *.JPEG, *.PNG')
    parser.add_argument('--exclude', nargs='+', default=["*_border*"],
                        help='File patterns to exclude (default: *_border*)')
    parser.add_argument('-f', '--font', default='Roboto-Regular.ttf',
                        help='Font file in fonts directory')
    parser.add_argument('-fb', '--fontbold', default='Roboto-Medium.ttf',
                        help='Bold font file in fonts directory')
    return parser.parse_args()


def process_image(path: str, add_exif: bool, add_palette: bool, border_type: BorderType, fontname: str, boldfontname: str) -> str:
    """ Add a border to an image
    Supported image types ['jpg', 'jpeg', 'png'].

    Args:
        path (str): The image file path
        add_exif (bool): Add photo exif information to the border
        add_palette (bool): Add colour palette information to the border.
                            Currently only supported on Polaroid border types.
        border_type (BorderType): The type of border to add to the photo.
        fontname (str): name of the font file to use
        boldfontname (str): name of the bold font file to use
    """
    filetypes = ['jpg', 'jpeg', 'png']
    path_dot_parts = path.split('.')
    ext = path_dot_parts[-1:][0]
    filename = ".".join(path_dot_parts[:-1])

    if not ext or ext.lower() not in filetypes:
        logger.error(f'Image must be one of {filetypes}')
        return

    exif = None
    img = Image.open(path)
    border = create_border(img.width, img.height, border_type)
    img_with_border = draw_border(img, border)
    save_as = f'{filename}_border-{border.border_type}'

    if add_exif:
        exif = get_exif(img)
        if exif:
            moduledir = os.path.dirname(os.path.abspath(__file__))
            fontdir = os.path.join(moduledir, "fonts")
            font_path = os.path.join(fontdir, fontname)
            bold_font_path = os.path.join(fontdir, boldfontname)

            # Validate fonts before processing any images
            error_messages = [f"Font '{f}' not found in the font directory." for f in [
                font_path, bold_font_path] if not validate_font(f)]
            if len(error_messages) > 0:
                raise ValueError(error_messages)

            img_with_border = draw_exif(img_with_border, exif, border, font_path, bold_font_path)
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
    exifdata = img.getexif()  # extracts original EXIF data from Image.open(path)
    img_with_border.save(save_path, exif=exifdata, subsampling=0, quality=95)

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
            logger.info(f'Skipping {args.path} as it does not match the include/exclude patterns')
    else:
        logger.error(f'{args.path} is not a valid file or directory')

    for path in paths:
        logger.info(f'Adding border to {path}')
        save_path = process_image(path, args.exif, args.palette, args.border_type, args.font, args.fontbold)
        logger.info(f'Saved as {save_path}')

if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        logger.error(e)
