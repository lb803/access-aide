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
from os.path import abspath, dirname, join

class Access:
    '''
    Class to add accessibility features to xhtml files.

    The class methods aims at adding accessibility features according to the WCAG 2.0 guidelines.
    '''

    NS_XMLLANG = '{http://www.w3.org/XML/1998/namespace}lang'
    NS_EPUB_TYPE = '{http://www.idpf.org/2007/ops}type'

    ARIA_MAP_PATH = join(dirname(abspath(__file__)), \
                         'assets/epubtype-aria-map.json')
    EXTRA_TAGS_PATH = join(dirname(abspath(__file__)), \
                          'assets/extra-tags.json')

    def __init__(self, document, override=False):
        self.document = document
        self.override = override

        with open(self.ARIA_MAP_PATH) as f:
            self.aria_map = json.loads(f.read())

        with open(self.EXTRA_TAGS_PATH) as f:
            self.extra_tags = json.loads(f.read())

    def get_html_node(self):
        '''Return first HTML node of the document'''

        return self.document.xpath('//*[local-name()="html"]')[0]

    def get_et_nodes(self):
        '''Return HTML nodes with epub:type attribute'''

        return self.document.xpath('//*[@epub:type]',
                        namespaces={'epub': 'http://www.idpf.org/2007/ops'})

    def add_aria(self, node):
        '''Add aria roles.

        This method finds nodes with epub:type attributes
        and adds aria roles appropriately.
        Before adding the new aria role, the node tag is checked against
        a given list of possible tags and a list of allowed extra tags. Please,
        refer to the documentation in the `./assets/` folder for more on this.
        '''

        tag = lxml.etree.QName(node).localname
        values = node.attrib[self.NS_EPUB_TYPE]

        # iter over values, in case of epub:type overloading
        for value in values.split(' '):

            # get map for the 'value' key (if present)
            map = self.aria_map.get(value, False)

            if map and (tag in map['tag'] or tag in self.extra_tags):

                # EXCEPTIONS
                # skip if <img> doesn't have alt text
                if tag == 'img' and not node.get('alt'):
                    continue

                # skip if <a> is not in map and has href value
                if tag == 'a' and \
                   (tag not in map['tag'] and node.get('href')):
                    continue

                if self.write_attrib(node, 'role', map['aria']):
                    return True

    def write_attrib(self, node, attribute, value):
        '''Write attributes to nodes.

        Attributes are written if config has 'force_override' set
        or if node is not present. True is returned to flag success,
        otherwise False.
        '''

        if self.override or attribute not in node.attrib:
            node.attrib[attribute] = value
            return True

        return False
