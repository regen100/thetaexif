import argparse
import sys

from . import tag
from .exif import ExifReader, TagReader


def main(argv=None):
    parser = argparse.ArgumentParser(
        'thetaexif', description='Read THETA EXIF tag and display')
    parser.add_argument('image',
                        type=argparse.FileType('rb'),
                        help='path to image')
    args = parser.parse_args()

    def formatter(reader, tags):
        for k, v in reader.items():
            if isinstance(v, TagReader):
                continue
            line = '0x%04x' % k
            if k in tags:
                line += ' [%s]' % tags[k]
            if isinstance(v, tuple):
                v = '(' + ', '.join(map(str, v)) + ')'
            line += ': %s' % v
            print(line)

    try:
        reader = ExifReader(args.image)
        makernote = reader.makernote
        theta = reader.theta
    except ValueError as e:
        print('Error:', e)
        return 1

    print('RICOH Marker Note')
    formatter(makernote, tag.MARKERNOTE_TAGS)
    print()
    print('THETA Subdir')
    formatter(theta, tag.THETASUBDIR_TGAS)

    return 0


if __name__ == '__main__':
    sys.exit(main())
