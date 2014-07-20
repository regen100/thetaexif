import os
import unittest
import urllib2
import shutil
from fractions import Fraction
from PIL import Image
from scipy import misc
import thetaexif


class TestExif(unittest.TestCase):
    def setUp(self):
        url = ('https://theta360.s3.amazonaws.com'
               '/d32805ec-c37d-11e3-ac04-52540092ec69-1/equirectangular')
        self.image = 'var/test.jpg'

        if not os.path.exists(self.image):
            dir = os.path.dirname(self.image)
            if not os.path.exists(dir):
                os.makedirs(dir)
            req = urllib2.urlopen(url)
            with open(self.image, 'wb') as fp:
                shutil.copyfileobj(req, fp)

        self.lena = Image.fromarray(misc.lena())

    def test_tagreader(self):
        # No EXIF image test
        img = self.lena
        self.assertRaises(ValueError, thetaexif.TagReader.load, img)

        # TagReader.load() test (str)
        img = self.image
        reader = thetaexif.TagReader.load(img)
        self.assertIsInstance(reader, thetaexif.TagReader)

        # TagReader.load() test (file object)
        img = open(self.image, 'rb')
        reader = thetaexif.TagReader.load(img)
        self.assertIsInstance(reader, thetaexif.TagReader)

        # TagReader.load() test (PIL)
        img = Image.open(self.image)
        reader = thetaexif.TagReader.load(img)
        self.assertIsInstance(reader, thetaexif.TagReader)

        # THETA IFD test
        self.assertIn(thetaexif.tag.THETA_SUBDIR, reader)
        subdir = reader[thetaexif.tag.THETA_SUBDIR]
        self.assertIsInstance(subdir, thetaexif.TagReader)

        # Sensor test
        self.assertIn(thetaexif.tag.ZENITH_ES, subdir)
        self.assertEqual(subdir[thetaexif.tag.ZENITH_ES], (Fraction(200, 10),
                                                           Fraction(-240, 10)))

        self.assertIn(thetaexif.tag.COMPASS_ES, subdir)
        self.assertEqual(subdir[thetaexif.tag.COMPASS_ES], Fraction(225, 10))

        # tobytes()
        self.assertEqual(reader.tobytes(), img.info['exif'])

        # write to exif
        comapss = Fraction(1, 10)
        subdir[thetaexif.tag.COMPASS_ES] = comapss
        self.assertEqual(subdir[thetaexif.tag.COMPASS_ES], comapss)
