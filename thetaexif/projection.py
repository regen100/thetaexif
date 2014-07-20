import math
import functools
import numpy as np
from PIL import Image
from exif import ExifReader
import tag


def remap(imgarray, coordinates):
    try:
        import cv2
        yy, xx = coordinates
        remapped = cv2.remap(
            imgarray, xx, yy,
            interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
    except ImportError:
        from scipy import ndimage
        remapped = np.empty_like(imgarray)
        for c in xrange(imgarray.shape[2]):
            ndimage.map_coordinates(
                imgarray[..., c], coordinates,
                order=1, mode='wrap', output=remapped[..., c])

    return remapped


def rotation(axis, angle):
    axis = np.array(axis) / math.sqrt(np.dot(axis, axis))
    a = math.cos(angle / 2)
    b, c, d = axis * math.sin(angle / 2)
    return np.array([
        [a * a + b * b - c * c - d * d,
         2 * (b * c - a * d),
         2 * (b * d + a * c)],
        [2 * (b * c + a * d),
         a * a + c * c - b * b - d * d,
         2 * (c * d - a * b)],
        [2 * (b * d - a * c),
         2 * (c * d + a * b),
         a * a + d * d - b * b - c * c]
    ])

rx = functools.partial(rotation, [1, 0, 0])
ry = functools.partial(rotation, [0, 1, 0])
rz = functools.partial(rotation, [0, 0, 1])


def getpose(reader, compass=False):
    zenith = map(float, reader.theta[tag.ZENITH_ES])
    z, x = np.deg2rad(zenith)
    r = rx(x).dot(rz(z))
    if compass:
        y = np.deg2rad(float(reader.theta[tag.COMPASS_ES]))
        r = ry(y).dot(r)
    return r


def rectify(img, compass=False):
    import mapping

    if not isinstance(img, Image.Image):
        img = Image.open(img)

    reader = ExifReader(img)
    r = getpose(reader, compass).T

    imgarray = np.asarray(img)
    h, w = imgarray.shape[:2]

    coord = mapping.getcoordinates(w, h, r)
    rectified = remap(imgarray, coord)
    resultimg = Image.fromarray(rectified)

    reader.theta[tag.ZENITH_ES] = (0, 0)
    if compass:
        reader.theta[tag.COMPASS_ES] = 0
    resultimg.info['exif'] = reader.tobytes()

    return resultimg


class NonJFIFHeaderFile():
    def __init__(self, fp):
        self.fp = fp

    def write(self, b):
        if b[:4] == '\xff\xd8\xff\xe0' and b[20:22] == '\xff\xe1':
            b = b[:2] + b[20:]
        return self.fp.write(b)
