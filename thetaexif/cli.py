import os
import argparse
from PIL import Image
import projection


def rectify(argv=None):
    parser = argparse.ArgumentParser(description='Rectify THETA image')
    parser.add_argument(
        'image', nargs='+', type=argparse.FileType('rb'), help='path to image')
    parser.add_argument(
        '-c', '--compass', action='store_true', help='use compass')
    parser.add_argument(
        '-d', '--dir', help='output directory (default: source directory)')
    args = parser.parse_args(argv)

    if args.dir and not os.path.exists(args.dir):
        os.makedirs(args.dir)

    for src in args.image:
        if args.dir:
            dst = os.path.join(args.dir, os.path.basename(src.name))
        else:
            base, ext = os.path.splitext(src.name)
            dst = base + '_rectified' + ext

        rectified = projection.rectify(src, args.compass)
        Image.fromarray(rectified).save(dst)

    return 0
