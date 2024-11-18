"""
Text on image functions
"""
import os
from typing import List, TypeVar
from PIL import Image, ImageDraw, ImageFont

T = TypeVar('T')

def load_font_variants(fontpath: str) -> List[T]:
    """Try loading the different font variant indices.

    Args:
        fontpath (str): Path to the font file

    Returns:
        [(index, {'family': str, 'style': str})]: A list containing the available font variants
    """
    variants = []
    index = 0

    while True:
        try:
            font = ImageFont.truetype(fontpath, size=12, index=index)
            info = {
                'family': font.getname()[0],
                'style': font.getname()[1]
            }
            variants.append((index, info))
            index += 1
        except Exception:
            break

    return variants

def validate_font(fontpath: str, index: int) -> bool:
    """Validate if the font exists and contains a variant index

    Args:
        fontpath (str): Path to the font file
        index (int): The font variant index.

    Returns:
        str: None if font exists, otherwise an error message.
    """
    if not os.path.isfile(fontpath):
        return f'Font {fontpath} does not exist.'

    font_variants = load_font_variants(fontpath)
    if not any(variant[0] == index for variant in font_variants):
        return f'Font {fontpath} does not contain a variant with index: {index}. Available variants: {font_variants}'

    return None

def create_font(size: int, fontpath: str, index: int = 0) -> ImageFont.FreeTypeFont:
    """Create the font object

    Args:
        size (int): Pixel size
        fontpath (str): Path to the font file
        index (int): The font variant index. Defaults to 0.

    Returns:
        ImageFont.FreeTypeFont: The created font
    """
    font = ImageFont.truetype(fontpath, size, index)
    return font

def draw_text_on_image(img: Image, text: str, xy: tuple, centered: bool,
                       font: ImageFont.FreeTypeFont, fill: tuple = (100, 100, 100)) -> Image:
    """Draw text on an image

    Args:
        img (Image): The image to draw on
        text (str): The text to draw
        xy (tuple): The xy position of the starting point
        centered (bool): Center the text relative to the entire image
        font (ImageFont.FreeTypeFont): The font to use. See create_font and create_bold_font.
        fill (tuple, optional): The font color. Defaults to black (100, 100, 100).

    Returns:
        Image: The image with the text drawn on it.
        xy (tuple): The xy position of the next drawing pos
    """
    # Create a draw object.
    # TODO: Creating this every time we want to draw a line is inefficient. Look into other options.
    draw = ImageDraw.Draw(img)

    # Enable antialiasing
    draw.fontmode = 'L'

    x, y = xy

    # Get the width of the text line so we can return the finish x pos
    w = draw.textlength(text, font=font)

    if centered:
        # Center the starting x pos
        x = (img.width - w) / 2

    # Draw the actual text on the image.
    draw.text((x, y), text, font=font, fill=fill, anchor="ls")

    # Figure out next x, y positions
    next_y = y + font.size + (font.size / 2) if centered else y
    next_x = x if centered else x + w + (font.size / 2)

    return img, (next_x, next_y)

def get_optimal_font_size(text, target_height, fontpath, index, max_font_size=100, min_font_size=1):
    """
    Calculate the optimal font size based on a target height

    Args:
        text (str): Sample text to draw
        target_height (int): The target height
        fontpath: (str): The path of the font to determine the size for.
        index (int): The font variant index.
        max_font_size (int, optional): Max font size to return. Defaults to 100.
        min_font_size (int, optional): Min font size to return. Defaults to 1.
    """
    def check_size(font_size):
        font = ImageFont.truetype(fontpath, font_size, index)
        font.size = font_size
        _, _, _, text_height = font.getbbox(text)
        return text_height <= target_height

    # Binary search for the optimal font size
    low, high = min_font_size, max_font_size
    while low <= high:
        mid = (low + high) // 2
        if check_size(mid):
            low = mid + 1
        else:
            high = mid - 1

    return high # The largest font size that fits
