#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021 Julian Betz
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#      http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from __future__ import print_function
import sys
import os
from os.path import (abspath, realpath, expanduser, dirname, basename, join,
                     splitext)

# Check for the proper executable.
PROJECT_ROOT = dirname(abspath(realpath(expanduser(__file__))))
VIRTUALENVS_DIR = realpath(join(PROJECT_ROOT, 'virtualenvs', 'py3'))
if not sys.executable.startswith(join(VIRTUALENVS_DIR, '')):
    print('Activate the virtualenv in %r' % (VIRTUALENVS_DIR,),
          file=sys.stderr)
    sys.exit(1)

from typing import Tuple, Iterable
import click
import re
from fontTools.ttLib import TTFont, TTCollection
from fontTools.t1Lib import T1Font


UNREADABLE_FILE_TYPES = {'.pfa', '.pfb', '.gsf', '.pcf'}


def is_supporting_ttf(font: TTFont, character: int) -> bool:
    """Check whether the specified font supports the specified character.

    :param font: A TrueType, OpenType, or Web Open Font Format 2 font.

    :param character: The character to search for.

    :return: ``True`` if ``character`` is supported in ``font``, ``False`` if
        it is not.

    """
    return any(table.isUnicode() and character in table.cmap
               for table in font['cmap'].tables)


def is_supporting_t1(font: T1Font, character: int) -> bool:
    """Check whether the specified font supports the specified character.

    :param font: A T1 font.

    :param character: The character to search for.

    :return: ``True`` if ``character`` is supported in ``font``, ``False`` if
        it is not, and ``None`` if membership cannot be determined.

    """
    for key in font.getGlyphSet().keys():
        if ((len(key) == 1 and character == ord(key))
            or (re.fullmatch(r'uni[0-9A-F]+', key)
                and character == int(key[3:], 16))):
            return True
    return None
    

def get_ttf_family(font: TTFont) -> Tuple[str, str]:
    """Return the family and subfamily of the specified font.

    :param font: A TrueType, OpenType, or Web Open Font Format 2 font.

    :return: The family and subfamily of the specified font.

    """
    family, subfamily = '', ''
    for name in font['name'].names:
        if name.nameID == 1:
            if family == '':
                family = name.string.decode(name.getEncoding())
            else:
                break
        elif name.nameID == 2 and family != '':
            subfamily = name.string.decode(name.getEncoding())
            break
    return family, subfamily
    

def get_t1_family(file_path: str) -> Tuple[str, str]:
    """Return the family and subfamily of the specified font.

    Family and subfamily are not looked up in the file, but are estimated from
    the filename.

    :param file_path: The path to a T1 font file.

    :return: The family and subfamily of the font.

    """
    name = splitext(basename(file_path))[0].rsplit('-', 1)
    if len(name) == 2:
        return tuple(name)
    else:
        return name[0], ''


def get_supporting_fonts(code_point: int) -> Iterable[Tuple[str, str]]:
    """Find all fonts that support the specified Unicode code point.

    This recursively searches the directories ``/usr/share/fonts``,
    ``~/.local/share/fonts``, and ``~/.fonts`` for matching font files.

    :param code_point: The Unicode code point of the character to search for
        in the installed fonts.

    :return: An iterable over the family-subfamily tuples of all fonts that
        support the character corresponding to ``code_point``.

    """
    for directory in ('/usr/share/fonts',
                      expanduser('~/.local/share/fonts'),
                      expanduser('~/.fonts')):
        for dirpath, _, filenames in os.walk(directory, followlinks=True):
            for filename in filenames:
                file_path = join(dirpath, filename)
                file_extension = splitext(filename)[1]
                if file_extension in ('.ttf', '.otf', '.woff2'):
                    font = TTFont(file_path)
                    if is_supporting_ttf(font, code_point):
                        yield get_ttf_family(font)
                elif file_extension == '.ttc':
                    font_collection = TTCollection(file_path)
                    for font in font_collection.fonts:
                        if is_supporting_ttf(font, code_point):
                            yield get_ttf_family(font)
                elif file_extension == '.t1':
                    font = T1Font(file_path)
                    supporting = is_supporting_t1(font, code_point)
                    if supporting is None:
                        print('Unable to determine support in %s'
                              % (file_path,),
                              file=sys.stderr)
                    elif supporting:
                        yield get_t1_family(file_path)
                elif (file_extension in UNREADABLE_FILE_TYPES
                      or (file_extension == '.gz'
                          and splitext(splitext(filename)[0])[1]
                          in UNREADABLE_FILE_TYPES)):
                    print('Skipping unreadable %s' % (file_path,),
                          file=sys.stderr)


@click.command()
@click.argument('character', type=str)
@click.option('-f/-c', '--fine/--coarse', default=True, show_default=True,
              help='Whether to output font subfamilies in addition to '
              'families.')
@click.option('-s', '--separator', type=str, default='\t', show_default=False,
              help='The separator to use between font family and subfamily.  '
              '[default: TAB]')
@click.option('-z/-n', '--null/--newline', default=False, show_default=True,
              help='Whether to use ASCII null or newline to separate names.')
def main(character: str, *, fine: bool, separator: str, null: bool) -> None:
    """Search for all fonts that support CHARACTER.

    Supported font formats are TrueType (TTF/TTC), OpenType (OTF), and Web
    Open Font Format 2 (WOFF2).  The Type 1 (T1) font format is partially
    supported: Only the support of a limited set of characters can be
    detected, but not the lack of support of any character.  Printer Font
    ASCII (PFA), Printer Font Binary (PFB), X11 bitmap (PCF), and Ghostscript
    Font (GSF) files are found, but not analyzed for support.\f

    :param character: The character to search for.

    :param fine: Whether to output font subfamilies in addition to families.

    :param separator: The separator to use between font family and subfamily.

    :param null: Whether to use ASCII null or newline to separate names.

    """
    end = '\0' if null else '\n'
    fonts = get_supporting_fonts(ord(character))
    if fine:
        for family, subfamily in sorted(set(fonts)):
            print('%s%s%s' % (family, separator, subfamily), end=end)
    else:
        for family in sorted(set(font[0] for font in fonts)):
            print(family, end=end)


if __name__ == '__main__':
    main()
