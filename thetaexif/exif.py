# References:
# - http://xanxys.hatenablog.jp/entry/20131110/1384094832
# - http://www.ozhiker.com/electronics/pjmt/jpeg_info/ricoh_mn.html
# - http://www.sno.phy.queensu.ca/~phil/exiftool/TagNames/Ricoh.html
# - https://github.com/atotto/ricoh-theta-tools

import io
import collections
import struct
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
                return float(unpacked[0]) / unpacked[1]
        handler.size = st.size
        handler.typeid = typeid
        handlers[typeid] = handler
    return handlers

lehandlers = build_handler('<')
behandlers = build_handler('>')


class TagReader(collections.Mapping):
    '''
    EXIF tag reader class for THETA image.
    '''
    subdir = {tag.RICOH_SUBDIR: 20, tag.THETA_SUBDIR: 0}

    def __init__(self, endian, fp):
        self.endian = endian[:2]
        self.fp = fp
        self.tags = {}
        self.data = {}

        if self.endian == 'II':
            self.handlers = lehandlers
        elif self.endian == 'MM':
            self.handlers = behandlers
        else:
            raise ValueError('endian must be II or MM.')

        u16 = self.handlers[3]
        u32 = self.handlers[4]

        for i in xrange(u16(fp)):
            tagid = u16(fp)
            tagtype = u16(fp)
            try:
                handler = self.handlers[tagtype]
            except IndexError:
                raise ValueError('Invalid data type.')
            num = u32(fp)
            if handler.size * num > 4:
                offset = u32(fp)
            else:
                offset = fp.tell()
                fp.seek(4, io.SEEK_CUR)

            self.tags[tagid] = (handler, num, offset)

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

            if key in self.subdir:
                self.fp.seek(value + self.subdir[key])
                self.data[key] = TagReader(self.endian, self.fp)
            else:
                self.data[key] = value
            return self.data[key]

    def __iter__(self):
        return iter(self.tags)

    def __len__(self):
        return len(self.tags)

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

    @classmethod
    def load(cls, img):
        '''
        Open image and load EXIF tags.
        '''
        if not isinstance(img, Image.Image):
            img = Image.open(img)
        if 'exif' not in img.info:
            raise ValueError('No EXIF.')

        body = img.info['exif'][6:]
        offset = body.find('Ricoh\x00\x00\x00')
        if offset == -1:
            raise ValueError('No RICOH maker note.')

        fp = io.BytesIO(body)
        header = fp.read(8)
        fp.seek(offset + 8)
        return cls(header, fp)
