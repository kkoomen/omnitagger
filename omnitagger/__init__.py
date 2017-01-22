#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Kim Koomen <koomen@protonail.com>
#
# Distributed under terms of the MIT license.

"""
A CLI that beautifies your (old) music files and automatically adds metatags
based on the filename.
"""

__version__ = '0.0.1'
__author__ = 'Kim Koomen'
__email__ = 'koomen@protonmail.com'
__url__ = 'https://github.com/muts/omni-tagger'
__license__ = 'MIT'


import logging

module_name = __name__.split('.')[0]
log_format = '[{}] [%(levelname)s] %(message)s'.format(module_name)

console = logging.StreamHandler()
console.setFormatter(logging.Formatter(log_format))

logging.getLogger('').addHandler(console)
