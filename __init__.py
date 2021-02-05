from calibre.customize import EditBookToolPlugin

class AccessAidePlugin(EditBookToolPlugin):
    name = 'Access Aide'
    version = (0, 1, 5)
    author = 'Luca Baffa'
    supported_platforms = ['windows', 'osx', 'linux']
    description = 'Access Aide plugin for Calibre'
    minimum_calibre_version = (1, 46, 0)

    actual_plugin = 'calibre_plugins.access_aide.ui:AccessAidePlugin'

    def is_customizable(self):
        return True

    def config_widget(self):
        from calibre_plugins.access_aide.config import ConfigWidget
        return ConfigWidget()

    def save_settings(self, config_widget):
        config_widget.save_settings()
