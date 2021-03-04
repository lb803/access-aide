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

import lxml.etree
import json
from PyQt5.Qt import QAction

# The base class that all tools must inherit from
from calibre.gui2.tweak_book.plugin import Tool

from calibre import force_unicode
from calibre.gui2 import error_dialog, info_dialog
from calibre.ebooks.oeb.base import OPF_MIME, OEB_DOCS

from calibre_plugins.access_aide.config import prefs

# My modules
from .lib.stats import Stats
from .lib.access import Access


class AccessAide(Tool):
    name = 'access-aide'
    allowed_in_toolbar = True
    allowed_in_menu = True

    def __init__(self):

        # init stat counters
        self.lang_stat = Stats(desc='Language attributes')
        self.aria_stat = Stats(desc='Aria roles')
        self.meta_stat = Stats(desc='Metadata declarations')

    def create_action(self, for_toolbar=True):
        ac = QAction(get_icons('icon/icon.png'), 'Access Aide', self.gui)

        if not for_toolbar:
            self.register_shortcut(ac, 'access-aide-tool',
                                   default_keys=('Ctrl+Shift+A',))

        ac.triggered.connect(self.main)
        return ac

    def main(self):
        # create a restore point
        self.boss.add_savepoint('Before: Access Aide')

        container = self.current_container

        if not container:
            return error_dialog(self.gui, 'Access Aide',
                                'No book open, please open a book first.',
                                show=True)

        if container.book_type != 'epub' or \
           container.opf_version_parsed.major not in [2, 3]:
            message = 'Access Aide supports EPUB 2 and 3, {} {} given.' \
                      .format(container.book_type.upper(),
                              container.opf_version_parsed.major)

            return error_dialog(self.gui, 'Access Aide', message, show=True)

        lang = self.get_lang(container)

        blacklist = ['toc.xhtml']

        # iterate over book files
        for name, media_type in list(container.mime_map.items()):

            if media_type in OEB_DOCS \
               and name not in blacklist:

                doc = Access(container.parsed(name),
                             override=prefs['force_override'])

                # add language declarations
                html_node = doc.get_html_node()

                if doc.write_attrib(html_node, 'lang', lang):
                    self.lang_stat.increase()

                if doc.write_attrib(html_node, doc.NS_XMLLANG, lang):
                    self.lang_stat.increase()

                # add aria roles
                et_nodes = doc.get_et_nodes()

                for node in et_nodes:
                    if doc.add_aria(node):
                        self.aria_stat.increase()

            elif media_type in OPF_MIME:
                self.add_metadata(container)

            else:
                continue

            container.dirty(name)

        info_dialog(self.gui, 'Access Aide', self.stats_report(), show=True)

        self.lang_stat.reset()
        self.aria_stat.reset()
        self.meta_stat.reset()

        # update the editor UI
        self.boss.apply_container_update_to_gui()

    def get_lang(self, container):
        '''Retrieve book main language.
        This method parses the OPF file, gets a list of the declared
        languages and returns the first one (which we trust to be the
        main language of the book).
        '''

        try:
            lang = container.opf_xpath('//dc:language/text()')[0]
        except IndexError:
            message = 'The OPF file does not report language info.'

            return error_dialog(self.gui, 'Access Aide', message, show=True)

        return lang

    def stats_report(self):
        '''Compose a short report on stats.

        This method returns a string to display at the end of
        runtime along with some statistics.
        '''

        data = [self.lang_stat.report(),
                self.aria_stat.report(),
                self.meta_stat.report()]

        return '<h3>Routine completed</h3><p>{}</p>'.format('<br>'.join(data))


    def add_metadata(self, container):
        ''' Add metadata to OPF file.

        This method looks up the config file and add appropriate metadata for
        the volume.
        '''

        metadata = container.opf_xpath('//opf:metadata')[0]

        meta = prefs['access']

        for value in meta:

            for text in meta[value]:

                # if epub3
                if container.opf_version_parsed.major == 3:

                    # prevent overriding
                    if prefs['force_override'] \
                       or not container.opf_xpath(
                           '''
                           //*[contains(@property, "{}")
                               and contains(text(), "{}")]
                           '''.format(value, text)):

                        element = lxml.etree.Element('meta')
                        element.set('property', ('schema:' + value))
                        element.text = text

                        container.insert_into_xml(metadata, element)

                        self.meta_stat.increase()

                # if epub2
                elif container.opf_version_parsed.major == 2:

                    # prevent overriding
                    if prefs['force_override'] \
                       or not container.opf_xpath(
                           '''
                           //*[contains(@name, "{}")
                               and contains(@content, "{}")]
                           '''.format(value, text)):

                        element = lxml.etree.Element('meta')
                        element.set('name', ('schema:' + value))
                        element.set('content', text)

                        container.insert_into_xml(metadata, element)

                        self.meta_stat.increase()
