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


class PageEditor(object):

    def __init__(self, preferences, settings):
        self.view = PageEditorView()
        self.preferences = preferences
        self.settings = settings

    def init(self):
        self.view.option_spaces_instead_of_tabs.set_active(self.settings.get_value('preferences', 'spaces_instead_of_tabs'))
        self.view.option_spaces_instead_of_tabs.connect('notify::active', self.preferences.on_check_button_toggle, 'spaces_instead_of_tabs')

        self.view.tab_width_spinbutton.get_adjustment().set_value(self.settings.get_value('preferences', 'tab_width'))
        self.view.tab_width_spinbutton.get_adjustment().connect('value-changed', self.preferences.spin_button_changed, 'tab_width')

        self.view.option_show_line_numbers.set_active(self.settings.get_value('preferences', 'show_line_numbers'))
        self.view.option_show_line_numbers.connect('notify::active', self.preferences.on_check_button_toggle, 'show_line_numbers')

        self.view.option_line_wrapping.set_active(self.settings.get_value('preferences', 'enable_line_wrapping'))
        self.view.option_line_wrapping.connect('notify::active', self.preferences.on_check_button_toggle, 'enable_line_wrapping')

        self.view.option_code_folding.set_active(self.settings.get_value('preferences', 'enable_code_folding'))
        self.view.option_code_folding.connect('notify::active', self.preferences.on_check_button_toggle, 'enable_code_folding')

        self.view.option_highlight_current_line.set_active(self.settings.get_value('preferences', 'highlight_current_line'))
        self.view.option_highlight_current_line.connect('notify::active', self.preferences.on_check_button_toggle, 'highlight_current_line')

        self.view.option_highlight_matching_brackets.set_active(self.settings.get_value('preferences', 'highlight_matching_brackets'))
        self.view.option_highlight_matching_brackets.connect('notify::active', self.preferences.on_check_button_toggle, 'highlight_matching_brackets')


class PageEditorView(Adw.PreferencesPage):

    def __init__(self):
        Adw.PreferencesPage.__init__(self)
        super(PageEditorView, self).set_title(_('Editor'))
        super(PageEditorView, self).set_icon_name('edit-symbolic')

        group = Adw.PreferencesGroup()
        group.set_title(_('Tab Stops'))

        self.option_spaces_instead_of_tabs = Adw.SwitchRow()
        self.option_spaces_instead_of_tabs.set_title(_('Insert spaces instead of tabs'))
        group.add(self.option_spaces_instead_of_tabs)

        self.tab_width_spinbutton = Adw.SpinRow.new_with_range(1, 8, 1)
        self.tab_width_spinbutton.set_title(_('Tab width'))
        group.add(self.tab_width_spinbutton)

        self.add(group)


        group = Adw.PreferencesGroup()
        group.set_title(_('Lines'))

        self.option_show_line_numbers = Adw.SwitchRow()
        self.option_show_line_numbers.set_title(_('Show line numbers'))
        group.add(self.option_show_line_numbers)

        self.add(group)

        self.option_line_wrapping = Adw.SwitchRow()
        self.option_line_wrapping.set_title(_('Enable line wrapping'))
        group.add(self.option_line_wrapping)

        self.option_highlight_current_line = Adw.SwitchRow()
        self.option_highlight_current_line.set_title(_('Highlight current line'))
        group.add(self.option_highlight_current_line)

        self.add(group)


        group = Adw.PreferencesGroup()
        group.set_title(_('Code'))

        self.option_code_folding = Adw.SwitchRow()
        self.option_code_folding.set_title(_('Enable code folding'))
        group.add(self.option_code_folding)

        self.option_highlight_matching_brackets = Adw.SwitchRow()
        self.option_highlight_matching_brackets.set_title(_('Highlight matching brackets'))
        group.add(self.option_highlight_matching_brackets)

        self.add(group)
