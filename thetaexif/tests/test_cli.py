import os
import unittest

from thetaexif import ExifReader, tag
from thetaexif.cli import parse

from . import testdata


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.image = testdata.prepare_image()
        self.rectified = os.path.splitext(self.image)[0] + '_rectified.jpg'

    def test_rectify(self):
        parse(['rectify', self.image])
        self.assertTrue(os.path.exists(self.rectified))
        self.assertRaises(ValueError, ExifReader, self.rectified)
        os.unlink(self.rectified)

        # write EXIF
        parse(['rectify', self.image, '-e'])
        self.assertTrue(os.path.exists(self.rectified))
        reader = ExifReader(self.rectified)
        self.assertEqual(reader.theta[tag.ZENITH_ES], (0, 0))
        self.assertEqual(reader.theta[tag.COMPASS_ES], testdata.COMPASS_ES)
        self.assertEqual(reader.gps[tag.GPS_IMG_DIRECTION],
                         testdata.COMPASS_ES)
        reader.img.fp.close()
        os.unlink(self.rectified)

        # write EXIF (using compass)
        parse(['rectify', self.image, '-e', '-c'])
        self.assertTrue(os.path.exists(self.rectified))
        reader = ExifReader(self.rectified)
        self.assertEqual(reader.theta[tag.ZENITH_ES], (0, 0))
        self.assertEqual(reader.theta[tag.COMPASS_ES], 0)
        self.assertEqual(reader.gps[tag.GPS_IMG_DIRECTION], 0)
        reader.img.fp.close()
        os.unlink(self.rectified)


if __name__ == '__main__':
    unittest.main()
