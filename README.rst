=========
thetaexif
=========
.. image:: https://badge.fury.io/py/thetaexif.svg
    :target: http://badge.fury.io/py/thetaexif

`thetaexif` is a Python library for RICOH THETA image.
It provides a EXIF reader class and a rectification tool.

Requirements
============
* Python 2.7 (not support 3.x)
* Pillow
* Numpy

For rectification function:

* Cython
* Scipy or OpenCV Python bindings

Setup
=====
::

    $ pip install thetaexif

Usage
=====

In Python
---------
::

    >>> from thetaexif import TagReader, tag
    >>> reader = TagReader.load('image.jpg')
    >>> reader[tag.FIRMWARE_VERSION]
    'Rev0102'
    >>> reader[tag.THETA_SUBDIR][tag.ZENITH_ES]
    (20.0, -24.0)

In shell
--------
::

    $ python -m thetaexif image.jpg
    RecordingFormat: 2
    MakerNoteType: Rdc
    FirmwareVersion: Rev0102
    SerialNumber: 0000000000000000
    RicohCameraType: 1
    HDRType: 0
    ZenithEs: (20.0, -24.0)
    CompassEs: 22.5
    AbnormalAcceleration: 0
    FilmISO: (100, 0, 100, 0)
    Aperture: (2.1, 2.1)
    ExposureTime: (0.00025, 0.00025)
    SensorSerial1: A0015348
    SensorSerial2: A0015357

Rectification (requires Cython)
-------------------------------
If you install thetaexif with Cython, ``theta-rectify`` command is available.
It reads gyroscope and compass data and rotate images to rectify camera pose.

Rectify image.jpg and save to image_rectified.jpg::

    $ theta-rectify image.jpg

Rectify image.jpg using compass data (rotate image to face the north)::

    $ theta-rectify -c image.jpg
