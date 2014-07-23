import os
import argparse
import projection


def rectify(args):
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

        with open(dst, 'wb') as fp:
            fp = projection.NonJFIFHeaderFile(fp)
            rectified.save(fp, 'JPEG', **params)

    return 0


def parse(argv=None):
    parser = argparse.ArgumentParser(description='THETA Image Tool')
    subparsers = parser.add_subparsers(title='subcommands')

    # Rectify
    parser_rectify = subparsers.add_parser('rectify', help='rectify image')
    parser_rectify.set_defaults(func=rectify)
    parser_rectify.add_argument(
        'image', nargs='+', type=argparse.FileType('rb'), help='path to image')
    parser_rectify.add_argument(
        '-c', '--compass', action='store_true', help='use compass')
    parser_rectify.add_argument(
        '-d', '--dir', help='output directory (default: source directory)')
    parser_rectify.add_argument(
        '-e', '--exif', action='store_true', help='write EXIF')

    args = parser.parse_args(argv)
    args.func(args)
