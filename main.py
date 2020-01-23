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

import sys
import os
from PyQt5.QtWidgets import QApplication, QStyleFactory
from PyQt5.QtCore import Qt, QCoreApplication, QSettings, QByteArray, QUrl
from PyQt5.QtGui import QIcon, QKeySequence, QFont, QPalette, QColor
from PyQt5.QtQml import qmlRegisterType
from mainwindow import MainWindow
from ebook import Ebook
from part import Part
import main_rc


if __name__ == "__main__":
    sys.argv.append("--disable-web-security")

    app = QApplication(sys.argv)
    QCoreApplication.setOrganizationName("Artanidos")
    QCoreApplication.setApplicationName("EbookCreator")
    QCoreApplication.setApplicationVersion("1.1.1")

    app.setStyle(QStyleFactory.create("Fusion"))

    qmlRegisterType(Ebook, 'EbookCreator', 1, 0, 'Ebook')
    qmlRegisterType(Part, 'EbookCreator', 1, 0, 'Part')

    font = QFont("Sans Serif", 15)
    app.setFont(font)
    app.setWindowIcon(QIcon(":/images/logo.svg"))

    win = MainWindow(app)
    win.show()
    sys.exit(app.exec_())
