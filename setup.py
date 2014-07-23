from setuptools import setup, find_packages, Extension
import util

table = {
    'msvc': {
        'openmp': ('/openmp', ''),
    },
    'default': {
        'openmp': ('-fopenmp', '-fopenmp'),
    },
}

try:
    import cython
    import numpy as np
    ext_modules = [
        Extension(
            'thetaexif.mapping',
            ['cy/mapping.pyx'],
            include_dirs=[np.get_include()],
            extra_compile_args=['openmp'],
            extra_link_args=['openmp'],
        ),
    ]
except ImportError:
    ext_modules = []

setup(
    name='thetaexif',
    version='0.1',
    author='Regen',
    author_email='git@exadge.com',
    description='THETA EXIF Library',
    long_description=(open('README.rst').read() + '\n\n' +
                      open('CHANGES.rst').read()),
    url='https://github.com/regen100/thetaexif',
    platforms='any',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Utilities',
    ],
    packages=find_packages(exclude=['*.tests']),
    ext_modules=ext_modules,
    test_suite='thetaexif.tests',
    install_requires=['numpy', 'pillow'],
    tests_require=['scipy'],
    extras_require={'tool': ['cython']},
    entry_points={
        'console_scripts': ['theta-tool = thetaexif.cli:parse [tool]'],
    },
    cmdclass={
        'build_ext': util.gen_build_ext(table),
    },
)
