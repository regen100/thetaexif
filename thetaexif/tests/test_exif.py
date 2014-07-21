import unittest
from fractions import Fraction
from PIL import Image
from scipy import misc
from thetaexif import tag
from thetaexif.exif import ExifReader, TagReader
import testdata


class TestExif(unittest.TestCase):
    def setUp(self):
        self.image = testdata.prepare_image()
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
        self.assertEqual(reader.theta[tag.ZENITH_ES], testdata.ZENITH_ES)
        self.assertIn(tag.COMPASS_ES, reader.theta)
        self.assertEqual(reader.theta[tag.COMPASS_ES], testdata.COMPASS_ES)
        self.assertEqual(reader.gps[tag.GPS_IMG_DIRECTION],
                         testdata.COMPASS_ES)

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
