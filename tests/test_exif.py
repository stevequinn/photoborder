from exif import ExifItem

def test_ExifItem():
    itm = ExifItem('FocalLength', '23  ')
    assert str(itm) == '23mm'
    itm = ExifItem('UnknownItem', ' Bleh  ')
    assert str(itm) == 'Bleh'
