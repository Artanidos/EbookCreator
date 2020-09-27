#############################################################################
# Copyright (C) 2020 Olaf Japp
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
from part import Part


class Ebook(QObject):
    Q_CLASSINFO('DefaultProperty', 'parts')

    def __init__(self, parent = None):
        super().__init__(parent)
        self._name = ""
        self._theme = ""
        self._language = ""
        self._creator = ""
        self._publisher = ""
        self._size = ""
        self._parts = []
        self.filename = ""
        self.source_path = ""
        self.window = ""

    @pyqtProperty(QQmlListProperty)
    def parts(self):
        return QQmlListProperty(Part, self, self._parts)

    @pyqtProperty('QString')
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @pyqtProperty('QString')
    def language(self):
        return self._language

    @language.setter
    def language(self, language):
        self._language = language

    @pyqtProperty('QString')
    def theme(self):
        return self._theme

    @theme.setter
    def theme(self, theme):
        self._theme = theme

    @pyqtProperty('QString')
    def creator(self):
        return self._creator

    @creator.setter
    def creator(self, creator):
        self._creator = creator

    @pyqtProperty('QString')
    def publisher(self):
        return self._publisher

    @publisher.setter
    def publisher(self, publisher):
        self._publisher = publisher

    @pyqtProperty('QString')
    def size(self):
        return self._size

    @size.setter
    def size(self, size):
        self._size = size

    def setFilename(self, filename):
        info = QFileInfo(filename)
        self.filename = info.fileName()
        self.source_path = info.path()

    def setWindow(self, window):
        self.window = window

    def getPart(self, name):
        for part in self._parts:
            if part.name == name or part.src == name.lower() + ".md":
                return part
        return None

    def dropPart(self, partname):
        part = self.getPart(partname)
        filename = os.path.join(self.source_path, "parts", part.src)
        os.remove(filename)
        self._parts.remove(part)
        self.save()

    def addPart(self, name):
        part = Part()
        part.name = name
        part.src = name.replace(" ", "").lower() + ".md"
        self._parts.append(part)
        with open(os.path.join(self.source_path, "parts", part.src), "w") as f:
            f.write("")
        self.save()

    def updatePart(self, oldname, newname):
        part = self.getPart(oldname)
        part.name = newname
        self.save()

    def partUp(self, partname):
        part = self.getPart(partname)
        pos = self._parts.index(part)
        self._parts.remove(part)
        self._parts.insert(pos - 1, part)
        self.save()

    def partDown(self, partname):
        part = self.getPart(partname)
        pos = self._parts.index(part)
        self._parts.remove(part)
        self._parts.insert(pos + 1, part)
        self.save()

    def save(self):
        fname = os.path.join(self.source_path, self.filename)
        with open(fname, "w") as f:
            f.write("import EbookCreator 1.0\n\n")
            f.write("Ebook {\n")
            f.write("    name: \"" + self._name + "\"\n")
            f.write("    language: \"" + self._language + "\"\n")
            f.write("    size: \"" + self._size + "\"\n")
            f.write("    theme: \"" + self._theme + "\"\n")
            f.write("    creator: \"" + self._creator + "\"\n")
            for part in self._parts:
                f.write("    Part {\n")
                f.write("        src: \"" + part.src + "\"\n")
                f.write("        name: \"" + part.name + "\"\n")
                if part.pdfOnly:
                    f.write("        pdfOnly: true\n")
                f.write("    }\n")
            f.write("}\n")
