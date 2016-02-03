"""ImageKit processors"""

from imagekit.processors import ResizeToFill
from PIL import ExifTags


class RotateImageByExif(object):
    """Set correct image rotation based on the image's EXIF metadata"""

    def process(self, img):
        Orientation = 274
        assert ExifTags.TAGS[Orientation] == "Orientation"
        exif = img._getexif() or {}
        orientation = exif.get(Orientation, 0)
        if orientation == 3:
            return img.rotate(180, expand=True)
        elif orientation == 6:
            return img.rotate(270, expand=True)
        elif orientation == 8:
            return img.rotate(90, expand=True)
        else:
            return img


class RotateAndScale(object):
    """Does the equivalent of rotateAndScaleFile from fileupload.js"""

    def __init__(self, max_width, max_height):
        self.max_width = max_width
        self.max_height = max_height

    def process(self, img):
        subprocessors = [
            RotateImageByExif(),
            ResizeToFill(width=self.max_width, height=self.max_height, upscale=False),
        ]
        for sp in subprocessors:
            img = sp.process(img)
        return img
