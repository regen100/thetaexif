EXIF_TAGS = {
    0x0103: 'Compression',
    0x011a: 'XResolution',
    0x011b: 'YResolution',
    0x0128: 'ResolutionUnit',
    0x0201: 'JPEGInterchangeFormat',
    0x0202: 'JPEGInterchangeFormatLength',
    0x8769: 'ExifIFDPointer',
    0x8825: 'GPSInfoIFDPointer',
    0x927c: 'MakerNote',
}

GPS_TAGS = {
    0x0011: 'GPSImgDirection',
}

MARKERNOTE_TAGS = {
    0x0001: 'MakerNoteType',
    0x0002: 'FirmwareVersion',
    0x0005: 'SerialNumber',
    0x1000: 'RecordingFormat',
    0x2001: 'RicohSubdir',
    0x4001: 'ThetaSubdir',
}

THETASUBDIR_TGAS = {
    0x0001: 'RicohCameraType',
    0x0002: 'HDRType',
    0x0003: 'ZenithEs',
    0x0004: 'CompassEs',
    0x0005: 'AbnormalAcceleration',
    0x0006: 'Zenith',
    0x0007: 'Compress',
    0x0101: 'FilmISO',
    0x0102: 'Aperture',
    0x0103: 'ExposureTime',
    0x0104: 'SensorSerial1',
    0x0105: 'SensorSerial2',
}


def _register(obj):
    import re
    import sys
    for tag, name in obj.items():
        name = re.sub('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))', r'_\1', name)
        setattr(sys.modules[__name__], name.upper(), tag)


_register(EXIF_TAGS)
_register(GPS_TAGS)
_register(MARKERNOTE_TAGS)
_register(THETASUBDIR_TGAS)
