import os
import shutil
import urllib.request
from fractions import Fraction

URL = ('https://theta360.s3.amazonaws.com'
       '/d32805ec-c37d-11e3-ac04-52540092ec69-1/equirectangular')
ZENITH_ES = Fraction(200, 10), Fraction(-240, 10)
COMPASS_ES = Fraction(225, 10)


def prepare_image():
    image = 'var/test.jpg'

    if not os.path.exists(image):
        dir = os.path.dirname(image)
        if not os.path.exists(dir):
            os.makedirs(dir)
        req = urllib.request.urlopen(URL)
        with open(image, 'wb') as fp:
            shutil.copyfileobj(req, fp)

    return image
