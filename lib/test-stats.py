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

import unittest
from stats import Stats


class TestModule(unittest.TestCase):

    def setUp(self):
        self.items = Stats()

        self.tags = Stats(desc='Tags')
        self.tags.value = 5

    def test___init__(self):
        self.assertEqual(self.items.desc, 'Items')
        self.assertEqual(self.tags.desc, 'Tags')

        self.assertEqual(self.items.value, 0)

    def test_increase(self):
        self.items.increase()
        self.tags.increase()

        self.assertEqual(self.items.value, 1)
        self.assertEqual(self.tags.value, 6)

    def test_get(self):
        self.assertEqual(self.items.get(), 0)
        self.assertEqual(self.tags.get(), 5)

    def test_report(self):
        self.assertEqual(self.items.report(), 'Items added: 0')
        self.assertEqual(self.tags.report(), 'Tags added: 5')

    def test_reset(self):
        self.items.reset()
        self.tags.reset()

        self.assertEqual(self.items.value, 0)
        self.assertEqual(self.tags.value, 0)


if __name__ == '__main__':
    unittest.main()
