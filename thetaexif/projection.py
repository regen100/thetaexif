import functools

import numpy as np
from PIL import Image

from . import tag
from .exif import ExifReader


def getcoordinates(w, h, r):
    uu, vv = np.meshgrid(np.arange(w), np.arange(h))
    t = (uu - w / 2) * 2 * np.pi / w
    p = (vv - h / 2) * np.pi / h
    st, ct = np.sin(t), np.cos(t)
    sp, cp = np.sin(p), np.cos(p)
    xyz = np.dstack((cp * st, sp, cp * ct))
    xyz = np.einsum('ij,...j', r, xyz)
    t = np.arctan2(xyz[:, :, 0], xyz[:, :, 2])
    p = np.arcsin(xyz[:, :, 1])
    uu = t * w / 2 / np.pi + w / 2
    vv = p * h / np.pi + h / 2
    return np.dstack((vv, uu)).transpose(2, 0, 1)


def remap(imgarray, coordinates):
    from scipy import ndimage
    remapped = np.empty_like(imgarray)
    for c in range(imgarray.shape[2]):
        ndimage.map_coordinates(imgarray[..., c],
                                coordinates,
                                order=1,
                                mode='wrap',
                                output=remapped[..., c])

    return remapped


def rotation(axis, angle):
    axis = np.array(axis) / np.sqrt(np.dot(axis, axis))
    a = np.cos(angle / 2)
    b, c, d = axis * np.sin(angle / 2)
    return np.array([[
        a * a + b * b - c * c - d * d, 2 * (b * c - a * d), 2 * (b * d + a * c)
    ], [
        2 * (b * c + a * d), a * a + c * c - b * b - d * d, 2 * (c * d - a * b)
    ], [
        2 * (b * d - a * c), 2 * (c * d + a * b), a * a + d * d - b * b - c * c
    ]])


rx = functools.partial(rotation, [1, 0, 0])
ry = functools.partial(rotation, [0, 1, 0])
rz = functools.partial(rotation, [0, 0, 1])


def getpose(reader, compass=False):
    zenith = tuple(map(float, reader.theta[tag.ZENITH_ES]))
    z, x = np.deg2rad(zenith)
    r = rx(x).dot(rz(z))
    if compass:
        y = np.deg2rad(float(reader.theta[tag.COMPASS_ES]))
        r = ry(y).dot(r)
    return r


def rectify(img, compass=False):
    if not isinstance(img, Image.Image):
        img = Image.open(img)

    reader = ExifReader(img)
    r = getpose(reader, compass).T

    imgarray = np.asarray(img)
    h, w = imgarray.shape[:2]

    coord = getcoordinates(w, h, r)
    rectified = remap(imgarray, coord)
    resultimg = Image.fromarray(rectified)

    # Rewrite gyroscope and compass data
    reader.theta[tag.ZENITH_ES] = (0, 0)
    if compass:
        reader.theta[tag.COMPASS_ES] = 0
        reader.gps[tag.GPS_IMG_DIRECTION] = 0

    # Rewrite thumbnail
    size = reader.thumbnail.size
    reader.thumbnail = resultimg.resize(size, Image.ANTIALIAS)

    resultimg.info['exif'] = reader.tobytes()

    return resultimg


class NonJFIFHeaderFile():
    def __init__(self, fp):
        self.fp = fp

    def write(self, b):
        if b[:4] == b'\xff\xd8\xff\xe0' and b[20:22] == b'\xff\xe1':
            b = b[:2] + b[20:]
        return self.fp.write(b)
