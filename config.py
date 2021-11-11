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

from PyQt5.Qt import QWidget, QHBoxLayout, QVBoxLayout, QCheckBox, QGroupBox, QLabel, QLineEdit, QRadioButton
from calibre.utils.config import JSONConfig

prefs = JSONConfig('plugins/access_aide')

# Set defaults
prefs.defaults['force_override'] = False
prefs.defaults['access'] = {
    'accessibilitySummary': ['This publication conforms to WCAG 2.0 AA.'],
    'accessMode': ['textual', 'visual'],
    'accessModeSufficient': ['textual'],
    'accessibilityFeature': ['structuralNavigation'],
    'accessibilityHazard': ['unknown']
    }

class ConfigWidget(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.l = QVBoxLayout()
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

        self.acc_summ = QLineEdit(self)
        self.acc_summ.setText(prefs['access']['accessibilitySummary'][0])
        access_layout.addWidget(self.acc_summ)
        self.label.setBuddy(self.acc_summ)

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

        # accessibilityFeature
        self.label4 = QLabel('Accessibility Feature:')
        access_layout.addWidget(self.label4)

        self.acc_feat = QLineEdit(self)
        self.acc_feat.setText(prefs['access']['accessibilityFeature'][0])
        access_layout.addWidget(self.acc_feat)
        self.label.setBuddy(self.acc_feat)

        # accessibilityHazard
        self.label5 = QLabel('Accessibility Hazard:')
        access_layout.addWidget(self.label5)

        self.acc_hazard_none = QCheckBox('&'+_('None'), self)
        access_layout.addWidget(self.acc_hazard_none)
        if 'none' in prefs['access'].get('accessibilityHazard', []):
            self.acc_hazard_none.setChecked(True)
        else:
            self.acc_hazard_none.setChecked(False)

        self.acc_hazard_unknown = QCheckBox('&'+_('Unknown'), self)
        access_layout.addWidget(self.acc_hazard_unknown)
        if 'unknown' in prefs['access'].get('accessibilityHazard', []):
            self.acc_hazard_unknown.setChecked(True)
        else:
            self.acc_hazard_unknown.setChecked(False)

        self.acc_hazard_f = QCheckBox('&'+_('Flashing'), self)
        access_layout.addWidget(self.acc_hazard_f)
        if 'flashing' in prefs['access'].get('accessibilityHazard', []):
            self.acc_hazard_f.setChecked(True)
        else:
            self.acc_hazard_f.setChecked(False)

        self.acc_hazard_m = QCheckBox('&'+_('Motion Simulation'), self)
        access_layout.addWidget(self.acc_hazard_m)
        if 'motionSimulation' in prefs['access'].get('accessibilityHazard', []):
            self.acc_hazard_m.setChecked(True)
        else:
            self.acc_hazard_m.setChecked(False)

        self.acc_hazard_s = QCheckBox('&'+_('Sound'), self)
        access_layout.addWidget(self.acc_hazard_s)
        if 'sound' in prefs['access'].get('accessibilityHazard', []):
            self.acc_hazard_s.setChecked(True)
        else:
            self.acc_hazard_s.setChecked(False)


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

        # accessibilityHazard
        access_hazard = []
        if self.acc_hazard_none.isChecked():
            access_hazard.append('none')

        elif self.acc_hazard_unknown.isChecked():
            access_hazard.append('unknown')

        else:
            if self.acc_hazard_f.isChecked():
                access_hazard.append('flashing')
            else:
                access_hazard.append('noFlashingHazard')

            if self.acc_hazard_m.isChecked():
                access_hazard.append('motionSimulation')
            else:
                access_hazard.append('noMotionSimulationHazard')

            if self.acc_hazard_s.isChecked():
                access_hazard.append('sound')
            else:
                access_hazard.append('noSoundHazard')

        prefs['force_override'] = self.force_override.isChecked()
        prefs['access'] = {
            'accessibilitySummary': [self.acc_summ.text()],
            'accessMode': access_mode,
            'accessModeSufficient': [access_mode_suff],
            'accessibilityFeature': [self.acc_feat.text()],
            'accessibilityHazard': access_hazard
            }
