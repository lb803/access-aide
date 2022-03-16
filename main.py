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


class AccessAide(Tool):
    name = 'access-aide'
    allowed_in_toolbar = True
    allowed_in_menu = True

    def __init__(self):

        # init stat counters
        self.lang_stat = Stats(desc='Language attributes')
        self.aria_stat = Stats(desc='Aria roles')
        self.meta_stat = Stats(desc='Metadata declarations')
        self.title_stat = Stats(desc='Text content of &lt;title&gt; tags')
        self.fn_stat = Stats(desc='epub:type to footnote and endnote marks')

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

        blacklist = ['toc.xhtml']

        # iterate over book files
        for name, media_type in list(container.mime_map.items()):

            if media_type in OEB_DOCS \
               and name not in blacklist:

                if prefs.get('heuristic', {}).get('title_override'):
                    self.override_title(container.parsed(name))
                if prefs.get('heuristic', {}).get('type_footnotes'):
                    self.add_fn_type(container.parsed(name))

                self.add_lang(container.parsed(name),
                              self.get_lang(container))
                self.add_aria(container.parsed(name))

            elif media_type in OPF_MIME:
                self.add_metadata(container)

                if prefs.get('a11y', {}).get('enabled'):
                    self.add_a11y(container)

            else:
                continue

            container.dirty(name)

        info_dialog(self.gui, 'Access Aide', self.stats_report(), show=True)

        self.lang_stat.reset()
        self.aria_stat.reset()
        self.meta_stat.reset()
        self.title_stat.reset()
        self.fn_stat.reset()

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

    def override_title(self, root):
        '''Replace the text content of the <title> tag with the one of <h1>

        This method finds the first <h1> tag of the given 'root' element
        and override the text of <title> in the header.
        Changes are tracked and successes increase a stat counter.
        '''

        try:
            title = root.xpath('//*[local-name()="title"]')[0]
            h1 = root.xpath('//*[local-name()="h1"]')[0]
        except IndexError:
            return

        h1_text = ''.join(h1.itertext())

        self.write_text(title, h1_text, self.title_stat)

    def add_fn_type(self, root):
        '''Add epub:role to footnote markers and references

        This method finds footnote markers and references on the page
        and adds the corresponding epub:type(s). Hardcoded class values
        to find fn markers and references assume the book has been produced
        with InDesign.
        Changes are tracked and successes increase a stat counter.
        '''

        fn_markers_xpath = '//*[contains(@class, "_idFootnoteLink") or ' \
                               'contains(@class, "_idEndnoteLink")]'
        for fn_marker in root.xpath(fn_markers_xpath):
            self.write_attrib(fn_marker, '{http://www.idpf.org/2007/ops}type',
                              'noteref', self.fn_stat)

        fn_backlink_xpath = '//*[contains(@class, "_idFootnoteAnchor") or ' \
                                'contains(@class, "_idEndnoteAnchor")]'
        for fn_backlink in root.xpath(fn_backlink_xpath):
            self.write_attrib(fn_backlink, 'role',
                              'doc-backlink', self.aria_stat)

    def write_attrib(self, node, attribute, value, stat):
        '''Write attributes to nodes.

        Attributes are written if config has 'force_override' set
        or if node is not present.
        '''

        if prefs.get('force_override') \
           or attribute not in node.attrib:

            node.attrib[attribute] = value
            if stat:
                stat.increase()

        return

    def write_text(self, node, value, stat):
        '''Write text to nodes.

        Text is written if config has 'force_override' set
        or if node text differs.
        '''

        if prefs.get('force_override') \
           or ''.join(node.itertext()) != value:

            node.text = value
            if stat:
                stat.increase()

        return

    def stats_report(self):
        '''Compose a short report on stats.

        This method returns a string to display at the end of
        runtime along with some statistics.
        '''

        data = [self.lang_stat.report(),
                self.aria_stat.report(),
                self.meta_stat.report()]

        if prefs.get('heuristic', {}).get('title_override'):
            data.append(self.title_stat.report())
        if prefs.get('heuristic', {}).get('type_footnotes'):
            data.append(self.fn_stat.report())

        return '<h3>Routine completed</h3><p>{}</p>'.format('<br>'.join(data))


    def add_metadata(self, container):
        ''' Add metadata to OPF file.

        This method looks up the config file and add appropriate metadata for
        the volume.
        '''

        metadata = container.opf_xpath('//opf:metadata')[0]

        meta = prefs.get('access')

        for value in meta:

            for text in meta[value]:

                # if epub3
                if container.opf_version_parsed.major == 3:

                    # prevent overriding
                    if prefs.get('force_override') \
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
                    if prefs.get('force_override') \
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

    def add_a11y(self, container):
        ''' Add a11y metadata to OPF file.

        This method looks up the config file and add appropriate metadata for
        the volume.
        '''
        metadata = container.opf_xpath('//opf:metadata')[0]

        conforms_to = prefs.get('dcterms', {}).get('conformsTo')
        if conforms_to:
            # if epub3
            if container.opf_version_parsed.major == 3:

                # prevent overriding
                if prefs.get('force_override') \
                   or not container.opf_xpath('//*[contains(@rel, "{}")]'
                                              .format('dcterms:conformsTo')):

                        element = lxml.etree.Element('link')
                        self.write_attrib(element, 'rel',
                                          'dcterms:conformsTo', self.meta_stat)
                        self.write_attrib(element, 'href', conforms_to, None)

                        container.insert_into_xml(metadata, element)

            # if epub2
            elif container.opf_version_parsed.major == 2:

                # prevent overriding
                if prefs.get('force_override') \
                   or not container.opf_xpath('//*[contains(@name, "{}")]'
                                              .format('dcterms:conformsTo')):

                    element = lxml.etree.Element('meta')
                    self.write_attrib(element, 'name',
                                      'dcterms:conformsTo', self.meta_stat)
                    self.write_attrib(element, 'content', conforms_to, None)

                    container.insert_into_xml(metadata, element)

        certifiedBy = prefs.get('a11y', {}).get('certifiedBy')
        if certifiedBy:
            # if epub3
            if container.opf_version_parsed.major == 3:

                # prevent overriding
                if prefs.get('force_override') \
                   or not container.opf_xpath('//*[contains(@property, "{}")]'
                                              .format('a11y:certifiedBy')):

                        element = lxml.etree.Element('meta')
                        self.write_attrib(element, 'property',
                                          'a11y:certifiedBy', self.meta_stat)
                        self.write_text(element, certifiedBy, None)

                        container.insert_into_xml(metadata, element)
            # if epub2
            elif container.opf_version_parsed.major == 2:

                # prevent overriding
                if prefs.get('force_override') \
                   or not container.opf_xpath('//*[contains(@name, "{}")]'
                                              .format('a11y:certifiedBy')):

                    element = lxml.etree.Element('meta')
                    self.write_attrib(element, 'name',
                                      'a11y:certifiedBy', self.meta_stat)
                    self.write_attrib(element, 'content',
                                      certifiedBy, None)

                    container.insert_into_xml(metadata, element)

        certifierCred = prefs.get('a11y', {}).get('certifierCredential')
        if certifierCred:
            # if epub3
            if container.opf_version_parsed.major == 3:

                # prevent overriding
                if prefs.get('force_override') \
                   or not container.opf_xpath('//*[contains(@property, "{}")]'
                                         .format('a11y:certifierCredential')):

                        element = lxml.etree.Element('meta')
                        self.write_attrib(element, 'property',
                                          'a11y:certifierCredential',
                                          self.meta_stat)
                        self.write_text(element, certifierCred, None)

                        container.insert_into_xml(metadata, element)

            # if epub2
            elif container.opf_version_parsed.major == 2:

                # prevent overriding
                if prefs.get('force_override') \
                   or not container.opf_xpath('//*[contains(@name, "{}")]'
                                        .format('a11y:certifierCredential')):

                    element = lxml.etree.Element('meta')
                    self.write_attrib(element, 'name',
                                      'a11y:certifierCredential',
                                      self.meta_stat)
                    self.write_attrib(element, 'content', certifierCred, None)

                    container.insert_into_xml(metadata, element)

        certifierRep = prefs.get('a11y', {}).get('certifierReport')
        if certifierRep:
            # if epub3
            if container.opf_version_parsed.major == 3:

                # prevent overriding
                if prefs.get('force_override') \
                   or not container.opf_xpath('//*[contains(@rel, "{}")]'
                                              .format('a11y:certifierReport')):

                        element = lxml.etree.Element('link')
                        self.write_attrib(element, 'rel',
                                          'a11y:certifierReport',
                                          self.meta_stat)
                        self.write_attrib(element, 'href', certifierRep, None)

                        container.insert_into_xml(metadata, element)

            # if epub2
            elif container.opf_version_parsed.major == 2:

                # prevent overriding
                if prefs.get('force_override') \
                   or not container.opf_xpath('//*[contains(@name, "{}")]'
                                        .format('a11y:certifierReport')):

                    element = lxml.etree.Element('meta')
                    self.write_attrib(element, 'name', 'a11y:certifierReport',
                                      self.meta_stat)
                    self.write_attrib(element, 'content', certifierRep, None)

                    container.insert_into_xml(metadata, element)
