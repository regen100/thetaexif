=========
thetaexif
=========
.. image:: https://badge.fury.io/py/thetaexif.svg
    :target: http://badge.fury.io/py/thetaexif
.. image:: https://travis-ci.org/regen100/thetaexif.svg?branch=master
    :target: https://travis-ci.org/regen100/thetaexif

`thetaexif` is a Python library for RICOH THETA image.
It provides a EXIF reader class and a rectification tool.

Requirements
============
* Python 3.6 or later
* Pillow
* Scipy

Setup
=====
::

    $ pip install thetaexif

Usage
=====

In Python
---------
::

    >>> from thetaexif import ExifReader, tag
    >>> reader = ExifReader('image.jpg')
    >>> reader.makernote[tag.FIRMWARE_VERSION]
    b'Rev0102'
    >>> reader.theta[tag.ZENITH_ES]
    (Fraction(20, 1), Fraction(-24, 1))

Show Theta EXIF
---------------
::

    $ theta-tool info image.jpg
    RICOH Marker Note
    0x0001 [MakerNoteType]: Rdc
    0x0002 [FirmwareVersion]: Rev0102
    0x0005 [SerialNumber]: 0000000000102690
    0x1000 [RecordingFormat]: 2

    THETA Subdir
    0x0001 [RicohCameraType]: 1
    0x0002 [HDRType]: 0
    0x0003 [ZenithEs]: (20, -24)
    0x0004 [CompassEs]: 45/2
    0x0005 [AbnormalAcceleration]: 0
    0x0101 [FilmISO]: (100, 0, 100, 0)
    0x0102 [Aperture]: (21/10, 21/10)
    0x0103 [ExposureTime]: (1/4000, 1/4000)
    0x0104 [SensorSerial1]: A0015348
    0x0105 [SensorSerial2]: A0015357

Rectification
-------------
`rectify` command reads gyroscope and compass data and rotate images to rectify camera pose.

Rectify image.jpg and save to image_rectified.jpg::

    $ theta-tool rectify image.jpg

Rectify image.jpg using compass data (rotate image to face the north)::

    $ theta-tool rectify -c image.jpg

Keep EXIF and rectify::

    $ theta-tool rectify -e image.jpg

