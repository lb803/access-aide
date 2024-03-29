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

class Stats:
    '''
    Simple class to manage stats.

    Once the object is created, stat value can be increased, returned
    and reset to zero.
    '''

    def __init__(self, desc='Items'):
        self.desc = desc
        self.value = 0

    def increase(self):
        self.value += 1

    def get(self):
        return self.value

    def report(self):
        return '{} added: {}'.format(self.desc, self.value)

    def reset(self):
        self.value = 0
