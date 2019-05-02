import argparse
import os

from . import projection, tag
from .exif import ExifReader, TagReader


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

        src.close()

    return 0


def info(args):
    def formatter(reader, tags):
        for k, v in reader.items():
            if isinstance(v, TagReader):
                continue
            line = '0x{:04x}'.format(k)
            if k in tags:
                line += ' [{}]'.format(tags[k])
            if isinstance(v, tuple):
                v = '(' + ', '.join(map(str, v)) + ')'
            elif isinstance(v, bytes):
                try:
                    v = v.decode('ascii')
                except UnicodeDecodeError:
                    pass
            line += ': {}'.format(v)
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


def parse(argv=None):
    parser = argparse.ArgumentParser(description='THETA Image Tool')
    subparsers = parser.add_subparsers()
    subparsers.required = True
    subparsers.dest = 'command'

    # Rectify
    parser_rectify = subparsers.add_parser('rectify', help='rectify image')
    parser_rectify.set_defaults(func=rectify)
    parser_rectify.add_argument('image',
                                nargs='+',
                                type=argparse.FileType('rb'),
                                help='path to image')
    parser_rectify.add_argument('-c',
                                '--compass',
                                action='store_true',
                                help='use compass')
    parser_rectify.add_argument(
        '-d', '--dir', help='output directory (default: source directory)')
    parser_rectify.add_argument('-e',
                                '--exif',
                                action='store_true',
                                help='write EXIF')

    # Info
    parser_info = subparsers.add_parser('info',
                                        description='display THETA EXIF tag')
    parser_info.set_defaults(func=info)
    parser_info.add_argument('image',
                             type=argparse.FileType('rb'),
                             help='path to image')

    args = parser.parse_args(argv)
    return args.func(args)
