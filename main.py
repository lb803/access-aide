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
from lib.stats import Stats

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

        # Stat counters
        self.lang_tag = Stats()
        self.aria_match = Stats()
        self.meta_decl = Stats()

        # get the book main language
        lang = self.get_lang(container)

        # load a map to navigate epub-types and aria roles
        self.epubtype_aria_map = self.load_json('assets/epubtype-aria-map.json')

        # load a list of extra tags
        self.extra_tags = self.load_json('assets/extra-tags.json')

        # add metadata to OPF file
        self.add_metadata(container)

        # list of files to ignore
        blacklist = ['toc.xhtml']

        # iterate over book files
        for name, media_type in container.mime_map.items():

            # if HTML file
            if media_type in OEB_DOCS and name not in blacklist:

                # set language to <html> tags
                self.add_lang(container.parsed(name), lang)

                # add aria roles
                self.add_aria(container.parsed(name))

                container.dirty(name)

        # display info dialogue
        self.display_info()

    def load_json(self, path):
        '''Load a JSON file.

        This method loads a json file stored inside the plugin
        given its relative path. The method returns a python object.
        '''

        return json.loads(get_resources(path))

    def get_lang(self, container):
        '''Retrieve book main language.

        This method parses the OPF file, gets a list of the declared
        languages and returns the first one (which we trust to be the
        main language of the book).
        '''

        languages = container.opf_xpath('//dc:language/text()')

        if not languages:
            return error_dialog(self.gui, 'Access Aide',
                                'The OPF file does not report language info.',
                                show=True)

        return languages[0]

    def add_lang(self, root, lang):
        '''Add language attributes to <html> tags.

        This method finds the <html> tag of the given 'root' element
        and adds language declarations. Changes are tracked and successes
        increase a stat counter.
        '''

        html = root.xpath('//*[local-name()="html"]')[0]

        # set lang for 'lang' attribute
        if self.write_attrib(html, 'lang', lang):

            self.lang_tag.increase()

        # set lang for 'xml:lang' attribute
        if self.write_attrib(html,
                '{http://www.w3.org/XML/1998/namespace}lang', lang):

            self.lang_tag.increase()

    def add_aria(self, root):
        '''Add aria roles.

        This method finds nodes with epub:type attributes
        and adds aria roles appropriately.
        Before adding the new aria role, the node tag is checked against
        a given list of possible tags and a list of allowed extra tags. Please,
        refer to the documentation in the `./assets/` folder for more on this.
        '''

        # find nodes with  an 'epub:type' attribute
        nodes = root.xpath('//*[@epub:type]',
                           namespaces={'epub':'http://www.idpf.org/2007/ops'})

        for node in nodes:

            tag = lxml.etree.QName(node).localname
            value = node.attrib['{http://www.idpf.org/2007/ops}type']

            # get map for the 'value' key
            map = self.epubtype_aria_map.get(value, None)

            # skip if the epub type is not mapped
            if map == None:

                continue

            # if the tag on 'node' is allowed
            if tag in map['tag'] or tag in self.extra_tags:

                if self.write_attrib(node, 'role', map['aria']):

                    self.aria_match.increase()

    def write_attrib(self, node, attribute, value):
        '''Write attributes to nodes.

        A preliminary check is performed, in the spirit of keeping
        changes to the original document to a minimum.
        '''

        # skip if force_override is not set and attribute is already set
        if prefs['force_override'] == False \
           and attribute in node.attrib:

            return False

        node.attrib[attribute] = value

        return True

    def display_info(self):
        '''Display an info dialogue.

        This method composes and shows an info dialogue to display at the end of
        runtime along with some statistics.
        '''

        message = ('<h3>Routine completed</h3>'
                   '<p>Language attributes added: {lang_tag}<br>'
                   'Aria roles added: {aria_match}<br>'
                   'Metadata declarations added: {meta_decl}</p>') \
                   .format(**{'lang_tag': self.lang_tag.get(),
                              'aria_match': self.aria_match.get(),
                              'meta_decl': self.meta_decl.get()})

        info_dialog(self.gui, 'Access Aide',
                    message, show=True)

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
                if '3.' in container.opf_version:

                    # prevent overriding
                    if prefs['force_override'] == False \
                       and container.opf_xpath('//*[contains(@property, "{}")]'\
                                               .format(value)):

                        continue

                    element = lxml.etree.Element('meta')
                    element.set('property', ('schema:' + value))
                    element.text = text

                    self.meta_decl.increase()

                # if epub2
                elif '2.' in container.opf_version:

                    # prevent overriding
                    if prefs['force_override'] == False \
                       and container.opf_xpath('//*[contains(@name, "{}")]' \
                                               .format(value)):

                        continue

                    element = lxml.etree.Element('meta')
                    element.set('name', ('schema:' + value))
                    element.set('content', text)

                    self.meta_decl.increase()

                else:

                    return

                container.insert_into_xml(metadata, element)

            container.dirty(container.opf_name)
