omnitagger
==========

Omnitagger is a CLI tool for beautifying your music files and adding
metadata automatically to your files. It provides fingerprint lookup via
`acoustid <https://github.com/beetbox/pyacoustid>`__. Wether this is
specified or not: after that it will check for the
``artist - title.{mp3,flac,ogg}`` format. If that pattern isn't found
either, it will check the directory the file is in, since it is a common
case that when you download an album, the structure is:

::

    artist-name/
    ├── title.mp3
    ├── title.mp3
    ├── title.mp3
    └── title.mp3

If that isn't an options either, it will skip the file and continue to
the next one. For more information on how omnitagger works, visit the
`How it works <https://github.com/kkoomen/omnitagger/wiki/How-it-works>`__
page on the wiki.

Installation
============

-  ``$ git clone https://github.com/kkoomen/omnitagger``
-  ``$ cd omnitagger``
-  ``$ ./setup.py install``

Documentation
=============

Visit the
`documentation <https://github.com/kkoomen/omnitagger/wiki/Documentation>`__
on the wiki for further details on how to use omnitagger.

The purpose of omnitagger
=========================

The purpose of omnitagger was a personal issue we all can relate to in
the early days: You download an album or song using a YouTube converter
(or oldschool Limewire/Frostwire back in those days) and the names do
look horrible. Names with numbers in front of it while it is already in
the metatags, underscores instead of spaces... you get it. This was an
issue me and a friend of mine always had and I suddenly had the idea to
create a python script to make from an ugly and horrible-looking
filename a good-looking filename with metatags set correctly
automatically. Once I had the idea I kept building and building and
sometimes even rebuilding the whole script to make it better and more
efficient.

License
=======

MIT.
