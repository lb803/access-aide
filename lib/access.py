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

class Access:
    '''
    Class to add accessibility features to xhtml files.

    The class methods aims at adding accessibility features according to the WCAG 2.0 guidelines.
    '''

    NS_XMLLANG = '{http://www.w3.org/XML/1998/namespace}lang'

    def __init__(self, document, override=False):
        self.document = document
        self.override = override

    def get_html_node(self):
        ''' Return first HTML node of the document'''

        return self.document.xpath('//*[local-name()="html"]')[0]

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
