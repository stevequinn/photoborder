import os
from pathlib import Path

def get_image_files(directory):
    # List of common image file extensions
    # image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
    image_extensions = ['.jpg', '.jpeg']

    # Use a list comprehension to get all image files
    image_files = [
        file for file in os.listdir(directory)
        if Path(file).suffix.lower() in image_extensions and '_border' not in str(file).lower()
    ]

    return image_files

def test_run():
    images = get_image_files('./tests/images')
    for img in images:
        os.system(f'python border.py {img} -e -p')

if __name__ == "__main__":
    test_run()
