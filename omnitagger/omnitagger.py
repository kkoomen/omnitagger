#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Kim Koomen <koomen@protonail.com>
#
# Distributed under terms of the MIT license.

"""
Contains the main logic for getting the files, beautify them, and log the info.
"""

import os
import re
import sys
import logging
from titlecase import titlecase
from shutil import copyfile
from omnitagger.metatagger import tagger
import acoustid

class OmniTagger:

    def __init__(self, args):
        self.package_name = __name__.split('.', 1)[0]
        self.destination = self.package_name
        for arg in vars(args):
            setattr(self, arg, getattr(args, arg))

    def get_files(self):
        """
        Get audio files of type mp3/ogg/flac recursively or non-recursively.

        :rtype: list
        """
        files = []
        if self.recursive:
            for root, dirnames, filenames in os.walk(os.getcwd()):
                for filename in filenames:
                    if filename.endswith(tuple(self.filetypes)):
                        cwd = root.replace(os.getcwd(), '')
                        dirname = cwd[1::].split('/', 1)[0]
                        if dirname != self.destination and filename not in self.ignore_files:
                            file = os.path.join(root, filename)
                            files.append(file)
        else:
            for filename in os.listdir(os.getcwd()):
                if filename.endswith(tuple(self.filetypes)) and filename not in self.ignore_files:
                    files.append(os.path.realpath(filename))

        if len(files) < 1:
            logging.error('No {} files found in your current directory.'.format(
                '/'.join(self.filetypes).replace('.', '').upper()
            ))
            exit(1)
        else:
            return sorted(files)

    def get_filename_pattern(self):
        """
        The filename should start with this pattern

        :rtype: string
        """
        pattern = '^'

        # Check for optional digits in the first line and check for parentheses,
        # dots or dashes in the second line. We should expect the following
        # cases (where the parentheses can also be a dot or dash of course,
        # which is most common):
        #
        # 01)FOx sTeVENsoN - trIGgeR.mp3
        # 01 ) FOx sTeVENsoN - trIGgeR.mp3
        # 01) FOx sTeVENsoN - trIGgeR.mp3
        # 01 )FOx sTeVENsoN - trIGgeR.mp3
        # 01FOx sTeVENsoN - trIGgeR.mp3
        pattern += '(?:[\d]+)?'
        pattern += '(?:\s*(?:\)|\.|\-)\s*)?'

        # The artist including the link sign. We should expect the following cases:
        #
        # 01 FOx sTeVENsoN - trIGgeR.mp3
        # 01 FOx sTeVENsoN -trIGgeR.mp3
        # 01 FOx sTeVENsoN- trIGgeR.mp3
        # 01 FOx sTeVENsoN-trIGgeR.mp3
        #
        # where #4 should be irrelevant. I didn't include it in the regex, since
        # we can pretty much assume that when you have a word with a link sign that
        # has no spaces on the left or right that it is one word. We assume that it
        # is an mistake only if it is a case #1, #2, or #3.
        #
        # We also make it optional because if the artist is None we can grab the
        # current directory its name or read the artist in the tags if it's already
        # in there.
        pattern += '(?:(.+)(?:\-\ |\ \-\ |\ \-))?'

        # We can assume this is the rest of the filename which will be the title
        # of the song.
        pattern += '(.+)'

        # The file extension (excluding the dot)
        pattern += '(?:\.(mp3|ogg|flac))'

        # String should also end with this pattern
        pattern += '$'
        return pattern

    def _get_find_artist_error_question(self):
        return (
            "Unable to find artist via filename or metadata for \"{}\". \n"
            "Is the directory name ({}) perhaps the exact artist name? [Y/n]: "
        )

    def _prompt_user_for_artist(self, answer):
        while not answer or answer.lower() not in 'yn':
            answer = input('Please enter Y or n: ')

        if answer.lower() == 'n':
            artist = input("Enter a new artist name: ")
        elif answer == 'y':
            artist = current_dir
        return artist

    def find_artist(self, filepath):
        """
        If we don't have an artist, then check if it is in the
        metadata already. Otherwise we prompt the user if the artist
        is the name of the current folder, which is a common case
        when you download an album.

        :param filepath: the absolute path of the file to look for the artist.
        :rtype: none/string
        """
        artist = None
        metadata = tagger.read(filepath)

        if metadata and metadata['artist']:
            return metadata['artist']

        _, current_dir, filename  = filepath.rsplit('/', 2)
        question = self._get_find_artist_error_question()
        question = question.format(filename, current_dir)
        answer = input(question)
        return self._prompt_user_for_artist(answer)

    def _titlecase_handler(self, word, **kwargs):
        """
        This function gets called for every word that is being titlecased.
        We will titlecase articles if the user adds the flag.
        If we don't return anything then it will be titlecased by the
        "titlecase" module itself.

        :param word: the word to check on
        :rtype: none/string
        """
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
        elif self.skip_beautifying:
            return filepart.strip()
        elif isinstance(filepart, list):
            filepart = filepart[0]

        # For e.g. ACDC we get AC/DC back from the fingerprint lookup.
        # We want that slash to be removed, else the copying part goes wrong.
        # It will then assume "AC" is the folder and "DC" is the beginning
        # of the filename.
        #
        # Also replace ’ with a normal apostrophe, since that's the "normal" way.
        formatted_filename = re.sub(r'[\_]+', ' ', filepart)
        formatted_filename = re.sub(r'[\/]+', '', formatted_filename)
        formatted_filename = re.sub(r'[’]+', '\'', formatted_filename)

        if formatted_filename.strip() not in self.exceptions:
            formatted_filename = titlecase(
                formatted_filename,
                callback=self._titlecase_handler
            )

        formatted = ' '.join(
            [w for w in formatted_filename.split(' ') if w]
        )
        return formatted

    def get_file_fingerprint_data(self, file):
        """
        Lookup filedata via acoustid.

        :param file: the file to lookup
        :rtype: boolean/dictionary
        """

        # check if fingerprint_lookup is set, since the lookup can take a few
        # milliseconds, which makes the process slow very quickly when dealing
        # with large amount of files.
        if not self.fingerprint_lookup:
            return False

        try:
            results = acoustid.match('3zV9hw9Egc', file)
        except Exception as e:
            logging.error('Could not do a fingerprint lookup\n{}'.format(e))
            return False

        for score, rid, title, artist in results:
            result = {
                'artist': artist,
                'title': title,
                'score': '{}%'.format(int(score * 100)),
                'score_raw': score,
            }
            return result if artist and title else False

    def _format_fingerprint_data(self, **kwargs):
        artist = kwargs['artist']
        title = kwargs['title']

        # The format we get back from the fingerprint lookup:
        # Antoine Dodson; The Gregory Brothers; Kelly Dodson - Bed Intruder Song.mp3
        #
        # If we have a semi-colon we know we have multiple artists.
        # The 1st one is always the original one. The rest we append
        # after the file name as (Ft. {artist} & {artist}) etc...
        #
        # We do this so the user still has their music files structured
        # by their artist.
        if self.fingerprint_lookup and ';' in artist:
            original_artist, featured_artists = artist.split(';', 1)
            artist = self.beautify(original_artist)

            # We can also receive the format "{artist} & {artist}", that
            # is why we replace that with a semi-colon.
            featured_artists = re.sub(r'&', ';', featured_artists)

            # Sometimes the names are already in the title. Only append
            # the artists that are still excluded in the title.
            excluded_featured_artists = [
                fa for fa in featured_artists.split(';') if fa.strip() not in title
            ]
            if excluded_featured_artists:
                excluded_featured_artists = ' & '.join(
                    [a for a in excluded_featured_artists if a]
                )
                title += ' (Ft. {})'.format(excluded_featured_artists)

        return [self.beautify(artist), self.beautify(title)]

    def _get_file_data(self, file):
        filepath, filename = file.rsplit('/', 1)
        pattern = self.get_filename_pattern()
        regex = re.match(pattern, filename)
        score = False
        fingerprint_data = self.get_file_fingerprint_data(file)

        if fingerprint_data:
            score = fingerprint_data['score']
            artist, title = self._format_fingerprint_data(
                artist=fingerprint_data['artist'],
                title=fingerprint_data['title']
            )
        else:
            artist = self.beautify(regex.group(1)) or self.beautify(self.find_artist(file))
            title = self.beautify(regex.group(2))

        extension = regex.group(3)
        return [artist, title, extension, score]

    def main(self):
        files = self.get_files()
        for index,file in enumerate(files):
            filepath, filename = file.rsplit('/', 1)
            valid_file = tagger.is_valid_audio_file(file)
            if  valid_file is False:
                continue

            artist, title, extension, score = self._get_file_data(file)

            # If we don't have an artist, we will skip this file.
            if not artist:
                logging.error('Unable to find artist for file "{}", skipping.'.format(filename))
                continue

            # copy the file under its new name
            dest_folder = os.path.join(os.getcwd(), self.destination)
            dest_filename = '{} - {}.{}'.format(artist, title, extension)
            dest_file = '{}/{}'.format(dest_folder, dest_filename)
            copyfile(file, dest_file)

            # write the metadata to the new file
            filedata = {
                'filename': dest_file,
                'artist': artist,
                'title': title,
                'extension': extension
            }
            tagger.write(filedata, clear=self.clear)

            if self.remove_original:
                os.remove(file)

            # log with a color to let the user know the file name has changed
            if filename != dest_filename:
                logging.info(
                    '\033[1;31m({}/{}) {}\033[0m --> \033[1;31m{}\033[0m'.format(
                        index + 1,
                        len(files),
                        filename,
                        dest_filename
                    )
                )
            else:
                logging.info('({}/{}) {}'.format(index + 1, len(files), dest_filename))
