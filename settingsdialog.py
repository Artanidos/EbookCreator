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

from PyQt5.QtWidgets import QDialog, QGridLayout, QComboBox, QStyleFactory, QLabel, QWidget, QHBoxLayout, QPushButton
from PyQt5.QtGui import QColor
from coloreditor import ColorEditor


class SettingsDialog(QDialog):
    def __init__(self, theme, hilite_color, parent=None):
        super(SettingsDialog, self).__init__(parent)

        self.hilite_color = hilite_color
        self.theme = theme

        self.setWindowTitle("EbookCreator - Settings")
        box = QHBoxLayout()
        self.ok = QPushButton("Ok")
        self.ok.setEnabled(False)
        self.cancel = QPushButton("Cancel")
        box.addStretch()
        box.addWidget(self.ok)
        box.addWidget(self.cancel)
        layout = QGridLayout()
        self.color = ColorEditor("Hilite color")
        self.color.setColor(QColor(self.hilite_color))
        self.styles = QComboBox()
        self.styles.addItem("DarkFusion")
        self.styles.addItems(QStyleFactory.keys())
        self.styles.setCurrentText(theme)
        layout.addWidget(QLabel("  Theme"), 0, 0)
        layout.addWidget(self.styles, 0, 3, 1, 4)
        layout.addWidget(self.color, 1, 0, 1, 7)
        layout.addLayout(box, 2, 0, 1, 7)
        self.setLayout(layout)

        self.color.colorChanged.connect(self.colorChanged)
        self.styles.currentTextChanged.connect(self.themeChanged)
        self.ok.clicked.connect(self.okClicked)
        self.cancel.clicked.connect(self.close)

    def colorChanged(self, color):
        self.ok.setEnabled(True)

    def themeChanged(self, theme):
        self.ok.setEnabled(True)

    def okClicked(self):
        self.hilite_color = self.color.color.text()
        self.theme = self.styles.currentText()
        self.close()
