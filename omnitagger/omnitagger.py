#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Kim Koomen <koomen@protonail.com>
#
# Distributed under terms of the MIT license.

"""
TODO
"""

import os
import re

class OmniTagger:

    def __init__(self):
        self.destination = '{}/omnitagger'.format(os.getcwd())
        self.recursive = True
        self.allowed_extensions = ('.mp3', '.ogg', '.flac')

    def get_files(self):
        files = []
        if self.recursive:
            for root, dirnames, filenames in os.walk(os.getcwd()):
                for filename in filenames:
                    if filename.endswith(self.allowed_extensions or ('.mp3', '.ogg', '.flac')):
                        cwd = root.replace(os.getcwd(), '')
                        dirname = cwd[1::].split('/', 1)[0]
                        if dirname != self.destination:
                            file = os.path.join(cwd[1::], filename)
                            files.append(file)
        else:
            for file in os.listdir(os.getcwd()):
                if file.endswith(self.allowed_extensions or ('.mp3', '.ogg', '.flac')):
                    files.append(file)

        if len(files) < 1:
            exit('No mp3/ogg/flac-files found in your current working directory.')
        else:
            return sorted(files)

    def get_filename_pattern(self):
        """
        The filename should start with this pattern
        """
        pattern = '^'

        """
        Check for optional digits in the first line and check for parentheses,
        dots or dashes in the second line. We should expect the following cases
        (where the parentheses can also be a dot or dash of course, which is
        most common):

        01)FOx sTeVENsoN - trIGgeR.mp3
        01 ) FOx sTeVENsoN - trIGgeR.mp3
        01) FOx sTeVENsoN - trIGgeR.mp3
        01 )FOx sTeVENsoN - trIGgeR.mp3
        01FOx sTeVENsoN - trIGgeR.mp3
        """
        pattern += '(?:[\d]+)?'
        pattern += '(?:\s*(?:\)|\.|\-)\s*)?'

        """
        The artist including the link sign. We should expect the following cases:

        01 FOx sTeVENsoN - trIGgeR.mp3
        01 FOx sTeVENsoN -trIGgeR.mp3
        01 FOx sTeVENsoN- trIGgeR.mp3
        01 FOx sTeVENsoN-trIGgeR.mp3

        where #4 should be irrelevant. I didn't include it in the regex, since
        we can pretty much assume that when you have a word with a link sign that
        has no spaces on the left or right that it is one word. We assume that it
        is an mistake only if it is a case #1, #2, or #3.

        We also make it optional because if the artist is None we can grab the
        current directory its name or read the artist in the tags if it's already
        in there.
        """
        pattern += '(?:(.+)(?:\-\ |\ \-\ |\ \-))?'

        """
        We can assume this is the rest of the filename which will be the title
        of the song.
        """
        pattern += '(.+)'

        """
        The file extension (excluding the dot)
        """
        pattern += '(?:\.(mp3|ogg|flac))'

        """
        String should also end with this pattern
        """
        pattern += '$'
        return pattern

    def beautify(self, filepart):
        if filepart is None:
            return

        formatted = ' '.join(
            [w for w in filepart.title().split(' ') if w]
        )
        return formatted

    def main(self):
        files = self.get_files()
        for filename in files:
            try:
                pattern = self.get_filename_pattern()
                regex = re.match(pattern, filename)

                artist = self.beautify(regex.group(1))
                title = self.beautify(regex.group(2))
                extension = regex.group(3)
                print('{} - {}.{}'.format(artist, title, extension))
            except AttributeError as e:
                print("\"{}\" does not match the pattern".format(filename))
                continue




omnitagger = OmniTagger()
