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

from PyQt5.Qt import QWidget, QHBoxLayout, QVBoxLayout, QCheckBox, QGroupBox, QLabel, QLineEdit, QRadioButton, QGridLayout
from calibre.utils.config import JSONConfig

prefs = JSONConfig('plugins/access_aide')

# Set defaults
prefs.defaults['force_override'] = False
prefs.defaults['heuristic'] = {
    'title_override': False,
    'type_footnotes': False
    }
prefs.defaults['access'] = {
    'accessibilitySummary': ['This publication conforms to WCAG 2.0 AA.'],
    'accessMode': ['textual', 'visual'],
    'accessModeSufficient': ['textual'],
    'accessibilityFeature': ['structuralNavigation'],
    'accessibilityHazard': ['unknown']
    }
prefs.defaults['a11y'] = {
    'enabled': False,
    'certifiedBy': '',
    'certifierCredential': '',
    'certifierReport': ''
}

class ConfigWidget(QWidget):

    def __init__(self):
        QWidget.__init__(self)

        grid = QGridLayout()
        grid.addWidget(self.general_group(), 0, 0, 1, 1)
        grid.addWidget(self.heuristic_group(), 0, 1, 1, 1)
        grid.addWidget(self.access_group(), 1, 0, 1, 2)
        grid.addWidget(self.a11y_group(), 2, 0, 1, 2)
        self.setLayout(grid)
        
    def general_group(self):
        group_box = QGroupBox('General Preferences', self)

        self.force_override = QCheckBox('Force Override', self)
        self.force_override.setToolTip('When checked, existing HTML '
                                       'attributes and values will be '
                                       'overwritten.')
        self.force_override.setChecked(prefs['force_override'])

        vbox = QVBoxLayout()
        vbox.addWidget(self.force_override)
        vbox.addStretch(1)
        group_box.setLayout(vbox)

        return group_box

    def heuristic_group(self):
        group_box = QGroupBox('Heuristic Options', self)

        self.title_override = QCheckBox('Match <title> text with <h1>', self)
        self.title_override.setToolTip('When checked, replaces '
                                       'the existing <title> text with'
                                       'the first <h1> found on the page')
        try:
            self.title_override \
                .setChecked(prefs['heuristic']['title_override'])
        except KeyError:
            self.title_override.setChecked(False)

        self.type_fn = QCheckBox('Add epub:type to footnote and endnote '
                                 'marks', self)
        self.type_fn.setToolTip('When checked, adds corresponding epub:type '
                                'to footnote and endnote marks.')
        try:
            self.type_fn.setChecked(prefs['heuristic']['type_footnotes'])
        except KeyError:
            self.type_fn.setChecked(False)

        vbox = QVBoxLayout()
        vbox.addWidget(self.title_override)
        vbox.addWidget(self.type_fn)
        vbox.addStretch(1)
        group_box.setLayout(vbox)

        return group_box

    def access_group(self):
        group_box = QGroupBox('Accessibility', self)

        # accessibilitySummary
        acc_summ_label = QLabel(self)
        acc_summ_label.setText('Accessibility Summary:')

        self.acc_summ = QLineEdit(self)
        self.acc_summ.setText(prefs['access']['accessibilitySummary'][0])
        acc_summ_label.setBuddy(self.acc_summ)

        # accessMode
        acc_mode_label = QLabel(self)
        acc_mode_label.setText('Access Mode:')
        
        self.acc_mode_t = QCheckBox('Textual', self)
        if 'textual' in prefs['access']['accessMode']:
            self.acc_mode_t.setChecked(True)
        else:
            self.acc_mode_t.setChecked(False)

        self.acc_mode_v = QCheckBox('Visual', self)
        if 'visual' in prefs['access']['accessMode']:
            self.acc_mode_v.setChecked(True)
        else:
            self.acc_mode_v.setChecked(False)

        # accessModeSufficient
        acc_suff_label = QLabel(self)
        acc_suff_label.setText('Access Mode Sufficient:')

        self.acc_suff_t = QRadioButton('Textual')
        if 'textual' in prefs['access']['accessModeSufficient']:
            self.acc_suff_t.setChecked(True)

        self.acc_suff_v = QRadioButton('Visual')
        if 'visual' in prefs['access']['accessModeSufficient']:
            self.acc_suff_v.setChecked(True)

        # accessibilityFeature
        acc_feat_label = QLabel(self)
        acc_feat_label.setText('Accessibility Feature:')

        self.acc_feat = QLineEdit(self)
        self.acc_feat.setText(prefs['access']['accessibilityFeature'][0])
        acc_feat_label.setBuddy(self.acc_feat)

        # accessibilityHazard
        acc_hazard_label = QLabel(self)
        acc_hazard_label.setText('Accessibility Hazard:')

        self.acc_hazard_none = QCheckBox('None', self)
        if 'none' in prefs['access'].get('accessibilityHazard', []):
            self.acc_hazard_none.setChecked(True)
        else:
            self.acc_hazard_none.setChecked(False)

        self.acc_hazard_unknown = QCheckBox('Unknown', self)
        if 'unknown' in prefs['access'].get('accessibilityHazard', []):
            self.acc_hazard_unknown.setChecked(True)
        else:
            self.acc_hazard_unknown.setChecked(False)

        self.acc_hazard_f = QCheckBox('Flashing', self)
        if 'flashing' in prefs['access'].get('accessibilityHazard', []):
            self.acc_hazard_f.setChecked(True)
        else:
            self.acc_hazard_f.setChecked(False)

        self.acc_hazard_m = QCheckBox('Motion Simulation', self)
        if 'motionSimulation' in prefs['access'] \
                                 .get('accessibilityHazard', []):
            self.acc_hazard_m.setChecked(True)
        else:
            self.acc_hazard_m.setChecked(False)

        self.acc_hazard_s = QCheckBox('Sound', self)
        if 'sound' in prefs['access'].get('accessibilityHazard', []):
            self.acc_hazard_s.setChecked(True)
        else:
            self.acc_hazard_s.setChecked(False)

        vbox = QVBoxLayout()
        vbox.addWidget(acc_summ_label)
        vbox.addWidget(self.acc_summ)

        vbox.addWidget(acc_mode_label)
        vbox.addWidget(self.acc_mode_t)
        vbox.addWidget(self.acc_mode_v)

        vbox.addWidget(acc_suff_label)
        vbox.addWidget(self.acc_suff_t)
        vbox.addWidget(self.acc_suff_v)

        vbox.addWidget(acc_feat_label)
        vbox.addWidget(self.acc_feat)

        vbox.addWidget(acc_hazard_label)
        vbox.addWidget(self.acc_hazard_none)
        vbox.addWidget(self.acc_hazard_unknown)
        vbox.addWidget(self.acc_hazard_f)
        vbox.addWidget(self.acc_hazard_m)
        vbox.addWidget(self.acc_hazard_s)
        
        vbox.addStretch(1)
        group_box.setLayout(vbox)

        return group_box

    def a11y_group(self):
        self.a11y_box = QGroupBox('Conformance Properties', self)

        self.a11y_box.setCheckable(True)
        self.a11y_box.setChecked(prefs.get('a11y', {}).get('enabled', False))

        a11y_by_label = QLabel('Certified by:')
        self.a11y_by = QLineEdit(prefs.get('a11y', {}).get('certifiedBy', ''))
        a11y_by_label.setBuddy(self.a11y_by)

        a11y_credential_label = QLabel('Certifier Credential:')
        self.a11y_credential = QLineEdit(prefs.get('a11y', {}) \
                                              .get('certifierCredential', ''))
        a11y_credential_label.setBuddy(self.a11y_credential)

        a11y_report_label = QLabel('Report URL:')
        self.a11y_report = QLineEdit(prefs.get('a11y', {}) \
                                          .get('certifierReport', ''))
        a11y_report_label.setBuddy(self.a11y_report)

        vbox = QVBoxLayout()
        vbox.addWidget(a11y_by_label)
        vbox.addWidget(self.a11y_by)
        vbox.addWidget(a11y_credential_label)
        vbox.addWidget(self.a11y_credential)
        vbox.addWidget(a11y_report_label)
        vbox.addWidget(self.a11y_report)
        vbox.addStretch(1)
        self.a11y_box.setLayout(vbox)

        return self.a11y_box

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
        prefs['heuristic'] = {
            'title_override': self.title_override.isChecked(),
            'type_footnotes': self.type_fn.isChecked()
            }
        prefs['access'] = {
            'accessibilitySummary': [self.acc_summ.text()],
            'accessMode': access_mode,
            'accessModeSufficient': [access_mode_suff],
            'accessibilityFeature': [self.acc_feat.text()],
            'accessibilityHazard': access_hazard
            }
        prefs['a11y'] = {
            'enabled': self.a11y_box.isChecked(),
            'certifiedBy': self.a11y_by.text(),
            'certifierCredential': self.a11y_credential.text(),
            'certifierReport': self.a11y_report.text()
            }
