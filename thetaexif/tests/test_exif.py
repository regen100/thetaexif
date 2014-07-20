import os
import unittest
import urllib2
import shutil
from fractions import Fraction
from PIL import Image
from scipy import misc
from thetaexif import tag
from thetaexif.exif import ExifReader, TagReader


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

    def test_exifreader_load(self):
        # No EXIF image test
        img = self.lena
        self.assertRaises(ValueError, ExifReader, img)

        # ExifReader() test (str)
        img = self.image
        ExifReader(img)

        # ExifReader() test (file object)
        img = open(self.image, 'rb')
        ExifReader(img)

        # ExifReader() test (PIL)
        img = Image.open(self.image)
        ExifReader(img)

    def test_exifreader_read(self):
        reader = ExifReader(self.image)

        self.assertEqual(len(reader.ifdlist), 2)

        self.assertIsInstance(reader.exif, TagReader)
        self.assertIsInstance(reader.makernote, TagReader)
        self.assertIsInstance(reader.theta, TagReader)

        self.assertIn(tag.ZENITH_ES, reader.theta)
        self.assertEqual(reader.theta[tag.ZENITH_ES], (Fraction(200, 10),
                                                       Fraction(-240, 10)))
        self.assertIn(tag.COMPASS_ES, reader.theta)
        self.assertEqual(reader.theta[tag.COMPASS_ES], Fraction(225, 10))

    def test_exifreader_tobytes(self):
        reader = ExifReader(self.image)

        self.assertEqual(reader.tobytes(), reader.img.info['exif'])

    def test_exifreader_write(self):
        reader = ExifReader(self.image)

        comapss = Fraction(1, 10)
        reader.theta[tag.COMPASS_ES] = comapss
        self.assertEqual(reader.theta[tag.COMPASS_ES], comapss)

        comapss = 0.5
        reader.theta[tag.COMPASS_ES] = comapss
        self.assertEqual(reader.theta[tag.COMPASS_ES], comapss)

        self.assertNotEqual(reader.tobytes(), reader.img.info['exif'])

if __name__ == '__main__':
    unittest.main()
