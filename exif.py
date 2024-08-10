"""
Photo Exif extraction functions
"""
from PIL import Image
from PIL.ExifTags import TAGS


def get_exif(img: Image) -> dict:
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
