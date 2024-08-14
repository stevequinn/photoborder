"""
Photo Exif extraction functions
"""
from dataclasses import dataclass
from fractions import Fraction
from PIL import Image
from PIL.ExifTags import TAGS

def decimal_to_fraction(decimal):
    """
    Convert a decimal value to a fraction display.
    Used to display shutter speed values.
    """
    if not decimal:
        return ''

    result = str(Fraction(decimal))

    return result

@dataclass
class ExifItem:
    tag: str
    data: str

    formatter = {
        'Make': 'Shot on {dataval}',
        'FocalLength': '{dataval}mm',
        'FNumber': 'f/{dataval}',
        'ISOSpeedRatings': 'ISO{dataval}',
        'ExposureTime': '{dataval} sec'
    }

    def __str__(self) -> str:
        if self.data is None or self.data == '':
            return ''
        fmt_data = str(self.data).strip()
        if self.tag == 'ExposureTime':
           fmt_data = decimal_to_fraction(fmt_data)
        if self.tag in self.formatter:
            return self.formatter[self.tag].format(dataval=fmt_data)

        return fmt_data


def get_exif(img: Image) -> dict:
    """Load the exif data from an image.

    Args:
        img (Image): Pillow image object.

    Returns:
        dict: dictionary with exif data
    """
    exif_data = img._getexif()
    exif_dict = {
        'Make': '',
        'Model': '',
        'LensMake': '',
        'LensModel': '',
        'FNumber': '',
        'FocalLength': '',
        'ISOSpeedRatings': ''
    }

    if exif_data:
        # Iterate through the EXIF data and store it in the dictionary
        for tag_id in exif_data:
            tag = TAGS.get(tag_id, tag_id)
            data = exif_data.get(tag_id)
            if isinstance(data, bytes):
                data = data.decode()
            exif_dict[tag] = ExifItem(tag, data)

    # Print the EXIF data dictionary
    # print(exif_dict)

    return exif_dict
