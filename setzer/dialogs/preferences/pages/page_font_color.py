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
gi.require_version('GtkSource', '5')
from gi.repository import Gtk, Adw
from gi.repository import GLib, GObject
from gi.repository import Pango
from gi.repository import GtkSource

import os, os.path
import shutil
import xml.etree.ElementTree as ET

from setzer.app.service_locator import ServiceLocator
from setzer.app.font_manager import FontManager


class PageFontColor(object):

    def __init__(self, preferences, settings, main_window):
        self.view = PageFontColorView(main_window)
        self.preferences = preferences
        self.settings = settings
        self.main_window = main_window

    def init(self):
        self.update_switchers()
        self.view.style_switcher.connect('child-activated', self.on_style_switcher_changed)
        self.view.option_recolor_pdf.set_active(self.settings.get_value('preferences', 'recolor_pdf'))
        self.view.option_recolor_pdf.connect('notify::active', self.on_recolor_pdf_option_toggled)

        self.update_font_color_preview()

        source_language_manager = ServiceLocator.get_source_language_manager()
        source_language = source_language_manager.get_language('latex')
        self.view.source_buffer.set_language(source_language)
        self.update_font_color_preview()

        self.view.font = self.settings.get_value('preferences', 'font_string')
        self.view.font_label.set_label(self.settings.get_value('preferences', 'font_string'))
        self.view.option_use_system_font.set_active(self.settings.get_value('preferences', 'use_system_font'))
        self.view.option_use_system_font.connect('notify::active', self.on_use_system_font_toggled)

        self.view.font_label.connect('notify::label', self.on_font_set)

    def on_use_system_font_toggled(self, button, *args):
        self.settings.set_value('preferences', 'use_system_font', button.get_active())

    def on_recolor_pdf_option_toggled(self, button, *args):
        self.settings.set_value('preferences', 'recolor_pdf', button.get_active())

    def on_font_set(self, *args):
        fontdesc = self.view.font
        self.settings.set_value('preferences', 'font_string', fontdesc)

    def on_style_switcher_changed(self, switcher, child_widget):
        style_scheme_preview = child_widget.get_child()
        value = style_scheme_preview.get_scheme().get_name()
        if value != None:
            self.settings.set_value('preferences', 'color_scheme', value)
            self.update_font_color_preview()

    def get_scheme_id_from_file(self, pathname):
        tree = ET.parse(pathname)
        root = tree.getroot()
        return root.attrib['id']

    def update_switchers(self):
        names = ['default', 'default-dark']
        dirname = os.path.join(ServiceLocator.get_config_folder(), 'themes')
        if os.path.isdir(dirname):
            names += [self.get_scheme_id_from_file(os.path.join(dirname, file)) for file in os.listdir(dirname)]
        for name in names:
            self.view.style_switcher.add_style(name)

        active_id = self.settings.get_value('preferences', 'color_scheme')
        if active_id in names: self.view.style_switcher.select_style(active_id)
        else: self.view.style_switcher.select_style('default')

    def update_font_color_preview(self):
        source_style_scheme_manager = ServiceLocator.get_source_style_scheme_manager()
        name = self.settings.get_value('preferences', 'color_scheme')
        source_style_scheme_light = source_style_scheme_manager.get_scheme(name)
        self.view.source_buffer.set_style_scheme(source_style_scheme_light)


class PageFontColorView(Adw.PreferencesPage):

    def __init__(self, main_window):
        Adw.PreferencesPage.__init__(self)
        super(PageFontColorView, self).set_title(_('Font & Color'))
        super(PageFontColorView, self).set_icon_name('fill-tool-symbolic')
        self.main_window = main_window

        group = Adw.PreferencesGroup()

        self.source_view = GtkSource.View()
        self.source_view.get_style_context().add_class('card')
        self.source_view.get_style_context().add_class('preview-syntax')
        self.source_view.set_editable(False)
        self.source_view.set_cursor_visible(False)
        self.source_view.set_monospace(True)
        self.source_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.source_view.set_show_line_numbers(False)
        self.source_view.set_highlight_current_line(False)
        self.source_view.set_left_margin(12)
        self.source_view.set_right_margin(12)
        self.source_view.set_top_margin(12)
        self.source_view.set_bottom_margin(12)
        self.source_buffer = self.source_view.get_buffer()
        self.source_buffer.set_highlight_matching_brackets(False)
        self.source_buffer.set_text('''% Syntax highlighting preview
\\documentclass[letterpaper,11pt]{article}
\\usepackage{amsmath}
\\usepackage{amssymb}
\\begin{document}
\\section{Preview}
This is a \\textit{preview}, for $x, y \\in \\mathbb{R}: x \\leq y$ or $x > y$.
\\end{document}''')
        self.source_buffer.place_cursor(self.source_buffer.get_start_iter())
        group.add(self.source_view)

        self.add(group)

        group = Adw.PreferencesGroup()
        group.set_title(_('Font'))

        system_font = Adw.ExpanderRow()
        system_font.set_expanded(True)
        system_font.set_title(_('Use the system fixed width font'))

        self.option_use_system_font = Gtk.Switch()
        self.option_use_system_font.set_valign(Gtk.Align.CENTER)
        self.option_use_system_font.connect('notify::active', self.option_system_font_activate)
        system_font.add_suffix(self.option_use_system_font)

        system_font.connect('activate', self.system_font_activate)

        self.font_chooser_button = Adw.ActionRow()
        self.font_chooser_button.set_title(_('Editor font'))
        self.font_chooser_button.set_activatable(True)

        self.font = 'Monospace 10'
        self.connect('notify::font', self.on_font_update)

        self.font_label = Gtk.Label()
        self.font_label.set_label('Monospace 10')
        self.font_chooser_button.add_suffix(self.font_label)

        self.font_chooser_button.connect('activated', self.font_activate)
        system_font.add_row(self.font_chooser_button)

        self.system_font_row = system_font
        group.add(system_font)

        self.add(group)


        group = Adw.PreferencesGroup()
        group.set_title(_('Color Scheme'))

        self.style_switcher = StyleSwitcher()
        self.style_switcher.set_margin_start(18)
        self.style_switcher.set_margin_bottom(18)
        group.add(self.style_switcher)

        self.add(group)

        group = Adw.PreferencesGroup()
        group.set_title(_('Options'))

        self.option_recolor_pdf = Adw.SwitchRow()
        self.option_recolor_pdf.set_title(_('Show .pdf in theme colors'))
        group.add(self.option_recolor_pdf)

        self.add(group)

        self.option_system_font_activate()

    def system_font_activate(self, x, y):
        self.option_use_system_font.set_active(not self.option_use_system_font.get_active())

    def option_system_font_activate(self, *args):
        active = not self.option_use_system_font.get_active()
        self.system_font_row.set_enable_expansion(active)

    def font_activate(self, *args):
        self.font_dialog = Gtk.FontDialog()
        self.font_dialog.set_title(_('Choose a Font'))
        self.font_dialog.set_modal(True)

        fontdesc = Pango.FontDescription.from_string(self.font)

        self.font_dialog.choose_font(self.main_window, fontdesc, None, self.on_font_select_finish)

    def on_font_select_finish(self, source, res):
        fontdesc = self.font_dialog.choose_font_finish(res)

        if fontdesc.get_size() < 6 * Pango.SCALE:
            fontdesc.set_size(6 * Pango.SCALE)
        elif fontdesc.get_size() > 24 * Pango.SCALE:
            fontdesc.set_size(24 * Pango.SCALE)

        self.font = fontdesc.to_string()
        self.on_font_update()

    def on_font_update(self):
        self.font_label.set_label(self.font)

class StyleSwitcher(Gtk.FlowBox):

    def __init__(self):
        Gtk.FlowBox.__init__(self)
        self.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.set_row_spacing(6)
        self.set_activate_on_single_click(True)
        self.get_style_context().add_class('theme_previews')

        self.positions = dict()
        self.current_max = 0
        self.current_index = None

        self.connect('selected-children-changed', self.on_child_activated)


    def add_style(self, name):
        style_manager = ServiceLocator.get_source_style_scheme_manager()
        widget = GtkSource.StyleSchemePreview.new(style_manager.get_scheme(name))
        widget.get_style_context().add_class('card')
        self.append(widget)
        self.positions[name] = self.current_max
        self.current_max += 1

    def select_style(self, name):
        self.select_child(self.get_child_at_index(self.positions[name]))

    def on_child_activated(self, switcher):
        if self.current_index != None:
            self.get_child_at_index(self.current_index).get_child().set_selected(False)

        child_widget = self.get_selected_children()[0]
        name = child_widget.get_child().get_scheme().get_name()
        child_widget.get_child().set_selected(True)
        self.current_index = self.positions[name]
