# Copyright (C) 2006 Osmo Salomaa
#
# This file is part of Gaupol.
#
# Gaupol is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# Gaupol is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Gaupol; if not, write to the Free Software Foundation, Inc., 51 Franklin
# Street, Fifth Floor, Boston, MA 02110-1301, USA.


"""TMPlayer file."""


import codecs

from gaupol import cons
from gaupol.calculator import Calculator
from ._subfile import SubtitleFile


class TMPlayer(SubtitleFile):

    """TMPlayer file."""

    format = cons.FORMAT.TMPLAYER
    has_header = False
    identifier = r"^\d\d:\d\d:\d\d:.*$", 0
    mode = cons.MODE.TIME

    def read(self):
        """Read file.

        Raise IOError if reading fails.
        Raise UnicodeError if decoding fails.
        Return show times, hide times, texts.
        """
        shows = []
        hides = []
        texts = []
        for line in self._read_lines():
            if len(line.strip()) >= 9:
                shows.append(line[:8] + ".000")
                texts.append(line[9:-1])

        calc = Calculator()
        for i in range(1, len(shows)):
            hides.append(shows[i])
        hides.append(calc.add_seconds_to_time(shows[-1], 3.000))
        texts = list(x.replace("|", "\n") for x in texts)
        return shows, hides, texts

    def write(self, shows, hides, texts):
        """Write file.

        Raise IOError if writing fails.
        Raise UnicodeError if encoding fails.
        """
        calc = Calculator()
        shows = list(calc.round_time(x, 0)[:8] + ":" for x in shows)
        texts = list(x.replace("\n", "|") for x in texts)

        fobj = codecs.open(self.path, "w", self.encoding)
        try:
            for i in range(len(shows)):
                fobj.write("%s%s%s" % (shows[i], texts[i], self.newline.value))
        finally:
            fobj.close()
