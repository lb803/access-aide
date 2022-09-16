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

from PyQt5.Qt import QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, \
                     QCheckBox, QGroupBox, QLabel, QLineEdit, QRadioButton, \
                     QGridLayout, QPushButton, QIcon, QPixmap, QCompleter, \
                     QDialogButtonBox, QDialog
from PyQt5.QtCore import Qt
from calibre.utils.config import JSONConfig

import webbrowser
import json


class Config():
    """Class to store/retrieve preference data within Calibre"""

    DEFAULTS = {
        "force_override": False,
        "heuristic": {"title_override": False, "type_footnotes": False},
        "access": {
            "accessibilitySummary": ["This publication conforms to WCAG 2.0 AA."],
            "accessMode": ["textual", "visual"],
            "accessModeSufficient": ["textual"],
            "accessibilityFeature": ["structuralNavigation", "alternativeText"],
            "accessibilityHazard": ["unknown"],
        },
        "a11y": {
            "enabled": False,
            "certifiedBy": "",
            "certifierCredential": "",
            "certifierReport": "",
        },
        "dcterms": {"conformsTo": ""},
    }

    def __init__(self):
        self.prefs = JSONConfig('plugins/access_aide')
        if not self.prefs:
            self.prefs.defaults = self.DEFAULTS

    def get_prefs(self):
        return self.prefs


class Completer(QCompleter):

    def __init__(self, *args, **kwargs):
        super(Completer, self).__init__(*args, **kwargs)
        self.setFilterMode(Qt.MatchContains)
        self.setCaseSensitivity(Qt.CaseInsensitive)
        self.setCompletionMode(QCompleter.PopupCompletion)


    # Add texts instead of replace
    def pathFromIndex(self, index):
        path = QCompleter.pathFromIndex(self, index)

        lst = str(self.widget().text()).split(' ')

        if len(lst) > 1:
            path = '%s %s' % (' '.join(lst[:-1]), path)

        return path

    # Add operator to separate between texts
    def splitPath(self, path):
        path = str(path.split(' ')[-1]).lstrip(' ')
        return [path]


class ConfigWidget(QDialog):

    def __init__(self, standalone=None):
        self.config = Config()
        self.prefs = self.config.get_prefs()

        QWidget.__init__(self)

        grid = QGridLayout()
        grid.addWidget(self.general_group(), 0, 0, 1, 1)
        grid.addWidget(self.heuristic_group(), 0, 1, 1, 1)
        grid.addWidget(self.access_group(), 1, 0, 1, 2)
        grid.addWidget(self.conform_group(), 2, 0, 1, 2)
        if standalone is not None:
            grid.addWidget(self.button_box(), 3, 0, 1, 2)
        self.setLayout(grid)

    def general_group(self):
        group_box = QGroupBox('General Preferences', self)

        self.force_override = QCheckBox('Force Override', self)
        self.force_override.setToolTip('When checked, existing HTML '
                                       'attributes and values will be '
                                       'overwritten.')
        self.force_override.setChecked(self.prefs.get('force_override', False))

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
        self.title_override.setChecked(self.prefs.get('heuristic', {}) \
                                            .get('title_override', False))

        self.type_fn = QCheckBox('Add epub:type to footnote and endnote '
                                 'marks', self)
        self.type_fn.setToolTip('When checked, adds corresponding epub:type '
                                'to footnote and endnote marks.')
        self.type_fn.setChecked(self.prefs.get('heuristic', {}) \
                                     .get('type_footnotes', False))

        vbox = QVBoxLayout()
        vbox.addWidget(self.title_override)
        vbox.addWidget(self.type_fn)
        vbox.addStretch(1)
        group_box.setLayout(vbox)

        return group_box

    def access_group(self):
        group_box = QGroupBox('Accessibility', self)

        # accessibilitySummary
        self.acc_summ = QLineEdit(self)
        self.acc_summ.setText(self.prefs['access']['accessibilitySummary'][0])

        # accessMode
        self.acc_mode_t = QCheckBox('Textual', self)
        if 'textual' in self.prefs['access']['accessMode']:
            self.acc_mode_t.setChecked(True)
        else:
            self.acc_mode_t.setChecked(False)

        self.acc_mode_v = QCheckBox('Visual', self)
        if 'visual' in self.prefs['access']['accessMode']:
            self.acc_mode_v.setChecked(True)
        else:
            self.acc_mode_v.setChecked(False)

        acc_mode_box = QVBoxLayout()
        acc_mode_box.addWidget(self.acc_mode_t)
        acc_mode_box.addWidget(self.acc_mode_v)

        # accessModeSufficient
        self.acc_suff_t = QRadioButton('Textual')
        if 'textual' in self.prefs['access']['accessModeSufficient']:
            self.acc_suff_t.setChecked(True)

        self.acc_suff_v = QRadioButton('Visual')
        if 'visual' in self.prefs['access']['accessModeSufficient']:
            self.acc_suff_v.setChecked(True)

        acc_suff_box = QVBoxLayout()
        acc_suff_box.addWidget(self.acc_suff_t)
        acc_suff_box.addWidget(self.acc_suff_v)

        # accessibilityFeature
        self.acc_feat = QLineEdit(self)
        acc_feat_list = self.prefs.get('access', {}).get('accessibilityFeature', [])
        self.acc_feat.setText(' '.join(acc_feat_list))
        self.acc_feat.setToolTip('schema:accessibilityFeature metadata '
                                 'propriety. Separate values with space.')
        self.acc_feat.setPlaceholderText('structuralNavigation '
                                         'alternativeText')

        feat_list = json.loads(get_resources('assets/acc_feature_values.json'))
        completer = Completer(feat_list)
        self.acc_feat.setCompleter(completer)

        # accessibilityHazard
        self.acc_hazard_none = QCheckBox('None', self)
        if 'none' in self.prefs['access'].get('accessibilityHazard', []):
            self.acc_hazard_none.setChecked(True)
        else:
            self.acc_hazard_none.setChecked(False)

        self.acc_hazard_unknown = QCheckBox('Unknown', self)
        if 'unknown' in self.prefs['access'].get('accessibilityHazard', []):
            self.acc_hazard_unknown.setChecked(True)
        else:
            self.acc_hazard_unknown.setChecked(False)

        self.acc_hazard_f = QCheckBox('Flashing', self)
        if 'flashing' in self.prefs['access'].get('accessibilityHazard', []):
            self.acc_hazard_f.setChecked(True)
        else:
            self.acc_hazard_f.setChecked(False)

        self.acc_hazard_m = QCheckBox('Motion Simulation', self)
        if 'motionSimulation' in self.prefs['access'] \
                                 .get('accessibilityHazard', []):
            self.acc_hazard_m.setChecked(True)
        else:
            self.acc_hazard_m.setChecked(False)

        self.acc_hazard_s = QCheckBox('Sound', self)
        if 'sound' in self.prefs['access'].get('accessibilityHazard', []):
            self.acc_hazard_s.setChecked(True)
        else:
            self.acc_hazard_s.setChecked(False)

        acc_hazard_box = QVBoxLayout()
        acc_hazard_box.addWidget(self.acc_hazard_none)
        acc_hazard_box.addWidget(self.acc_hazard_unknown)
        acc_hazard_box.addWidget(self.acc_hazard_f)
        acc_hazard_box.addWidget(self.acc_hazard_m)
        acc_hazard_box.addWidget(self.acc_hazard_s)

        fbox = QFormLayout()
        fbox.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        fbox.addRow(QLabel('Accessibility Summary:'), self.acc_summ)
        fbox.addRow(QLabel('Access Mode:'), acc_mode_box)
        fbox.addRow(QLabel('Access Mode Sufficient:'), acc_suff_box)
        fbox.addRow(QLabel('Accessibility Feature:'), self.acc_feat)
        fbox.addRow(QLabel('Accessibility Hazard:'), acc_hazard_box)
        group_box.setLayout(fbox)

        return group_box

    def conform_group(self):
        self.conform_box = QGroupBox('Conformance Properties', self)
        self.conform_box.setCheckable(True)
        self.conform_box.setChecked(self.prefs.get('a11y', {}).get('enabled', False))
        self.conform_box.setToolTip('Enable conformance metadata proprieties')

        self.conform_to = QLineEdit(self.prefs.get('dcterms', {}) \
                                    .get('conformsTo', ''))
        self.conform_to.setToolTip('dcterms:conformsTo metadata propriety')
        self.conform_to.setPlaceholderText('http://www.idpf.org/epub/a11y/'
                                           'accessibility-20170105.html'
                                           '#wcag-aa')

        self.a11y_by = QLineEdit(self.prefs.get('a11y', {}).get('certifiedBy', ''))
        self.a11y_by.setToolTip('a11y:certifiedBy metadata propriety')
        self.a11y_by.setPlaceholderText('Book Company Ltd')

        self.a11y_credential = QLineEdit(self.prefs.get('a11y', {}) \
                                              .get('certifierCredential', ''))
        self.a11y_credential.setToolTip('a11y:certifierCredential metadata '
                                        'propriety')
        self.a11y_credential.setPlaceholderText('DAISY OK')

        self.a11y_report = QLineEdit(self.prefs.get('a11y', {}) \
                                          .get('certifierReport', ''))
        self.a11y_report.setToolTip('a11y:certifierReport metadata propriety')
        self.a11y_report.setPlaceholderText('https://www.link.to/report.html')

        fbox = QFormLayout()
        fbox.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        fbox.addRow(QLabel('Conformance URL:'), self.conform_to)
        fbox.addRow(QLabel('Certified by:'), self.a11y_by)
        fbox.addRow(QLabel('Certifier Credential:'), self.a11y_credential)
        fbox.addRow(QLabel('Report URL:'), self.a11y_report)
        self.conform_box.setLayout(fbox)

        return self.conform_box

    def button_box(self):
        Btn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        buttonBox = QDialogButtonBox(Btn)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        return buttonBox

    def accept(self):
        self.save_settings()
        super().accept()

    def reject(self):
        super().reject()

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

        self.prefs['force_override'] = self.force_override.isChecked()
        self.prefs['heuristic'] = {
            'title_override': self.title_override.isChecked(),
            'type_footnotes': self.type_fn.isChecked()
            }
        self.prefs['access'] = {
            'accessibilitySummary': [self.acc_summ.text()],
            'accessMode': access_mode,
            'accessModeSufficient': [access_mode_suff],
            'accessibilityFeature': self.acc_feat.text().split(),
            'accessibilityHazard': access_hazard
            }
        self.prefs['a11y'] = {
            'enabled': self.conform_box.isChecked(),
            'certifiedBy': self.a11y_by.text(),
            'certifierCredential': self.a11y_credential.text(),
            'certifierReport': self.a11y_report.text()
            }
        self.prefs['dcterms'] = {
            'conformsTo': self.conform_to.text()
        }

        self.prefs = prefs
