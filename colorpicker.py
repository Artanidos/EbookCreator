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

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QColor, QPainter, QImage
from PyQt5.QtCore import pyqtSignal, QSize, Qt


class ColorPicker(QWidget):
    colorChanged = pyqtSignal(object)
    colorPicked = pyqtSignal(object)

    def __init__(self, parent=None):
        super(ColorPicker, self).__init__(parent)
        self._hue = 0.0
        self._lpressed = False
        self.setMinimumSize(100, 100)

    def sizeHint(self):
        return QSize(100, 100)

    def setHue(self, hue):
        self._hue = hue
        self.update()

    def hue(self):
        return self._hue

    def paintEvent(self, event):
        painter = QPainter(self)
        image = QImage(100, 100, QImage.Format_ARGB32)
        for x in range(100):
            for y in range(100):
                s = x / 100.0
                l = (100 - y) / 100.0
                a = 1.0
                color = QColor.fromHslF(self._hue, s, l, a)
                image.setPixel(x, y, color.rgba())
        painter.drawImage(0, 0, image)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._lpressed = True
        self.colorChanged.emit(self.getColor(event))

    def mouseReleaseEvent(self, event):
        if self._lpressed:
            self._lpressed = False
            self.colorPicked.emit(self.getColor(event))

    def getColor(self, event):
        x = event.pos().x()
        y = event.pos().y()
        if x < 0:
            x = 0
        if x > 100:
            x = 100
        if y < 0:
            y = 0
        if y > 100:
            y = 100
        s = x / 100.0
        l = (100 - y) / 100.0
        a = 1.0
        return QColor.fromHslF(self._hue, s, l, a)
