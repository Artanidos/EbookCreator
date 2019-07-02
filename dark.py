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

from PyQt5.QtWidgets import QProxyStyle, QStyleFactory, QApplication, QListWidget
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt
from flatbutton import FlatButton
from expander import Expander


class DarkFusion(QProxyStyle):

    def __init__(self, hilite_color):
        QProxyStyle.__init__(self, QStyleFactory.create("fusion"))
        self.hilite_color = hilite_color

    def polish(self, arg):
        if isinstance(arg, QPalette):
            palette = arg
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(64, 66, 68))
            palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.black)
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Highlight, QColor(self.hilite_color))
            palette.setColor(QPalette.HighlightedText, Qt.black)
            palette.setColor(QPalette.Disabled, QPalette.Text, Qt.darkGray)
            palette.setColor(QPalette.Disabled, QPalette.ButtonText, Qt.darkGray)
            palette.setColor(QPalette.Link, QColor("#bbbbbb"))
            return palette
        elif isinstance(arg, FlatButton):
            arg.setColors()
        elif isinstance(arg, Expander):
            arg.setColors()
