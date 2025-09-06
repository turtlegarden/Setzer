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
gi.require_version('Xdp', '1.0')
from gi.repository import Gtk, Xdp, Adw
from setzer.widgets.radio_row.radio_row import RadioRow

import subprocess, os


class PageBuildSystem(object):

    def __init__(self, preferences, settings):
        self.view = PageBuildSystemView()
        self.preferences = preferences
        self.settings = settings
        self.latex_interpreters = list()
        self.latexmk_available = False

    def init(self):
        self.view.option_cleanup_build_files.set_active(self.settings.get_value('preferences', 'cleanup_build_files'))
        self.view.option_cleanup_build_files.connect('notify::active', self.preferences.on_check_button_toggle, 'cleanup_build_files')

        self.view.option_autoshow_build_log_errors.button.set_active(self.settings.get_value('preferences', 'autoshow_build_log') == 'errors')
        self.view.option_autoshow_build_log_errors_warnings.button.set_active(self.settings.get_value('preferences', 'autoshow_build_log') == 'errors_warnings')
        self.view.option_autoshow_build_log_all.button.set_active(self.settings.get_value('preferences', 'autoshow_build_log') == 'all')

        self.view.option_autoshow_build_log_errors.button.connect('notify::active', self.preferences.on_radio_button_toggle, 'autoshow_build_log', 'errors')
        self.view.option_autoshow_build_log_errors_warnings.button.connect('notify::active', self.preferences.on_radio_button_toggle, 'autoshow_build_log', 'errors_warnings')
        self.view.option_autoshow_build_log_all.button.connect('notify::active', self.preferences.on_radio_button_toggle, 'autoshow_build_log', 'all')

        self.view.option_system_commands_disable.button.set_active(self.settings.get_value('preferences', 'build_option_system_commands') == 'disable')
        self.view.option_system_commands_restricted.button.set_active(self.settings.get_value('preferences', 'build_option_system_commands') == 'restricted')
        self.view.option_system_commands_full.button.set_active(self.settings.get_value('preferences', 'build_option_system_commands') == 'enable')

        self.view.option_system_commands_disable.button.connect('notify::active', self.preferences.on_radio_button_toggle, 'build_option_system_commands', 'disable')
        self.view.option_system_commands_restricted.button.connect('notify::active', self.preferences.on_radio_button_toggle, 'build_option_system_commands', 'restricted')
        self.view.option_system_commands_full.button.connect('notify::active', self.preferences.on_radio_button_toggle, 'build_option_system_commands', 'enable')

        self.setup_latex_interpreters()

    def setup_latex_interpreters(self):
        self.latex_interpreters = list()
        for interpreter in ['xelatex', 'pdflatex', 'lualatex', 'tectonic']:
            self.view.option_latex_interpreter[interpreter].set_visible(False)
            arguments = [interpreter, '--version']
            try:
                process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except FileNotFoundError:
                pass
            else:
                process.wait()
                if process.returncode == 0:
                    self.latex_interpreters.append(interpreter)

        self.latexmk_available = False
        arguments = ['latexmk', '--version']
        try:
            process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except FileNotFoundError:
            pass
        else:
            process.wait()
            if process.returncode == 0:
                self.latexmk_available = True

        if len(self.latex_interpreters) == 0:
            self.view.no_interpreter_label.set_visible(True)
        else:
            self.view.no_interpreter_label.set_visible(False)
            if self.settings.get_value('preferences', 'latex_interpreter') not in self.latex_interpreters:
                self.settings.set_value('preferences', 'latex_interpreter', self.latex_interpreters[0])

            if self.latexmk_available:
                self.view.option_use_latexmk.set_visible(True)
            else:
                self.view.option_use_latexmk.set_visible(False)
                self.settings.set_value('preferences', 'use_latexmk', False)
            self.view.option_use_latexmk.set_active(self.settings.get_value('preferences', 'use_latexmk'))
            self.view.option_use_latexmk.connect('notify::active', self.preferences.on_check_button_toggle, 'use_latexmk')

            for interpreter in self.view.option_latex_interpreter:
                if interpreter in self.latex_interpreters:
                    self.view.option_latex_interpreter[interpreter].set_visible(True)
                    self.view.option_latex_interpreter[interpreter].button.set_active(interpreter == self.settings.get_value('preferences', 'latex_interpreter'))
                    self.view.option_latex_interpreter[interpreter].button.connect('notify::active', self.preferences.on_interpreter_changed, 'latex_interpreter', interpreter)
                else:
                    self.view.option_latex_interpreter[interpreter].set_visible(False)

            self.view.option_latex_interpreter['tectonic'].button.connect('notify::active', self.on_use_tectonic_active)
        self.update_tectonic_element_visibility()

    def on_use_tectonic_active(self, button):
        self.update_tectonic_element_visibility()

    def update_tectonic_element_visibility(self):
        if 'tectonic' in self.latex_interpreters and self.view.option_latex_interpreter['tectonic'].button.get_active():
            self.view.option_use_latexmk.set_visible(False)
            self.view.shell_escape_box.set_visible(False)
        else:
            self.view.option_use_latexmk.set_visible(True)
            self.view.shell_escape_box.set_visible(True)

class PageBuildSystemView(Adw.PreferencesPage):

    def __init__(self):
        Adw.PreferencesPage.__init__(self)
        super(PageBuildSystemView, self).set_title(_('Build System'))
        super(PageBuildSystemView, self).set_icon_name('builder-build-symbolic')

        group = Adw.PreferencesGroup()
        group.set_title(_('LaTeX Interpreter'))

        self.no_interpreter_label = Adw.ActionRow()
        self.no_interpreter_label.set_selectable(False)
        self.no_interpreter_label.set_use_markup(True)
        if Xdp.Portal().running_under_flatpak():
            self.no_interpreter_label.set_title(_('''No LaTeX interpreter found. To install interpreters in Flatpak, open a terminal and run the following command:
flatpak install org.freedesktop.Sdk.Extension.texlive'''))
        else:
            self.no_interpreter_label.set_title(_('No LaTeX interpreter found. For instructions on installing LaTeX see <a href="https://en.wikibooks.org/wiki/LaTeX/Installation">https://en.wikibooks.org/wiki/LaTeX/Installation</a>'))

        group.add(self.no_interpreter_label)

        self.option_latex_interpreter = dict()
        self.option_latex_interpreter['xelatex'] = RadioRow('XeLaTeX')
        buttongroup = self.option_latex_interpreter['xelatex'].button
        #self.option_latex_interpreter['xelatex'].update_group(buttongroup)
        self.option_latex_interpreter['pdflatex'] = RadioRow('PDFLaTeX', buttongroup)
        self.option_latex_interpreter['lualatex'] = RadioRow('LuaLaTeX', buttongroup)
        self.option_latex_interpreter['tectonic'] = RadioRow('Tectonic', buttongroup)
        self.option_latex_interpreter['tectonic'].set_description(_('Please note: the Tectonic backend uses only the V1 command-line interface. Tectonic.toml configuration files are ignored.'))

        group.add(self.option_latex_interpreter['xelatex'])
        group.add(self.option_latex_interpreter['pdflatex'])
        group.add(self.option_latex_interpreter['lualatex'])
        group.add(self.option_latex_interpreter['tectonic'])

        self.add(group)


        group = Adw.PreferencesGroup()
        group.set_title(_('Options'))

        self.option_cleanup_build_files = Adw.SwitchRow()
        self.option_cleanup_build_files.set_title(_('Automatically remove helper files (.log, .dvi, …) after building .pdf'))
        group.add(self.option_cleanup_build_files)

        self.option_use_latexmk = Adw.SwitchRow()
        self.option_use_latexmk.set_title(_('Use Latexmk'))
        group.add(self.option_use_latexmk)

        self.add(group)


        group = Adw.PreferencesGroup()
        group.set_title(_('Automatically show build log ..'))

        self.option_autoshow_build_log_errors = RadioRow(_('.. only when errors occurred.'))
        buttongroup = self.option_autoshow_build_log_errors.button
        #self.option_autoshow_build_log_errors.update_group(buttongroup)
        self.option_autoshow_build_log_errors_warnings = RadioRow(_('.. on errors and warnings.'), buttongroup)
        self.option_autoshow_build_log_all = RadioRow(_('.. on errors, warnings and badboxes.'), buttongroup)

        group.add(self.option_autoshow_build_log_errors)
        group.add(self.option_autoshow_build_log_errors_warnings)
        group.add(self.option_autoshow_build_log_all)

        self.add(group)

        label_header = Gtk.Label()
        label_header.set_markup('<b>' + _('Embedded system commands') + '</b>')
        label_header.set_xalign(0)
        label_header.set_margin_top(18)
        label_header.set_margin_bottom(6)

        group = Adw.PreferencesGroup()
        group.set_title(_('Embedded system commands'))
        group.set_description(_('Warning: enable this only if you have to. It can cause security problems when building files from untrusted sources.'))

        self.option_system_commands_disable = RadioRow((_('Disable') + ' (' + _('recommended') + ')'))
        buttongroup = self.option_system_commands_disable.button
        #self.option_system_commands_disable.update_group(buttongroup)
        self.option_system_commands_restricted = RadioRow(_('Enable restricted \\write18{SHELL COMMAND}'), buttongroup)
        self.option_system_commands_full = RadioRow(_('Fully enable \\write18{SHELL COMMAND}'), buttongroup)
        group.add(self.option_system_commands_disable)
        group.add(self.option_system_commands_restricted)
        group.add(self.option_system_commands_full)

        self.shell_escape_box = group

        self.add(self.shell_escape_box)
