"""
Add a border to the image named in the first parameter.
A new image with {filename}_bordered will be generated.
TODO: Refactor into separate modules.
TODO: Add optional colour palette.
TODO: Add thin border option with diff exif layout
TODO: Fix path split when there are multiple . in the file name.
"""
import os
import math
import argparse
from fractions import Fraction
import extcolors
from PIL import Image, ImageDraw, ImageFont
from PIL.ExifTags import TAGS

parser = argparse.ArgumentParser(
    prog='python border.py',
    description='Add a border and exif data to a jpg or png photo',
    epilog='Made for fun and to solve a little problem.'
)
parser.add_argument('filename')
parser.add_argument('-e', '--exif', action='store_true',
                    help='print photo exif data on the border')
args = parser.parse_args()


def decimal_to_fraction(decimal):
    """Convert a decimal value to a fraction display.
    Used to display shutter speed values.
    """
    result = str(Fraction(decimal))

    return result


def get_border_size(img_width, img_height, divisor=4):
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
    # I find just dividing by 4 too large for me. Divide by 16 looks better imo.
    border_size = math.ceil(math.sqrt(canvas_area - img_area) / divisor)
    # border_size = math.ceil(math.sqrt(canvas_area - img_area) / 48)

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


def create_font(size: int) -> ImageFont.FreeTypeFont:
    font = ImageFont.truetype("Avenir.ttc", size)
    return font


def create_bold_font(size: int) -> ImageFont.FreeTypeFont:
    font = ImageFont.truetype("Avenir.ttc", size, index=8)
    return font


def write_centred_text_on_image(img: Image, text, y, font_size=30, bold=False, fill=(100, 100, 100)):
    """Add centred text to an image

    Args:
        img (Image): Pillow image object
        text (str): str to be written to image
        x (int): First line starting X position
        y (int): First line starting Y position
        font_size (int, optional): Font pixel size. Defaults to 30.
        bold (boolean): Set bold font

    Returns:
        _type_: _description_
    """
    # Create a draw object
    draw = ImageDraw.Draw(img)

    # Load a font
    base_font = create_font(font_size)
    font = base_font
    if bold:
        bold_font = create_bold_font(font_size)
        font = bold_font

    # Get width and height of text
    w = draw.textlength(text, font=font)

    # Centred x position
    x = (img.width - w) / 2

    draw.text((x, y), text, font=font, fill=fill)

    return img


def extract_colors(img):
    # tolerance = 32
    tolerance = 32
    limit = 5
    colors, pixel_count = extcolors.extract_from_image(img, tolerance, limit)

    return colors


def render_color_platte(colors, size):
    # size = 150
    columns = 6
    width = int(min(len(colors), columns) * size)
    height = int((math.floor(len(colors) / columns) + 1) * size)
    result = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    canvas = ImageDraw.Draw(result)
    for idx, color in enumerate(colors):
        x = int((idx % columns) * size)
        y = int(math.floor(idx / columns) * size)
        # canvas.rectangle([(x, y), (x + size - 1, y + size - 1)], fill=color[0])
        canvas.rectangle([(x, y), (x + size, y + size)], fill=color[0])
    return result


def overlay_palette(img: Image, color_palette: Image, offset):
    # nrow = 2
    # ncol = 1
    # f = plt.figure(figsize=(20, 30), facecolor='None',
    #                edgecolor='k', dpi=55, num=None)
    # gs = gridspec.GridSpec(nrow, ncol, wspace=0.0, hspace=0.0)
    # f.add_subplot(2, 1, 1)
    # plt.imshow(img, interpolation='nearest')
    # plt.axis('off')
    # f.add_subplot(1, 2, 2)
    # plt.imshow(color_palette, interpolation='nearest')
    # plt.axis('off')
    # plt.subplots_adjust(wspace=0, hspace=0, bottom=0)
    # plt.show(block=True)

    img.paste(color_palette, offset)

    return img


def study_image(img, size):
    colors = extract_colors(img)
    color_palette = render_color_platte(colors, size)
    # img = overlay_palette(img, color_palette)
    return color_palette


def create_border(img: Image):
    border_size = get_border_size(img.width, img.height, 32)
    border_bottom_size = get_border_size(img.width, img.height, 6)
    w = img.width + (border_size * 2)
    h = img.height + border_size + border_bottom_size
    canvas = Image.new("RGB", (w, h), (255, 255, 255, 0))
    canvas.paste(img, (border_size, border_size))

    return canvas, border_size, border_bottom_size


def save(path, add_exif, add_palette=True):
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
    # border_size = get_border_size(img.width, img.height)
    # img_with_border = ImageOps.expand(img, border=border_size, fill=colour)
    img_with_border, border_size, border_bottom_size = create_border(img)
    exif = None
    img_margin = round(border_bottom_size / 8 / 2)

    if add_exif:
        exif = get_exif(img)
        if exif:
            heading_font_size = round(border_bottom_size / 8)
            font_size = round(border_bottom_size / 10)
            total_font_height = heading_font_size + \
                (2*img_margin) + (2*font_size)
            # exif_keys = ['Make', 'Model', 'LensMake', 'LensModel', 'FNumber', 'FocalLength', 'ISOSpeedRatings']
            text = f"Shot on {exif.get('Make', '').strip()} {exif.get('Model', '').strip()}".strip(
            )
            y = img_with_border.height - border_bottom_size + \
                (border_bottom_size/2) - (total_font_height / 2)
            img_with_border = write_centred_text_on_image(img_with_border,
                                                          text=text,
                                                          y=y,
                                                          font_size=heading_font_size,
                                                          bold=True,
                                                          fill=(100, 100, 100))
            margin = font_size
            y += font_size + margin
            font_size = round(border_bottom_size / 12)
            text = f"{exif.get('LensModel', '').strip()}".strip()
            # f"{exif.get('LensMake', '').strip()} {exif.get('LensModel', '').strip()}".strip())
            img_with_border = write_centred_text_on_image(img_with_border,
                                                          text=text,
                                                          y=y,
                                                          font_size=font_size,
                                                          fill=(128, 128, 128))
            margin = font_size / 2
            y += font_size + margin
            text = f"{exif.get('FocalLength', '')}mm f/{exif.get('FNumber', '')} ISO{exif.get('ISOSpeedRatings', '')} {decimal_to_fraction(exif.get('ExposureTime', '0'))} sec".strip()
            img_with_border = write_centred_text_on_image(img_with_border,
                                                          text=text,
                                                          y=y,
                                                          font_size=font_size,
                                                          fill=(128, 128, 128))

    if add_palette:
        palette_size = border_bottom_size / 3
        color_palette = study_image(img, palette_size)
        palette_x = img_with_border.width - border_size - color_palette.width
        palette_y = img_with_border.height - \
            round(border_bottom_size / 2) - round(color_palette.height / 2)
        # palette_y = img_with_border.height - border_size + img_margin
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
    img_with_border.save(f'{save_as}.{ext}', subsampling=0, quality=95)


if os.path.isdir(args.filename):
    for file in os.listdir(args.filename):
        print(f'Adding border to {file}')
        save(os.path.join(args.filename, file), args.exif)
else:
    print(f'Adding border to {args.filename}')
    save(args.filename, args.exif)

# from PIL import Image, ImageOps
# for i in list-of-images:
#   img = Image.open(i)
#   img_with_border = ImageOps.expand(img,border=300,fill='black')
#   img_with_border.save('bordered-%s' % i)
