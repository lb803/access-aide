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
from calibre.ebooks.oeb.polish.container import OEB_DOCS

from calibre_plugins.access_aide.config import prefs

# My modules
from .lib.stats import Stats


class AccessAide(Tool):
    name = 'access-aide'
    allowed_in_toolbar = True
    allowed_in_menu = True

    def __init__(self):

        # init stat counters
        self.lang_stat = Stats()  # language tags
        self.aria_stat = Stats()  # aria roles matches
        self.meta_stat = Stats()  # metadata declarations

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
            message = 'No book open, you need to have a book open first.'

            return error_dialog(self.gui, 'Access Aide', message, show=True)

        if container.book_type != 'epub':
            message = 'Access Aide supports EPUB files only, {} given.' \
                      .format(container.book_type)

            return error_dialog(self.gui, 'Access Aide', message, show=True)

        # get book main language
        try:
            lang = container.opf_xpath('//dc:language/text()')[0]
        except IndexError:
            message = 'The OPF file does not report language info.'

            return error_dialog(self.gui, 'Access Aide', message, show=True)

        self.add_metadata(container)

        blacklist = ['toc.xhtml']

        # iterate over book files
        for name, media_type in list(container.mime_map.items()):

            if media_type in OEB_DOCS \
               and name not in blacklist:

                self.add_lang(container.parsed(name), lang)
                self.add_aria(container.parsed(name))

                container.dirty(name)

        info_dialog(self.gui, 'Access Aide', self.stats_report(), show=True)

        self.lang_stat.reset()
        self.aria_stat.reset()
        self.meta_stat.reset()

        # update the editor UI
        self.boss.apply_container_update_to_gui()

    def add_lang(self, root, lang):
        '''Add language attributes to <html> tags.

        This method finds the <html> tag of the given 'root' element
        and adds language declarations. Changes are tracked and successes
        increase a stat counter.
        '''

        html = root.xpath('//*[local-name()="html"]')[0]

        # set lang for 'lang' attribute
        self.write_attrib(html, 'lang', lang, self.lang_stat)

        # set lang for 'xml:lang' attribute
        self.write_attrib(html, '{http://www.w3.org/XML/1998/namespace}lang',
                          lang, self.lang_stat)

    def add_aria(self, root):
        '''Add aria roles.

        This method finds nodes with epub:type attributes
        and adds aria roles appropriately.
        Before adding the new aria role, the node tag is checked against
        a given list of possible tags and a list of allowed extra tags. Please,
        refer to the documentation in the `./assets/` folder for more on this.
        '''

        # load maps
        epubtype_aria_map = json.loads(
                              get_resources('assets/epubtype-aria-map.json'))
        extra_tags = json.loads(get_resources('assets/extra-tags.json'))

        # find nodes with  an 'epub:type' attribute
        nodes = root.xpath('//*[@epub:type]',
                           namespaces={'epub': 'http://www.idpf.org/2007/ops'})

        for node in nodes:

            tag = lxml.etree.QName(node).localname
            values = node.attrib['{http://www.idpf.org/2007/ops}type']

            # iter over values, in case of epub:type overloading
            for value in values.split(' '):

                # get map for the 'value' key (if present)
                map = epubtype_aria_map.get(value, False)

                if map and (tag in map['tag'] or tag in extra_tags):

                    # EXCEPTIONS
                    # skip if <img> doesn't have alt text
                    if tag == 'img' and not node.get('alt'):
                        continue

                    # skip if <a> is not in map and has href value
                    if tag == 'a' and \
                       (tag not in map['tag'] and node.get('href')):
                        continue

                    self.write_attrib(node, 'role', map['aria'], self.aria_stat)

    def write_attrib(self, node, attribute, value, stat):
        '''Write attributes to nodes.

        Attributes are written if config has 'force_override' set
        or if node is not present.
        '''

        if prefs['force_override'] \
           or attribute not in node.attrib:

            node.attrib[attribute] = value
            stat.increase()

        return

    def stats_report(self):
        '''Compose a short report on stats.

        This method returns a string to display at the end of
        runtime along with some statistics.
        '''

        template = ('<h3>Routine completed</h3>'
                    '<p>Language attributes added: {lang_stat}<br>'
                    'Aria roles added: {aria_stat}<br>'
                    'Metadata declarations added: {meta_stat}</p>')

        data = {'lang_stat': self.lang_stat.get(),
                'aria_stat': self.aria_stat.get(),
                'meta_stat': self.meta_stat.get()}

        return template.format(**data)

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

                else:
                    # metadata currently available only for EPUB v2 and v3
                    return

            container.dirty(container.opf_name)
