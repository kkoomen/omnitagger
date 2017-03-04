#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 Kim Koomen <koomen@protonail.com>
#
# Distributed under terms of the MIT license.

"""
Setuptools for omnitagger.
"""

from setuptools import setup

OMNITAGGER = __import__('omnitagger')
VERSION = OMNITAGGER.__version__
AUTHOR = OMNITAGGER.__author__
AUTHOR_EMAIL = OMNITAGGER.__email__
URL = OMNITAGGER.__url__
LICENSE = OMNITAGGER.__license__
DESCRIPTION = OMNITAGGER.__doc__

with open('requirements.txt') as requirements:
    REQUIREMENTS = requirements.readlines()

with open('README.rst') as readme:
    LONG_DESCRIPTION = readme.read()

setup(
    name='omnitagger',
    version=VERSION,
    url=URL,
    #download_url='{}/tarball/{}'.format(URL, VERSION),
    long_description=LONG_DESCRIPTION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    packages=[
        'omnitagger',
    ],
    package_dir={'omnitagger': 'omnitagger'},
    install_requires=REQUIREMENTS,
    license=LICENSE,
    scripts=['bin/omnitagger'],
    keywords=['music', 'beautifier', 'mp3', 'ogg', 'flac', 'local', 'tagger'],
    classifiers=[
        'Intended Audience :: Developers',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ]
)
