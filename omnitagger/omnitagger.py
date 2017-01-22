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
import logging
from titlecase import titlecase
from shutil import copyfile
from omnitagger.metatagger import tagger

class OmniTagger:

    def __init__(self):
        self.destination = 'ot'
        self.exceptions = ['ZZ Top', 'TNT', 'xKito', 'ACDC']
        self.recursive = True
        self.titlecase_articles = True
        self.allowed_extensions = ['.mp3'] or ['.mp3', '.ogg', '.flac']

    def get_files(self):
        files = []
        if self.recursive:
            for root, dirnames, filenames in os.walk(os.getcwd()):
                for filename in filenames:
                    if filename.endswith(tuple(self.allowed_extensions)):
                        cwd = root.replace(os.getcwd(), '')
                        dirname = cwd[1::].split('/', 1)[0]
                        if dirname != self.destination:
                            file = os.path.join(root, filename)
                            files.append(file)
        else:
            for file in os.listdir(os.getcwd()):
                if file.endswith(tuple(self.allowed_extensions)):
                    files.append(os.path.realpath(file))

        if len(files) < 1:
            logging.error('No {} files found in your current directory.'.format(
                '/'.join(self.allowed_extensions).replace('.', '').upper()
            ))
            exit(1)
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

    def find_artist(self, filepath):
        """
        If we don't have an artist, then check if it is in the
        metadata already. Otherwise we prompt the user if the artist
        is the name of the current folder, which is a common case
        when you download an album.
        """
        artist = None
        metadata = tagger.read(filepath)

        if metadata and metadata['artist']:
            artist = self.beautify(metadata['artist'])
        else:
            _, current_dir, filename  = filepath.rsplit('/', 2)
            question = "Unable to find artist in filename or metadata for \"{}\". "
            question += "\nIs the directory name ({}) perhaps the "
            question += "exact artist name? [Y/n]: "
            question = question.format(filename, current_dir)
            answer = input(question)
            while not answer or answer.lower() not in 'yn':
                answer = input('Please enter Y or n. ')

            if answer.lower() == 'n':
                artist = input("Enter a new artist name: ")
            if answer == 'y':
                artist = current_dir

        if not artist:
            logging.error('Unable to find artist for file "{}", skipping.'.format(
                filename
            ))
        return artist

    def titlecase_handler(self, word, **kwargs):
        # Taken from
        # https://github.com/ppannuto/python-titlecase/blob/master/titlecase/__init__.py#L15
        articles = ['a','an','and','as','at','but','by','en','for','if','in',
                    'of','on','or','the','to','v','v.','via','vs','vs.']
        if self.titlecase_articles and word.lower() in articles:
            return word.title()

    def beautify(self, filepart):
        """
        Beautifies a part of a file.

        :param filepart: a string that can be the title or artist
        :rtype: string
        """
        if not filepart:
            return False
        elif isinstance(filepart, list):
            filepart = filepart[0]

        if filepart.strip() not in self.exceptions:
            filepart = titlecase(filepart.lower(), callback=self.titlecase_handler)

        formatted = ' '.join(
            [w for w in filepart.split(' ') if w]
        )
        return formatted

    def main(self):
        files = self.get_files()
        for index,file in enumerate(files):
            try:
                filepath, filename = file.rsplit('/', 1)
                valid_file = tagger.is_valid_audio_file(file)
                if valid_file is False:
                    continue

                pattern = self.get_filename_pattern()
                regex = re.match(pattern, filename)

                artist = self.beautify(regex.group(1) or self.find_artist(file))
                title = self.beautify(regex.group(2))
                extension = regex.group(3)

                if not artist:
                    continue

                # copy the file under its new name
                dest_folder = os.path.join(os.getcwd(), self.destination)
                dest_filename = '{} - {}.{}'.format(artist, title, extension)
                dest_file = '{}/{}'.format(dest_folder, dest_filename)
                copyfile(file, dest_file)

                # write the metadata
                filedata = {
                    'filename': dest_file,
                    'artist': artist,
                    'title': title,
                    'extension': extension
                }
                tagger.write(filedata)

                logging.info('({}/{}) {}'.format(index+1, len(files), dest_filename))
            except AttributeError as e:
                logging.error("\"{}\" does not match the pattern".format(filename))
                continue




omnitagger = OmniTagger()
