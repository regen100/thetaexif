import sys
import argparse
from exif import ExifReader, TagReader
import tag


def main(argv=None):
    parser = argparse.ArgumentParser(
        'thetaexif',
        description='Read THETA EXIF tag and display')
    parser.add_argument(
        'image', type=argparse.FileType('rb'), help='path to image')
    args = parser.parse_args()

    def formatter(tag, val):
        if isinstance(val, tuple):
            val = '(' + ', '.join(map(str, val)) + ')'
        return '{}: {}'.format(tag, val)

    try:
        reader = ExifReader(args.image)
        for k, v in reader.makernote.iteritems():
            if not isinstance(v, TagReader):
                print formatter(tag.MARKERNOTE_TAGS.get(k, k), v)
        for k, v in reader.theta.iteritems():
            print formatter(tag.THETASUBDIR_TGAS.get(k, k), v)
    except (IndexError, ValueError):
        print 'Error: %s does not have THETA EXIF tag' % args.image.name
        return 1

    return 0

if __name__ == '__main__':
    sys.exit(main())
