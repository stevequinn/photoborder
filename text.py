"""
Text on image functions
"""
from PIL import Image, ImageDraw, ImageFont

MAINFONT = "Avenir.ttc"


def create_font(size: int, fontname=MAINFONT) -> ImageFont.FreeTypeFont:
    """Create the font object

    Args:
        size (int): Pixel size

    Returns:
        ImageFont.FreeTypeFont: The created font
    """
    font = ImageFont.truetype(fontname, size)
    return font


def create_bold_font(size: int, fontname=MAINFONT) -> ImageFont.FreeTypeFont:
    """Create the bold font object

    Args:
        size (int): Pixel size

    Returns:
        ImageFont.FreeTypeFont: The created font
    """
    font = ImageFont.truetype(fontname, size, index=8)
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
        fill (tuple, optional): The font colour. Defaults to black (100, 100, 100).

    Returns:
        Image: The image with the text drawn on it.
    """
    # Create a draw object.
    # TODO: Creating this every time we want to draw a line is inefficient. Look into other options.
    draw = ImageDraw.Draw(img)

    x, y = xy

    if centered:
         # Get width and height of text
        w = draw.textlength(text, font=font)
        x = (img.width - w) / 2

    # Draw the actual text on the image.
    draw.text((x, y), text, font=font, fill=fill)

    # Figure out next y position
    next_y = y + font.size + (font.size / 2)

    return img, next_y

