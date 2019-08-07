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
import datetime
import shutil
from PyQt5.QtWidgets import QWizard, QWizardPage, QLabel, QLineEdit, QComboBox, QGridLayout, QVBoxLayout
from PyQt5.QtCore import pyqtSignal, QDir
from PyQt5.QtGui import QPixmap
import resources


class ProjectWizard(QWizard):
    loadBook = pyqtSignal(object)

    def __init__(self, install_directory, parent = None):
        super(ProjectWizard, self).__init__(parent)
        self.install_directory = install_directory
        self.addPage(IntroPage())
        self.addPage(ProjectInfoPage(install_directory))
        self.addPage(ConclusionPage())
        self.setWindowTitle("Project Wizard")

    def accept(self):
        projectName = self.field("projectName")
        language = self.field("language")
        theme = self.field("theme")
        creator = self.field("creator")
        path = os.path.join(self.install_directory, "sources", projectName.replace(" ", "").lower())

        os.mkdir(path)
        os.mkdir(os.path.join(path, "parts"))
        os.mkdir(os.path.join(path, "images"))

        with open(os.path.join(path, "book.qml"), "w") as f:
            f.write("import EbookCreator 1.0\n\n")
            f.write("Ebook {\n")
            f.write("    name: \"" + projectName + "\"\n")
            f.write("    language: \"" + language + "\"\n")
            f.write("    theme: \"" + theme + "\"\n")
            f.write("    creator: \"" + creator + "\"\n")
            f.write("    Part {\n")
            f.write("        src: \"first.md\"\n")
            f.write("        name: \"First\"\n")
            f.write("    }")
            f.write("}\n")

        with open(os.path.join(path, "parts", "first.md"), "w") as f:
            f.write("#" + projectName + "\n")

        shutil.copytree(os.path.join(os.getcwd(), "themes", theme, "assets", "css"), os.path.join(path, "css"))

        super().accept()
        self.loadBook.emit(path + "/book.qml")


class IntroPage(QWizardPage):

    def __init__(self):
        QWizardPage.__init__(self)
        self.setTitle("Introduction")
        self.setPixmap(QWizard.WatermarkPixmap, QPixmap(":/images/wizard.svg"))

        label = QLabel("This wizard will generate a skeleton project. "
                       "You simply need to specify the project name and set a "
                       "few options to produce the project.")
        label.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)


class ProjectInfoPage(QWizardPage):

    def __init__(self, install_directory):
        QWizardPage.__init__(self)
        self.install_directory = install_directory
        self.setTitle("Project Information")
        self.setSubTitle("Specify basic information about the project for which you "
                         "want to generate project files.")
        self.setPixmap(QWizard.LogoPixmap, QPixmap(":/images/logo.svg"))

        self.projectNameLabel = QLabel("&Book title:")
        self.projectNameLineEdit = QLineEdit()
        self.projectNameLabel.setBuddy(self.projectNameLineEdit)
        self.projectNameLineEdit.setPlaceholderText("Book title")

        self.creatorNameLabel = QLabel("&Creator:")
        self.creatorNameLineEdit = QLineEdit()
        self.creatorNameLabel.setBuddy(self.creatorNameLineEdit)
        self.creatorNameLineEdit.setPlaceholderText("Book creator")

        self.languageLabel = QLabel("&Language:")
        self.language = QComboBox()
        self.language.setEditable(True)
        self.languageLabel.setBuddy(self.language)
        self.language.addItem("de")
        self.language.addItem("en")
        self.language.addItem("es")
        self.language.addItem("fr")
        self.language.addItem("it")

        self.themeLabel = QLabel("&Theme")
        self.theme = QComboBox()
        self.themeLabel.setBuddy(self.theme)
        # todo, add all other themes
        self.theme.addItem("default")

        self.registerField("projectName*", self.projectNameLineEdit)
        self.registerField("creator*", self.creatorNameLineEdit)
        self.registerField("language", self.language, "currentText")
        self.registerField("theme", self.theme, "currentText")

        self.warning = QLabel("")
        self.warning.setStyleSheet("QLabel  color : orange ")

        layout = QGridLayout()
        layout.addWidget(self.projectNameLabel, 0, 0)
        layout.addWidget(self.projectNameLineEdit, 0, 1)
        layout.addWidget(self.creatorNameLabel, 1, 0)
        layout.addWidget(self.creatorNameLineEdit, 1, 1)
        layout.addWidget(self.languageLabel, 2, 0)
        layout.addWidget(self.language, 2, 1)
        layout.addWidget(self.themeLabel, 3, 0)
        layout.addWidget(self.theme, 3, 1)
        layout.addWidget(self.warning, 4, 0, 1, 2)
        self.setLayout(layout)
        self.projectNameLineEdit.textChanged.connect(self.projectNameChanged)

    def projectNameChanged(self, name):
        if os.path.isdir(os.path.join(self.install_directory, "sources", name.lower())):
            self.warning.setText("WARNING<br/>A project with the name " + name.lower() + " already exists.<br/>If you continue the project will be overridden.")
        else:
            self.warning.setText("")


class ConclusionPage(QWizardPage):

    def __init__(self):
        QWizardPage.__init__(self)
        self.setTitle("Conclusion")
        self.setPixmap(QWizard.WatermarkPixmap, QPixmap(":/images/wizard.png"))

        self.label = QLabel("Click Finish to generate the project skeleton.")
        self.label.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)
