from PyQt5.Qt import QWidget, QHBoxLayout, QVBoxLayout, QCheckBox, QGroupBox, QLabel, QLineEdit, QRadioButton
from calibre.utils.config import JSONConfig

prefs = JSONConfig('plugins/access_aide')

# Set defaults
prefs.defaults['force_override'] = False
prefs.defaults['access'] = {
    'accessibilitySummary': 'This publication conforms to WCAG 2.0 AA.',
    'accessMode': ['textual', 'visual'],
    'accessModeSufficient': 'textual'
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
        access_layout = QVBoxLayout()
        access.setLayout(access_layout)

        # accessibilitySummary
        self.label = QLabel('Accessibility Summary:')
        access_layout.addWidget(self.label)

        self.msg = QLineEdit(self)
        self.msg.setText(prefs['access']['accessibilitySummary'])
        access_layout.addWidget(self.msg)
        self.label.setBuddy(self.msg)

        # accessMode
        self.label2 = QLabel('Access Mode:')
        access_layout.addWidget(self.label2)

        self.acc_mode_t = QCheckBox('&'+_('Textual'), self)
        access_layout.addWidget(self.acc_mode_t)
        if 'textual' in prefs['access']['accessMode']:
            self.acc_mode_t.setChecked(True)
        else:
            self.acc_mode_t.setChecked(False)

        self.acc_mode_v = QCheckBox('&'+_('Visual'), self)
        access_layout.addWidget(self.acc_mode_v)

        if 'visual' in prefs['access']['accessMode']:
            self.acc_mode_v.setChecked(True)

        else:
            self.acc_mode_v.setChecked(False)

        # accessModeSufficient
        self.label3 = QLabel('Access Mode Sufficient:')
        access_layout.addWidget(self.label3)

        self.acc_suff_t = QRadioButton('Textual')

        if 'textual' in prefs['access']['accessModeSufficient']:
            self.acc_suff_t.setChecked(True)

        access_layout.addWidget(self.acc_suff_t)

        self.acc_suff_v = QRadioButton('Visual')

        if 'visual' in prefs['access']['accessModeSufficient']:
            self.acc_suff_v.setChecked(True)

        access_layout.addWidget(self.acc_suff_v)

    def save_settings(self):

        # accessMode
        access_mode = []
        if self.acc_mode_t.isChecked():
            access_mode.append('textual')

        if self.acc_mode_v.isChecked():
            access_mode.append('visual')

        # accessModeSufficient
        access_mode_suff = ''
        if self.acc_suff_t.isChecked():
            access_mode_suff = 'textual'

        else:
            access_mode_suff = 'visual'

        prefs['force_override'] = self.force_override.isChecked()
        prefs['access'] = {
            'accessibilitySummary': self.msg.text(),
            'accessMode': access_mode,
            'accessModeSufficient': access_mode_suff
            }
