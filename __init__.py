from calibre.customize import EditBookToolPlugin

class DemoPlugin(EditBookToolPlugin):
    name = 'Access Aide'
    version = (0, 1, 0)
    author = 'Luca Baffa'
    supported_platforms = ['windows', 'osx', 'linux']
    description = 'Access Aide plugin for Calibre'
    minimum_calibre_version = (1, 46, 0)
