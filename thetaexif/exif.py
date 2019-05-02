# References:
# - http://xanxys.hatenablog.jp/entry/20131110/1384094832
# - http://www.ozhiker.com/electronics/pjmt/jpeg_info/ricoh_mn.html
# - http://www.sno.phy.queensu.ca/~phil/exiftool/TagNames/Ricoh.html
# - https://github.com/atotto/ricoh-theta-tools

import collections
import fractions
import io
import struct

from PIL import Image

from . import tag


class Handler(object):
    TABLE = {
        1: 'B',
        2: 'c',
        3: 'H',
        4: 'I',
        5: 'II',
        6: 'b',
        7: 'c',
        8: 'h',
        9: 'i',
        10: 'ii',
        11: 'f',
        12: 'd',
    }

    def __init__(self, typeid, formatter):
        self.typeid = typeid
        self.formatter = formatter

    @property
    def size(self):
        return self.formatter.size

    def read(self, fp):
        unpacked = self.formatter.unpack(fp.read(self.size))
        if len(unpacked) == 1:
            return unpacked[0]
        else:
            return fractions.Fraction(unpacked[0], unpacked[1])

    def write(self, fp, value):
        if self.typeid in (5, 10):
            value = fractions.Fraction(value)
            packed = self.formatter.pack(value.numerator, value.denominator)
        else:
            packed = self.formatter.pack(value)
        fp.write(packed)

    @classmethod
    def build_handler(cls, endian=''):
        handlers = {}
        for typeid, fmt in cls.TABLE.items():
            formatter = struct.Struct(endian + fmt)
            handlers[typeid] = cls(typeid, formatter)
        return handlers


Handler.lehandlers = Handler.build_handler('<')
Handler.behandlers = Handler.build_handler('>')


class TIFFHeader(object):
    def __init__(self, fp):
        self.endian = fp.read(2)
        if self.endian not in (b'II', b'MM'):
            raise ValueError('endian must be II or MM: {}'.format(self.endian))
        tiff_code = self.u16(fp)
        if tiff_code != 0x002A:
            raise ValueError('Invalid TIFF header.')
        self.zeroth_ifd_offset = self.u32(fp)
        fp.seek(self.zeroth_ifd_offset)

    @property
    def handlers(self):
        if self.endian == b'II':
            return Handler.lehandlers
        elif self.endian == b'MM':
            return Handler.behandlers

    @property
    def u16(self):
        return self.handlers[3].read

    @property
    def u32(self):
        return self.handlers[4].read


class TagReader(collections.MutableMapping):
    '''
    IFD reader class.
    '''
    SUBDIR_HEADER = {
        tag.EXIF_IFD_POINTER: 0,
        tag.GPS_INFO_IFD_POINTER: 0,
        tag.RICOH_SUBDIR: 20,
        tag.THETA_SUBDIR: 0
    }

    def __init__(self, fp, header=None):
        self.fp = fp
        self.tags = {}
        self.data = {}
        if header is None:
            self.header = TIFFHeader(fp)
        else:
            self.header = header

        for i in range(header.u16(fp)):
            tagid = header.u16(fp)
            tagtype = header.u16(fp)
            if tagid == 0 and tagtype == 0:
                continue
            try:
                handler = header.handlers[tagtype]
            except KeyError:
                raise ValueError('Invalid data type.')
            num = header.u32(fp)
            if handler.size * num > 4:
                offset = header.u32(fp)
            else:
                offset = fp.tell()
                fp.seek(4, io.SEEK_CUR)

            self.tags[tagid] = (handler, num, offset)

        self.nextifd_offset = header.u32(fp)

    def __str__(self):
        return str(self.asdict())

    def __getitem__(self, key):
        try:
            return self.data[key]
        except KeyError:
            handler, num, offset = self.tags[key]
            self.fp.seek(offset)
            value = tuple(handler.read(self.fp) for _ in range(num))
            if handler.typeid == 2:
                value = b''.join(value[:-1])
            elif handler.typeid == 7:
                value = b''.join(value)
            elif len(value) == 1:
                value = value[0]

            if key in self.SUBDIR_HEADER:
                self.fp.seek(value + self.SUBDIR_HEADER[key])
                self.data[key] = TagReader(self.fp, self.header)
            else:
                self.data[key] = value
            return self.data[key]

    def __setitem__(self, key, values):
        handler, num, offset = self.tags[key]
        if not isinstance(values, collections.abc.Sized):
            values = (values, )
        if num != len(values):
            raise ValueError('Invalid length of values.')

        self.fp.seek(offset)
        for value in values:
            handler.write(self.fp, value)

        if key in self.data:
            del self.data[key]

    def __delitem__(self, key):
        raise NotImplementedError

    def __iter__(self):
        return iter(self.tags)

    def __len__(self):
        return len(self.tags)

    def getoffset(self, key):
        handler, num, offset = self.tags[key]
        return offset

    def asdict(self):
        '''
        Convert to dictionary recursively.
        '''
        return self._dict(self)

    def _dict(self, obj):
        d = {}
        for k, v in obj.items():
            if isinstance(v, self.__class__):
                d[k] = self._dict(v)
            else:
                d[k] = v
        return d


class ExifReader(object):
    """EXIF reader class for THETA image."""

    EXIF_ID_CODE = b'Exif\x00\x00'
    RICOH_MAKERNOTE_CODE = b'Ricoh\x00\x00\x00'

    def __init__(self, img):
        if not isinstance(img, Image.Image):
            img = Image.open(img)
        if 'exif' not in img.info:
            raise ValueError('No EXIF.')

        self.img = img
        body = img.info['exif'][len(ExifReader.EXIF_ID_CODE):]
        self.fp = io.BytesIO(body)
        header = TIFFHeader(self.fp)

        self.ifdlist = []
        while True:
            ifd = TagReader(self.fp, header)
            self.ifdlist.append(ifd)
            if ifd.nextifd_offset:
                self.fp.seek(ifd.nextifd_offset)
            else:
                break

        self._makernote = None

    @property
    def exif(self):
        return self.ifdlist[0][tag.EXIF_IFD_POINTER]

    @property
    def gps(self):
        return self.ifdlist[0][tag.GPS_INFO_IFD_POINTER]

    @property
    def makernote(self):
        if not self._makernote:
            if tag.MAKER_NOTE not in self.exif:
                raise ValueError('No MakerNote.')

            self.fp.seek(self.exif.getoffset(tag.MAKER_NOTE))
            code_len = len(ExifReader.RICOH_MAKERNOTE_CODE)
            if self.fp.read(code_len) != self.RICOH_MAKERNOTE_CODE:
                raise ValueError('No RICOH maker note.')

            self._makernote = TagReader(self.fp, self.exif.header)
        return self._makernote

    @property
    def theta(self):
        if tag.THETA_SUBDIR not in self.makernote:
            raise ValueError('No THETA subdir.')
        return self.makernote[tag.THETA_SUBDIR]

    @property
    def thumbnail(self):
        offset = self.ifdlist[1][tag.JPEG_INTERCHANGE_FORMAT]
        length = self.ifdlist[1][tag.JPEG_INTERCHANGE_FORMAT_LENGTH]
        self.fp.seek(offset)
        fp = io.BytesIO(self.fp.read(length))
        return Image.open(fp)

    @thumbnail.setter
    def thumbnail(self, img):
        offset = self.ifdlist[1][tag.JPEG_INTERCHANGE_FORMAT]
        self.fp.seek(offset)
        img.save(self.fp, 'JPEG')
        end = self.fp.tell()
        self.fp.truncate()
        self.ifdlist[1][tag.JPEG_INTERCHANGE_FORMAT_LENGTH] = end - offset

    def tobytes(self):
        self.fp.seek(0)
        return self.EXIF_ID_CODE + self.fp.read()
