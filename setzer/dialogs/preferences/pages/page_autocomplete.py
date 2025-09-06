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


class PageAutocomplete(object):

    def __init__(self, preferences, settings):
        self.view = PageAutocompleteView()
        self.preferences = preferences
        self.settings = settings

    def init(self):
        self.view.option_autocomplete.set_active(self.settings.get_value('preferences', 'enable_autocomplete'))
        self.view.option_autocomplete.connect('notify::active', self.preferences.on_check_button_toggle, 'enable_autocomplete')

        self.view.option_bracket_completion.set_active(self.settings.get_value('preferences', 'enable_bracket_completion'))
        self.view.option_bracket_completion.connect('notify::active', self.preferences.on_check_button_toggle, 'enable_bracket_completion')

        self.view.option_selection_brackets.set_active(self.settings.get_value('preferences', 'bracket_selection'))
        self.view.option_selection_brackets.connect('notify::active', self.preferences.on_check_button_toggle, 'bracket_selection')

        self.view.option_tab_jump_brackets.set_active(self.settings.get_value('preferences', 'tab_jump_brackets'))
        self.view.option_tab_jump_brackets.connect('notify::active', self.preferences.on_check_button_toggle, 'tab_jump_brackets')

        self.view.option_update_matching_blocks.set_active(self.settings.get_value('preferences', 'update_matching_blocks'))
        self.view.option_update_matching_blocks.connect('notify::active', self.preferences.on_check_button_toggle, 'update_matching_blocks')


class PageAutocompleteView(Adw.PreferencesPage):

    def __init__(self):
        Adw.PreferencesPage.__init__(self)
        super(PageAutocompleteView, self).set_title(_('Autocomplete'))
        super(PageAutocompleteView, self).set_icon_name('code-symbolic')

        group = Adw.PreferencesGroup()
        group.set_title('<b>' + _('LaTeX Commands') + '</b>')

        self.option_autocomplete = Adw.SwitchRow()
        self.option_autocomplete.set_title(_('Suggest matching LaTeX Commands'))
        group.add(self.option_autocomplete)

        self.add(group)


        group = Adw.PreferencesGroup()
        group.set_title(_('Others'))

        self.option_bracket_completion = Adw.SwitchRow()
        self.option_bracket_completion.set_title(_('Automatically add closing brackets'))
        group.add(self.option_bracket_completion)

        self.option_selection_brackets = Adw.SwitchRow()
        self.option_selection_brackets.set_title(_('Add brackets to selected text, instead of replacing it with them'))
        group.add(self.option_selection_brackets)

        self.option_tab_jump_brackets = Adw.SwitchRow()
        self.option_tab_jump_brackets.set_use_markup(True)
        self.option_tab_jump_brackets.set_title(_('Jump over closing brackets with <tt>Tab</tt>'))
        group.add(self.option_tab_jump_brackets)

        self.option_update_matching_blocks = Adw.SwitchRow()
        self.option_update_matching_blocks.set_use_markup(True)
        self.option_update_matching_blocks.set_title(_('Update matching <tt>begin</tt> / <tt>end</tt> blocks'))
        group.add(self.option_update_matching_blocks)

        self.add(group)
