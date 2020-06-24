import lxml.etree
import json
from PyQt5.Qt import QAction, QInputDialog

# The base class that all tools must inherit from
from calibre.gui2.tweak_book.plugin import Tool

from calibre import force_unicode
from calibre.gui2 import error_dialog, info_dialog
from calibre.ebooks.oeb.polish.container import OEB_DOCS, serialize


class AccessAide(Tool):
    name = 'access-aide'
    allowed_in_toolbar = True
    allowed_in_menu = True

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
            return error_dialog(self.gui, 'No book open',
                                'Need to have a book open first', show=True)

        # override existing attributes
        # in future releases, we could have this set via plugin preferences
        self.force_override = False

        # Stats
        self.lang_tag = 0
        self.aria_match = 0

        # get the book main language
        lang = self.get_lang(container)

        # load a map to navigate epub-types and aria roles
        self.epubtype_aria_map = self.load_json('assets/epubtype-aria-map.json')

        # load a list of extra tags
        self.extra_tags = self.load_json('assets/extra-tags.json')

        # iterate over book files
        for name, media_type in container.mime_map.items():

            # if HTML file
            if media_type in OEB_DOCS:

                # set language to <html> tags
                self.add_lang(container.parsed(name), lang)

                # add aria roles
                self.add_aria(container.parsed(name))

                container.dirty(name)

        # display info dialogue
        self.display_info()

    def load_json(self, path):
        '''
        This method loads a json file stored inside the plugin
        given its relative path
        '''

        return json.loads(get_resources(path))

    def get_lang(self, container):
        '''
        This method parses the OPF file, gets a list of the declared
        languages and returns the first one (which we trust to be the
        main language of the book)
        '''

        languages = container.opf_xpath('//dc:language/text()')

        if not languages:
            return error_dialog(self.gui, 'Access Aide',
                                'The OPF file does not report language info.',
                                show=True)

        return languages[0]

    def add_lang(self, root, lang):
        '''
        This method finds the <html> tag of the given 'root' element
        and adds language declarations.
        '''

        # get the "first" <html> tag
        html = root.xpath('//*[local-name()="html"]')[0]

        # set lang for 'lang' and 'xml:lang' attributes
        if self.write_attrib(html, 'lang', lang):

            # if successful, increment the stat counter
            self.lang_tag += 1

        if self.write_attrib(html,
                '{http://www.w3.org/XML/1998/namespace}lang', lang):

            self.lang_tag += 1

    def add_aria(self, root):
        '''
        This method finds nodes with epub style attributes
        and adds aria roles appropriately.
        '''

        # find nodes with  an 'epub:type' attribute
        nodes = root.xpath('//*[@epub:type]',
                           namespaces={'epub':'http://www.idpf.org/2007/ops'})

        # iter through nodes
        for node in nodes:

            tag = lxml.etree.QName(node).localname
            value = node.attrib['{http://www.idpf.org/2007/ops}type']

            # get map for the 'value' key
            map = self.epubtype_aria_map.get(value, None)

            # skip if the epub type is not mapped
            if map == None:

                continue

            # if the tag of the node is allowed
            # and write the aria role to the node is successful
            if (tag in map['tag'] or tag in self.extra_tags) \
               and self.write_attrib(node, 'aria', map['aria']):

                # if successful, increment the stat counter
                self.aria_match += 1

    def write_attrib(self, node, attribute, value):
        '''
        This method writes attributes to nodes.

        A preliminary check is performed, in the spirit of keeping
        changes to the original document to a minimum.
        '''

        # skip if force_override is not set and attribute is already set
        if self.force_override == False \
           and attribute in node.attrib:

            return False

        node.attrib[attribute] = value

        return True

    def display_info(self):
        '''
        This method displays an info dialogue.
        '''

        message = ('<h3>Routine completed</h3>'
                   '<p>Language attributes added: {lang_tag}<br>'
                   'Aria roles added: {aria_match}</p>') \
                   .format(**{'lang_tag': self.lang_tag,
                              'aria_match': self.aria_match})

        info_dialog(self.gui, 'Access Aide',
                    message, show=True)
