# Copyright (C) 2005 Osmo Salomaa
#
# This file is part of Gaupol.
#
# Gaupol is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Gaupol is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Gaupol; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA


"""Editing entire rows (subtitles)."""


try:
    from psyco.classes import *
except ImportError:
    pass

import gtk

from gaupol.constants import POSITION, TYPE
from gaupol.gui.colcons import *
from gaupol.gui.delegates.delegate import Delegate
from gaupol.gui.delegates.durmanager import DURAction
from gaupol.gui.dialogs.insertsub import InsertSubtitleDialog


class RowInsertAction(DURAction):

    """Action to insert subtitles."""
    
    def __init__(self, project, position, amount):

        self.project = project

        selected_rows = project.get_selected_rows()

        if not selected_rows:
            self._start_row = 0
        elif position == POSITION.ABOVE:
            self._start_row = selected_rows[0]
        elif position == POSITION.BELOW:
            self._start_row = selected_rows[0] + 1

        self._amount = amount
        self._inserted_rows = []

        self.description = _('Inserting subtitles')
        self.documents = [TYPE.MAIN, TYPE.TRAN]

    def do(self):
        """Insert rows."""

        # Insert new rows to Data.
        self.project.data.insert_subtitles(self._start_row, self._amount)

        tree_view_column = self.project.get_focus()[2]
        tree_view = self.project.tree_view
        model     = tree_view.get_model()
        timings   = self.project.get_timings()
        texts     = self.project.data.texts

        # Insert rows to ListStore and save new rows.
        for row in range(self._start_row, self._start_row + self._amount):
            model.insert(row, [row + 1] + timings[row] + texts[row])
            self._inserted_rows.append(row)

        self.project.reload_data_in_columns(NO)

        # Move focus to first of the new rows.
        try:
            tree_view.set_cursor(self._start_row, tree_view_column)
        except TypeError:
            pass

        # Select all new rows.
        selection = tree_view.get_selection()
        selection.unselect_all()
        for row in range(self._start_row, self._start_row + self._amount):
            selection.select_path(row)

    def undo(self):
        """Remove inserted rows."""

        # Remove rows from Data.
        self.project.data.remove_subtitles(self._inserted_rows)
        
        # Remove rows from ListStore.
        model = self.project.tree_view.get_model()
        for row in self._inserted_rows:
            model.remove(model.get_iter(row))

        self.project.reload_data_in_columns(NO)


class RowRemoveAction(DURAction):

    """Action to remove selected subtitles."""
    
    def __init__(self, project):

        self.project = project

        self._selected_rows = project.get_selected_rows()
        
        self.description = _('Removing subtitles')
        self.documents = [TYPE.MAIN, TYPE.TRAN]

        texts  = project.data.texts
        times  = project.data.times
        frames = project.data.frames

        # Save data.
        self._removed_times  = [times[row]  for row in self._selected_rows]
        self._removed_frames = [frames[row] for row in self._selected_rows]
        self._removed_texts  = [texts[row]  for row in self._selected_rows]

    def do(self):
        """Remove rows."""

        tree_view_column = self.project.get_focus()[2]

        # Remove rows from Data.
        self.project.data.remove_subtitles(self._selected_rows)

        rows = self._selected_rows[:]
        rows.sort()
        rows.reverse()
        
        # Remove rows from ListStore.
        model = self.project.tree_view.get_model()
        for row in rows:
            model.remove(model.get_iter(row))

        self.project.reload_data_in_columns(NO)

        # Move focus and select first row of selection or last existing row.
        if self.project.data.times:
            row = min(self._selected_rows[0], len(self.project.data.times) - 1)
            try:
                self.project.tree_view.set_cursor(row, tree_view_column)
            except TypeError:
                pass

    def undo(self):
        """Restore rows."""
        
        model = self.project.tree_view.get_model()
        data  = self.project.data
        
        for i in range(len(self._selected_rows)):

            # Restore rows to Data.
            row = self._selected_rows[i]
            data.texts.insert( row, self._removed_texts[ i])
            data.times.insert( row, self._removed_times[ i])
            data.frames.insert(row, self._removed_frames[i])
            
            # Add blank rows to ListStore.
            model.append()

        # Restore rows to ListStore.
        self.project.reload_all_data()


class RowEditor(Delegate):

    """Editing entire rows (subtitles)."""

    def insert_subtitles(self, position, amount):
        """Insert blank subtitles at selection."""
        
        project = self.get_current_project()
        action = RowInsertAction(project, position, amount)
        self.do_action(project, action)

    def on_insert_subtitles_activated(self, *args):
        """Insert blank subtitles at selection."""
        
        position_name = self.config.get('insert_subtitles', 'position')
        position = POSITION.NAMES.index(position_name)
        amount = self.config.getint('insert_subtitles', 'amount')
        
        dialog = InsertSubtitleDialog(self.window)
        
        dialog.set_amount(amount)
        dialog.set_position(position)

        project = self.get_current_project()
        if not project.data.times:
            dialog.set_position_sensitive(False)
        
        response = dialog.run()
        position = dialog.get_position()
        position_name = POSITION.NAMES[position]
        amount = dialog.get_amount()
        dialog.destroy()

        if response != gtk.RESPONSE_OK:
            return

        self.config.set('insert_subtitles', 'position', position_name)
        self.config.setint('insert_subtitles', 'amount', amount)

        self.insert_subtitles(position, amount)

    def on_invert_selection_activated(self, *args):
        """Invert current selection."""

        project = self.get_current_project()
        
        selected_rows = project.get_selected_rows()
        selection = project.tree_view.get_selection()
        
        selection.select_all()
        for row in selected_rows:
            selection.unselect_path(row)

        project.tree_view.grab_focus()
        
    def on_remove_subtitles_activated(self, *args):
        """Remove selected subtitles."""

        project = self.get_current_project()
        action = RowRemoveAction(project)
        self.do_action(project, action)

    def on_select_all_activated(self, *args):
        """Select all subtitles."""

        project = self.get_current_project()
        
        selection = project.tree_view.get_selection()
        selection.select_all()
        
        project.tree_view.grab_focus()

    def on_unselect_all_activated(self, *args):
        """Unselect all subtitles."""

        project = self.get_current_project()
        
        selection = project.tree_view.get_selection()
        selection.unselect_all()
        
        project.tree_view.grab_focus()
