#############################################################################
# Copyright (C) 2019 Olaf Japp
#
# This file is part of EbookCreator.
#
#  EbookCreator is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  EbookCreator is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with EbookCreator.  If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

import os
from PyQt5.QtCore import QObject, pyqtProperty, QFileInfo, Q_CLASSINFO
from PyQt5.QtQml import QQmlListProperty
from page import Page


class Ebook(QObject):
    Q_CLASSINFO('DefaultProperty', 'pages')

    def __init__(self, parent = None):
        super().__init__(parent)
        self._name = ""
        self._author = ""
        self._description = ""
        self._pages = []
        self.filename = ""
        self.source_path = ""
        self.window = ""

    @pyqtProperty(QQmlListProperty)
    def pages(self):
        return QQmlListProperty(Page, self, self._pages)

    @pyqtProperty('QString')
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @pyqtProperty('QString')
    def author(self):
        return self._author

    @author.setter
    def author(self, author):
        self._author = author

    @pyqtProperty('QString')
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        self._description = description

    def setFilename(self, filename):
        info = QFileInfo(filename)
        self.filename = info.fileName()
        self.source_path = info.path()

    def setWindow(self, window):
        self.window = window
