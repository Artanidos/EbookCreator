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
from PyQt5.QtWidgets import QLabel, QWidget, QStyleOption, QStyle
from PyQt5.QtCore import Qt, pyqtSignal, pyqtProperty, QDir
from PyQt5.QtGui import QPixmap, QImage, QPalette, QPainter


class FlatButton(QLabel):
    clickedWithReturn = pyqtSignal(object)
    clicked = pyqtSignal()

    def __init__(self, svg):
        QLabel.__init__(self)
        self.svg = svg
        self._enabled = True
        self.returncode = ""
        self.setColors()
        self.setCursor(Qt.PointingHandCursor)

    def setColors(self):
        self.label_normal_color = self.palette().buttonText().color().name()
        self.label_hovered_color = self.palette().highlight().color().name()
        self.label_disabled_color = self.palette().color(QPalette.Disabled, QPalette.ButtonText).name()

        self.normal_icon = QPixmap(self.createIcon(self.svg, self.label_normal_color))
        self.hover_icon = QPixmap(self.createIcon(self.svg, self.label_hovered_color))
        self.disabled_icon = QPixmap(self.createIcon(self.svg, self.label_disabled_color))

        if self.enabled:
            self.setPixmap(self.normal_icon)
        else:
            self.setPixmap(self.disabled_icon)

    def createIcon(self, source, hilite_color):
        bg = self.palette().button().color().name()
        temp = QDir.tempPath()
        with open(source, "r") as fp:
            data = fp.read()

        out = os.path.join(temp, hilite_color + ".svg")
        with open(out, "w") as fp:
            fp.write(data.replace("#ff00ff", hilite_color).replace("#0000ff", bg))
        return out

    def mousePressEvent(self, event):
        self.setFocus()
        event.accept()

    def mouseReleaseEvent(self, event):
        if self.enabled:
            self.setPixmap(self.hover_icon)
            event.accept()
            if not self.returncode:
                self.clicked.emit()
            else:
                self.clickedWithReturn.emit(self.returncode)

    def enterEvent(self, event):
        if self.enabled:
            self.setPixmap(self.hover_icon)
        QWidget.enterEvent(self, event)

    def leaveEvent(self, event):
        if self.enabled:
            self.setPixmap(self.normal_icon)
        else:
            self.setPixmap(self.disabled_icon)
        QWidget.leaveEvent(self, event)

    @pyqtProperty(bool)
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        self._enabled = enabled
        if enabled:
            self.setPixmap(self.normal_icon)
        else:
            self.setPixmap(self.disabled_icon)
        self.update()
