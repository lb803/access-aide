#!/usr/bin/env python3
'''
Access Aide - A Calibre plugin to enhance accessibility features in epub files.
Copyright (C) 2020-2021 Luca Baffa

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from calibre.customize import EditBookToolPlugin

class AccessAidePlugin(EditBookToolPlugin):
    name = 'Access Aide'
    version = (0, 1, 15)
    author = 'Luca Baffa'
    supported_platforms = ['windows', 'osx', 'linux']
    description = 'Enhance accessibility features in EPUB files.'
    minimum_calibre_version = (1, 46, 0)

    actual_plugin = 'calibre_plugins.access_aide.ui:AccessAidePlugin'

    def is_customizable(self):
        return True

    def config_widget(self):
        from calibre_plugins.access_aide.config import ConfigWidget
        return ConfigWidget()

    def save_settings(self, config_widget):
        config_widget.save_settings()
