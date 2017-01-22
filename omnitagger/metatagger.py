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


from mutagen.mp3 import MP3
from mutagen.mp3 import HeaderNotFoundError
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, TIT2, TPE1, TPE2
from mutagen.flac import FLAC, FLACNoHeaderError
from mutagen.oggvorbis import OggVorbis, OggVorbisHeaderError
import mutagen.id3
import logging

class Tagger:

    def is_valid_audio_file(self, filename):
        _, ext = filename.rsplit('.', 1)
        try:
            if ext == 'mp3':
                audio = MP3(filename, ID3=EasyID3)
            elif ext == 'flac':
                audio = FLAC(filename)
            elif ext == 'ogg':
                audio = OggVorbis(filename)
            return audio
        except (HeaderNotFoundError, FLACNoHeaderError, OggVorbisHeaderError):
            logging.error('"{}" is not a valid audio file.'.format(filename))

        return False

    def read(self, filename):
        metadata = self.is_valid_audio_file(filename)
        return metadata


    def write(self, file, **kwargs):
        """
        Adds metadata to a file

        :param file: a dictionary containing file data
        """

        if file['extension'] == 'mp3':
            audio = MP3(file['filename'], ID3=EasyID3)
            try:
                audio.add_tags(ID3=EasyID3)
                if kwargs['clear']:
                    audio.clear()
            except (mutagen.id3.error, KeyError):
                pass
            audio['title'] = file['title']
            audio['artist'] = file['artist']
            audio.save()
            audio.save(v1=2, v2_version=3)
        elif file['extension'] == 'flac':
            try:
                audio = FLAC(file['filename'])
                if kwargs['clear']:
                    audio.clear()
            except (FLACNoHeaderError, KeyError):
                audio = FLAC()

            audio['TITLE'] = file['title']
            audio['ARTIST'] = file['artist']
            audio.save(file['filename'])
        elif file['extension'] == 'ogg':
            try:
                audio = OggVorbis(file['filename'])
                if kwargs['clear']:
                    audio.clear()
            except (OggVorbisHeaderError, KeyError):
                audio = OggVorbis()

            audio['title'] = file['artist']
            audio['artist'] = file['artist']
            audio['ALBUMARTIST'] = file['artist']
            audio.save(file['filename'])

tagger = Tagger()
