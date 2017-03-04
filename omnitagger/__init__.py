#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Kim Koomen <koomen@protonail.com>
#
# Distributed under terms of the MIT license.

"""
A CLI that beautifies your (old) music files, automatically adds metatags
based on fingerprinting, filename and metadata.
"""

__version__ = '2.0.9'
__author__ = 'Kim Koomen'
__email__ = 'koomen@protonmail.com'
__url__ = 'https://github.com/kkoomen/omnitagger'
__license__ = 'MIT'


import logging
import os
import sys

log_format = '[%(levelname)s] %(message)s'
logging.basicConfig(format=log_format, level=logging.INFO)

for logger_name in ['requests']:
    logging.getLogger(logger_name).propagate = False

package_name = __name__.split('.', 1)[0]
if not os.path.exists(package_name):
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        pass
    else:
        os.makedirs(package_name)
