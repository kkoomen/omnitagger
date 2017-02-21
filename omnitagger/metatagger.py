#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Kim Koomen <koomen@protonail.com>
#
# Distributed under terms of the MIT license.

"""
This file contains the tagger that reads/writes to a file.
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

    def is_valid_audio_file(self, filepath):
        """
        Check if a file is valid by putting in through mutagen.
        A file isn't an audio file of mutagen throws an header error

        :param filepath: the absolute path of the file to check on
        :returns: the audio file containing the metadata
        :rtype: boolean/class
        """
        _, filename = filepath.rsplit('/', 1)
        _, ext = filename.rsplit('.', 1)
        try:
            if ext == 'mp3':
                audio = MP3(filepath, ID3=EasyID3)
            elif ext == 'flac':
                audio = FLAC(filepath)
            elif ext == 'ogg':
                audio = OggVorbis(filepath)
            return audio
        except (HeaderNotFoundError, FLACNoHeaderError, OggVorbisHeaderError):
            logging.error('"{}" is not a valid audio file.'.format(filename))

        return False

    def read(self, filepath):
        """
        A wrapper around the is_valid_audio_file -function.

        :param filepath: the absolute path of the file to check on
        :returns: the audio file containing the metadata
        :rtype: boolean/class
        """
        metadata = self.is_valid_audio_file(filepath)
        return metadata

    def _write_mp3_metatags(self, file, **kwargs):
        audio = MP3(file['filename'], ID3=EasyID3)
        try:
            audio.add_tags(ID3=EasyID3)
        except (mutagen.id3.error, KeyError) as e:
            pass

        if kwargs['clear']:
            audio.delete()
        audio['title'] = file['title']
        audio['artist'] = file['artist']
        audio.save()
        audio.save(v1=2, v2_version=3)

    def _write_ogg_metatags(self, file, **kwargs):
        try:
            audio = OggVorbis(file['filename'])
        except (OggVorbisHeaderError, KeyError):
            audio = OggVorbis()

        if kwargs['clear']:
            audio.delete()
        audio['title'] = file['title']
        audio['artist'] = file['artist']
        audio['ALBUMARTIST'] = file['artist']
        audio.save(file['filename'])

    def _write_flac_metatags(self, file, **kwargs):
        try:
            audio = FLAC(file['filename'])
        except (FLACNoHeaderError, KeyError):
            audio = FLAC()

        if kwargs['clear']:
            audio.delete()
        audio['TITLE'] = file['title']
        audio['ARTIST'] = file['artist']
        audio.save(file['filename'])

    def write(self, file, **kwargs):
        """
        Adds metadata to a file

        :param file: a dictionary containing file data
        """

        if file['extension'] == 'mp3':
            self._write_mp3_metatags(file, **kwargs)
        elif file['extension'] == 'flac':
            self._write_flac_metatags(file, **kwargs)
        elif file['extension'] == 'ogg':
            self._write_ogg_metatags(file, **kwargs)

tagger = Tagger()
