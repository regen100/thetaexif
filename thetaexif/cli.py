import os
import argparse
import projection


def rectify(argv=None):
    parser = argparse.ArgumentParser(description='Rectify THETA image')
    parser.add_argument(
        'image', nargs='+', type=argparse.FileType('rb'), help='path to image')
    parser.add_argument(
        '-c', '--compass', action='store_true', help='use compass')
    parser.add_argument(
        '-d', '--dir', help='output directory (default: source directory)')
    parser.add_argument(
        '-e', '--exif', action='store_true', help='write EXIF')
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

        params = {}
        if args.exif:
            params['exif'] = rectified.info['exif']

        rectified.save(dst, **params)

    return 0
