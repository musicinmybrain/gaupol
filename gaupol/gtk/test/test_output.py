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


import gtk

from gaupol.gtk.unittest import TestCase
from .. import output


class TestOutputWindow(TestCase):

    def run(self):

        def destroy(*args):
            if not self.window.props.visible:
                self.window.destroy()
                gtk.main_quit()
        self.window.connect("notify::visible", destroy)
        self.window.show()
        gtk.main()

    def setup_method(self, method):

        self.window = output.OutputWindow()

    def test__on_close_button_clicked(self):

        self.window._on_close_button_clicked()

    def test__on_close_key_pressed(self):

        self.window._on_close_key_pressed()

    def test__on_delete_event(self):

        self.window._on_delete_event()

    def test__on_notify_visible(self):

        self.window.show()
        self.window.hide()

    def test_on_window_state_event(self):

        self.window.maximize()
        self.window.unmaximize()

    def test__save_geometry(self):

        self.window._save_geometry()

    def test_set_output(self):

        self.window.set_output("test")
        text_buffer = self.window._text_view.get_buffer()
        bounds = text_buffer.get_bounds()
        text = text_buffer.get_text(*bounds)
        assert text == "test"
