from setuptools import find_packages, setup

setup(
    name='thetaexif',
    version='0.2',
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
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    packages=find_packages(exclude=['*.tests']),
    test_suite='thetaexif.tests',
    install_requires=['numpy', 'scipy', 'pillow'],
    entry_points={
        'console_scripts': ['theta-tool = thetaexif.cli:parse'],
    },
)
