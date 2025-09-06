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

class RadioRow(Adw.ActionRow):

    def __init__(self, title, group = None):
        Adw.ActionRow.__init__(self)
        self.title = title
        self.group = group

        super(RadioRow, self).set_title(title)

        self.button = Gtk.CheckButton()

        if (self.group != None):
            self.button.set_group(self.group)

        super(RadioRow, self).add_prefix(self.button)
        super(RadioRow, self).set_activatable_widget(self.button)

    def set_description(self, desc):
        super(RadioRow, self).set_subtitle(desc)

    def update_group(self, group):
        self.group = group
        self.button.set_group(self.group)