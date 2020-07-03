from PyQt5.Qt import QWidget, QHBoxLayout, QCheckBox, QGroupBox, QLabel, QLineEdit
from calibre.utils.config import JSONConfig

prefs = JSONConfig('plugins/access_aide')

# Set defaults
prefs.defaults['force_override'] = False
prefs.defaults['access'] = {
    'accessibilitySummary': 'This publication conforms to WCAG 2.0 AA.'
    #'accessMode': ['textual', 'visual'],
    #'accessModeSufficient': ['textual', 'visual'],
    #'accessibilityFeature': 'structuralNavigation'
    }

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

        # Accessibility options
        access = QGroupBox(_('Accessibility'), self)
        self.l.addWidget(access)
        access_layout = QHBoxLayout()
        access.setLayout(access_layout)

        self.label = QLabel('Accessibility Summary:')
        access_layout.addWidget(self.label)

        self.msg = QLineEdit(self)
        self.msg.setText(prefs['access']['accessibilitySummary'])
        access_layout.addWidget(self.msg)
        self.label.setBuddy(self.msg)

    def save_settings(self):
        prefs['force_override'] = self.force_override.isChecked()
        prefs['access'] = {
            'accessibilitySummary': self.msg.text()
            }
