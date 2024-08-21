"""
Image colour palette functions
"""
import math
import extcolors
from PIL import Image, ImageDraw

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


def load_image_color_palette(img, size):
    colors = extract_colors(img)
    color_palette = render_color_platte(colors, size)
    # img = overlay_palette(img, color_palette)
    return color_palette
