import lxml.etree
from PyQt5.Qt import QAction, QInputDialog

# The base class that all tools must inherit from
from calibre.gui2.tweak_book.plugin import Tool

from calibre import force_unicode
from calibre.gui2 import error_dialog
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

        # get the book main language
        lang = self.get_lang(container)
        
        # iterate over book files
        for name, media_type in container.mime_map.items():

            # if HTML file
            if media_type in OEB_DOCS:

                # set language to <html> tags
                self.add_lang(container.parsed(name), lang)

                container.dirty(name)

    def get_lang(self, container):
        '''
        This method parses the OPF file, gets a list of the declared
        languages and returns the first one (which we trust to be the
        main language of the book)
        '''

        languages = container.opf_xpath('//dc:language/text()')

        if not languages:
            return error_dialog(self.gui, 'No language declaration for book',
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
        html.attrib['lang'] = lang
        html.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = lang
