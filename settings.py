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

from PyQt5.QtCore import (QCoreApplication, QParallelAnimationGroup,
                          QPropertyAnimation, Qt, pyqtProperty, pyqtSignal)
from PyQt5.QtGui import QColor, QImage, QPalette, QPixmap
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QLabel, QGridLayout, QComboBox, QLineEdit, QPushButton


class Settings(QDialog):

    def __init__(self, book, parent = None):
        super(Settings, self).__init__(parent)
        self.book = book
        self.saved = False
        self.setWindowTitle(QCoreApplication.applicationName() + " - Book Settings")
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Ok")
        self.ok_button.setDefault(True)
        self.ok_button.setEnabled(False)
        cancel_button = QPushButton("Cancel")
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(cancel_button)
        layout = QGridLayout()
        self.title = QLineEdit()
        self.title.setText(book.name)
        self.title.setMinimumWidth(200)
        self.creator = QLineEdit()
        self.creator.setText(book.creator)
        self.language = QComboBox()
        self.language.setEditable(True)
        self.language.addItem("de")
        self.language.addItem("en")
        self.language.addItem("es")
        self.language.addItem("it")
        self.language.addItem("fr")
        self.language.setEditText(book.language)
        self.theme = QComboBox()
        self.theme.addItem("default")
        layout.addWidget(QLabel("Title"), 0, 0)
        layout.addWidget(self.title, 0, 1, 1, 3)
        layout.addWidget(QLabel("Creator"), 1, 0)
        layout.addWidget(self.creator, 1, 1, 1, 3)
        layout.addWidget(QLabel("Language"), 2, 0)
        layout.addWidget(self.language, 2, 1)
        layout.addWidget(QLabel("Theme"), 3, 0)
        layout.addWidget(self.theme, 3, 1)
        layout.addLayout(button_layout, 4, 0, 1, 4)
        self.setLayout(layout)

        self.ok_button.clicked.connect(self.okClicked)
        cancel_button.clicked.connect(self.cancelClicked)
        self.title.textChanged.connect(self.textChanged)
        self.creator.textChanged.connect(self.textChanged)
        self.language.editTextChanged.connect(self.textChanged)
        self.theme.currentIndexChanged.connect(self.textChanged)

    def okClicked(self):
        self.book.name = self.title.text()
        self.book.creator = self.creator.text()
        self.book.language = self.language.currentText()
        self.book.theme = self.theme.currentText()
        self.book.save()
        self.saved = True
        self.close()

    def cancelClicked(self):
        self.close()

    def textChanged(self):
        self.ok_button.setEnabled(True)
