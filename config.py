from PyQt5.Qt import QWidget, QHBoxLayout, QCheckBox, QGroupBox
from calibre.utils.config import JSONConfig

prefs = JSONConfig('plugins/access_aide')

# Set defaults
prefs.defaults['force_override'] = False


class ConfigWidget(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.l = QHBoxLayout()
        self.setLayout(self.l)

        # Plugin options
        options = QGroupBox(_('Options'), self)
        self.l.addWidget(options)
        options_layout = QHBoxLayout()
        options.setLayout(options_layout)

        self.force_override = QCheckBox('&'+_('Force Override'), self)
        self.force_override.setToolTip(_('When checked, existing attributes and value will be overwritten.'))
        options_layout.addWidget(self.force_override)
        self.force_override.setChecked(prefs['force_override'])

    def save_settings(self):
        prefs['force_override'] = self.force_override.isChecked()
