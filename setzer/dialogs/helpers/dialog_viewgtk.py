#!/usr/bin/env python3
# coding: utf-8

# Copyright (C) 2017-present Robert Griesel
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Adw

from setzer.keyboard_shortcuts.shortcut_controller import ShortcutController


class DialogView(Adw.Dialog):

    def __init__(self, main_window):
        Adw.Dialog.__init__(self)

        self.toolbar = Adw.ToolbarView()
        self.child = self.toolbar

        self.headerbar = Adw.HeaderBar()
        self.toolbar.add_top_bar(self.headerbar)
