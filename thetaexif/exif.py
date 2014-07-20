# References:
# - http://xanxys.hatenablog.jp/entry/20131110/1384094832
# - http://www.ozhiker.com/electronics/pjmt/jpeg_info/ricoh_mn.html
# - http://www.sno.phy.queensu.ca/~phil/exiftool/TagNames/Ricoh.html
# - https://github.com/atotto/ricoh-theta-tools

import io
import collections
import struct
import fractions
from PIL import Image
import tag

table = {
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


def build_handler(endian=''):
    handlers = {}
    for typeid, fmt in table.iteritems():
        st = struct.Struct(endian + fmt)

        def handler(fp, st=st):
            unpacked = st.unpack(fp.read(st.size))
            if len(unpacked) == 1:
                return unpacked[0]
            else:
                return fractions.Fraction(unpacked[0], unpacked[1])
        handler.size = st.size
        handler.typeid = typeid
        handlers[typeid] = handler
    return handlers

lehandlers = build_handler('<')
behandlers = build_handler('>')


class TIFFHeader(object):
    def __init__(self, fp):
        self.endian = fp.read(2)
        if self.endian not in ('II', 'MM'):
            raise ValueError('endian must be II or MM.')
        tiff_code = self.u16(fp)
        if tiff_code != 0x002A:
            raise ValueError('Invalid TIFF header.')
        self.zeroth_ifd_offset = self.u32(fp)
        fp.seek(self.zeroth_ifd_offset)

    @property
    def handlers(self):
        if self.endian == 'II':
            return lehandlers
        elif self.endian == 'MM':
            return behandlers

    @property
    def u16(self):
        return self.handlers[3]

    @property
    def u32(self):
        return self.handlers[4]


class TagReader(collections.Mapping):
    '''
    EXIF tag reader class for THETA image.
    '''
    EXIF_ID_CODE = 'Exif\x00\x00'
    RICOH_MAKERNOTE_CODE = 'Ricoh\x00\x00\x00'
    SUBDIR_HEADER = {
        tag.EXIF_IFD_POINTER: 0,
        tag.RICOH_SUBDIR: 20,
        tag.THETA_SUBDIR: 0
    }

    def __init__(self, fp, header):
        self.fp = fp
        self.header = header
        self.tags = {}
        self.data = {}

        for i in xrange(header.u16(fp)):
            tagid = header.u16(fp)
            tagtype = header.u16(fp)
            try:
                handler = header.handlers[tagtype]
            except IndexError:
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
            value = tuple(handler(self.fp) for _ in xrange(num))
            if handler.typeid == 2:
                value = ''.join(value[:-1])
            elif handler.typeid == 7:
                value = ''.join(value)
            elif len(value) == 1:
                value = value[0]

            if key in self.SUBDIR_HEADER:
                self.fp.seek(value + self.SUBDIR_HEADER[key])
                self.data[key] = TagReader(self.fp, self.header)
            else:
                self.data[key] = value
            return self.data[key]

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
        for k, v in obj.iteritems():
            if isinstance(v, self.__class__):
                d[k] = self._dict(v)
            else:
                d[k] = v
        return d

    def tobytes(self):
        self.fp.seek(0)
        return self.EXIF_ID_CODE + self.fp.read()

    @classmethod
    def load(cls, img):
        '''
        Open image and load EXIF tags.
        '''
        if not isinstance(img, Image.Image):
            img = Image.open(img)
        if 'exif' not in img.info:
            raise ValueError('No EXIF.')

        body = img.info['exif'][len(TagReader.EXIF_ID_CODE):]
        fp = io.BytesIO(body)
        tiff_header = TIFFHeader(fp)
        exif_ifd = cls(fp, tiff_header)[tag.EXIF_IFD_POINTER]

        if tag.MAKER_NOTE not in exif_ifd:
            raise ValueError('No MakerNote.')

        fp.seek(exif_ifd.getoffset(tag.MAKER_NOTE))
        code_len = len(cls.RICOH_MAKERNOTE_CODE)
        if fp.read(code_len) != cls.RICOH_MAKERNOTE_CODE:
            raise ValueError('No RICOH maker note.')

        return cls(fp, tiff_header)
