# Copyright (C) 2005-2007 Osmo Salomaa
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


"""Tools menu UI manager actions."""


from gettext import gettext as _

from ._action import UIMAction


class AppendFileAction(UIMAction):

    """Append subtitles from file to the current project."""

    action_item = (
        "append_file",
        None,
        _("_Append File..."),
        None,
        _("Append subtitles from file to the current project"),)

    paths = ["/ui/menubar/tools/append_file"]

    @classmethod
    def is_doable(cls, application, page):
        """Return True if action can be done."""

        return (page is not None)


class SplitProjectAction(UIMAction):

    """Split the current project in two."""

    action_item = (
        "split_project",
        None,
        _("_Split Project..."),
        None,
        _("Split the current project in two"),)

    paths = ["/ui/menubar/tools/split_project"]

    @classmethod
    def is_doable(cls, application, page):
        """Return True if action can be done."""

        if page is not None:
            return len(page.project.times) > 1
        return False
