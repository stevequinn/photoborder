"""
Photo Exif extraction functions
"""
from dataclasses import dataclass
from fractions import Fraction
from PIL import Image
from PIL.ExifTags import TAGS

def format_shutter_speed(shutter_speed: str) -> str:
    """
    Convert a decimal value to a fraction display.
    Used to display shutter speed values.
    """
    try:
        fraction = Fraction(shutter_speed).limit_denominator()
        if fraction >= 1:
            # return f"{fraction.numerator}/{fraction.denominator}"
            return f"{fraction.numerator}"
        else:
            return f"1/{int(1/float(shutter_speed))}"
    except (ValueError, ZeroDivisionError):
        return shutter_speed

def format_focal_length(focal_length: str) -> str:
    """
    Round Focal Length
    """
    try:
        return round(float(focal_length), 2)
    except ValueError:
        return focal_length

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

        # Deal with any special case data formatting
        if self.tag == 'ExposureTime':
           fmt_data = format_shutter_speed(fmt_data)
        
        # Deal with any special case data formatting
        if self.tag == 'FocalLength':
           fmt_data = format_focal_length(fmt_data)

        # Apply the string template formatting defined in self.formatter
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
        'ISOSpeedRatings': '',
        'ExposureTime': ''
    }

    if exif_data:
        # Iterate through the EXIF data and store it in the dictionary
        for tag_id in exif_data:
            tag = TAGS.get(tag_id, tag_id)
            data = exif_data.get(tag_id)

            if isinstance(data, bytes):
                try:
                    data = data.decode()
                except UnicodeDecodeError as e:
                    # print(f'Error decoding tag {tag}', e)
                    # Expect decoding errors, ust ignore as we don't need the exif these happen on.
                    pass

            exif_dict[tag] = ExifItem(tag, data)

    # Print the EXIF data dictionary
    # print(exif_dict)

    return exif_dict
