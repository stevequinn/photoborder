import os
import pytest
from PIL import ImageFont
from text import create_font, load_font_variants



def test_font_index():
    fontname = 'Roboto-Regular.ttf'
    moduledir = os.path.dirname(os.path.abspath(__file__))
    fontdir = os.path.join(moduledir, "../fonts")
    font_path = os.path.join(fontdir, fontname)
    index = 20
    variants = []

    try:
        font = create_font(size=12, fontpath=font_path, index=index)
    except Exception:
        variants = load_font_variants(fontpath=font_path)
        print(f'Error loading {fontname} font variant {index}. Available variants: {variants}')
        assert len(variants) is not 0

    for variant in variants:
        try:
            font = create_font(size=12, fontpath=font_path, index=variant[0])
            print(f'{variant[1]} loaded')
        except Exception as exc:
            pytest.fail(f'Unexpected eception raised: {exc}')


