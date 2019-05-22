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
from PyQt5.QtWidgets import QWizard, QWizardPage, QLabel, QLineEdit, QComboBox, QGridLayout, QVBoxLayout
from PyQt5.QtCore import pyqtSignal, QDir
from PyQt5.QtGui import QPixmap


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
        description = self.field("description")
        author = self.field("author")
        path = os.path.join(self.install_directory, "sources", projectName.lower())

        os.mkdir(path)
        os.mkdir(os.path.join(path, "pages"))

        with open(os.path.join(path, "book.qml"), "w") as f:
            f.write("import EbookCreator 1.0\n\n")
            f.write("Ebook {\n")
            f.write("    name: \"" + projectName + "\"\n")
            f.write("    description: \"" + description + "\"\n")
            f.write("    author: \"" + author + "\"\n")
            f.write("}\n")

        with open(os.path.join(path, "pages", "first.md"), "w") as f:
            f.write("##" + projectName + "\n")

        super().accept()
        self.loadBook.emit(path + "/book.qml")


class IntroPage(QWizardPage):

    def __init__(self):
        QWizardPage.__init__(self)
        self.setTitle("Introduction")
        self.setPixmap(QWizard.WatermarkPixmap, QPixmap("./images/wizard.png"))

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
        self.setPixmap(QWizard.LogoPixmap, QPixmap("./images/icon64.png"))

        self.projectNameLabel = QLabel("&Book title:")
        self.projectNameLineEdit = QLineEdit()
        self.projectNameLabel.setBuddy(self.projectNameLineEdit)
        self.projectNameLineEdit.setPlaceholderText("Book title")

        self.descriptionLabel = QLabel("&Description:")
        self.descriptionLineEdit = QLineEdit()
        self.descriptionLabel.setBuddy(self.descriptionLineEdit)
        self.descriptionLineEdit.setPlaceholderText("Book description")

        self.authorLabel = QLabel("&Author")
        self.authorLineEdit = QLineEdit()
        self.authorLabel.setBuddy(self.authorLineEdit)
        self.authorLineEdit.setPlaceholderText("Author")

        self.registerField("projectName*", self.projectNameLineEdit)
        self.registerField("description", self.descriptionLineEdit)
        self.registerField("author", self.authorLineEdit)

        self.warning = QLabel("")
        self.warning.setStyleSheet("QLabel  color : orange ")

        layout = QGridLayout()
        layout.addWidget(self.projectNameLabel, 0, 0)
        layout.addWidget(self.projectNameLineEdit, 0, 1)
        layout.addWidget(self.descriptionLabel, 1, 0)
        layout.addWidget(self.descriptionLineEdit, 1, 1)
        layout.addWidget(self.authorLabel, 2, 0)
        layout.addWidget(self.authorLineEdit, 2, 1)
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
        self.setPixmap(QWizard.WatermarkPixmap, QPixmap("./images/wizard.png"))

        self.label = QLabel("Click Finish to generate the project skeleton.")
        self.label.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)
