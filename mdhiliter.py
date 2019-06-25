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

from PyQt5.QtGui import QFont, QFontMetrics, QImage, QSyntaxHighlighter, QTextCharFormat, QColor

TITLE = 0
BOLD = 1
ITALIC = 2
BOLD_ITALIC = 3
LAST_CONSTRUCT = BOLD_ITALIC


class MdHiLiter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(MdHiLiter, self).__init__(parent)

        self.formats = [0] * (LAST_CONSTRUCT + 1)
        titleFormat = QTextCharFormat()
        titleFormat.setForeground(QColor("#4d94d6"))
        titleFormat.setFontWeight(QFont.Bold)
        self.setFormatFor(TITLE, titleFormat)

        boldFormat = QTextCharFormat()
        boldFormat.setForeground(QColor("#abb471"))
        boldFormat.setFontWeight(QFont.Bold)
        self.setFormatFor(BOLD, boldFormat)

        italicFormat = QTextCharFormat()
        italicFormat.setForeground(QColor("#bf8369"))
        italicFormat.setFontItalic(True)
        self.setFormatFor(ITALIC, italicFormat)

        boldItalicFormat = QTextCharFormat()
        boldItalicFormat.setForeground(QColor("#bf8369"))
        boldItalicFormat.setFontItalic(True)
        boldItalicFormat.setFontWeight(QFont.Bold)
        self.setFormatFor(BOLD_ITALIC, boldItalicFormat)

    def setFormatFor(self, construct, format):
        self.formats[construct] = format
        self.rehighlight()

    def formatFor(self, construct):
        return self.formats[construct]

    def highlightBlock(self, text):
        length = len(text)
        start = 0
        pos = 0

        while pos < length:
            ch = text[pos]
            if ch == '#' and pos == 0 or text[pos - 1] == "\n":
                start = pos
                while pos < length and text[pos] != "\n":
                    pos = pos + 1
                self.setFormat(start, pos - start, self.formats[TITLE])
            elif ch == "*":
                start = pos
                cr = text.find("\n", pos + 1)
                tripl_star = self.find("***", text, pos + 4)
                dbl_star = self.find("**", text, pos + 3)
                star = self.find("*", text, pos + 2)
                if (pos + 3) < length and text[pos + 1] == "*" and text[pos + 2] == "*" and text[pos + 3] != " " and tripl_star > 0 and (tripl_star < cr or cr < 0):
                    self.setFormat(start, tripl_star + 3 - start, self.formats[BOLD_ITALIC])
                    pos = dbl_star + 3
                elif (pos + 2) < length and text[pos + 1] == "*" and text[pos + 2] != " " and dbl_star > 0 and (dbl_star < cr or cr < 0):
                    self.setFormat(start, dbl_star + 2 - start, self.formats[BOLD])
                    pos = dbl_star + 2
                elif (pos + 1) < length and text[pos + 1] != " " and star > 0 and (star < cr or cr < 0):
                    self.setFormat(start, star + 1 - start, self.formats[ITALIC])
                    pos = star + 1
                pos += 1
            else:
                pos += 1

    def find(self, needle, haystack, pos):
        while True:
            found = haystack.find(needle, pos)
            if found < 0:
                return -1
            else:
                if haystack[found - 1] == " ":
                    pos = found + 1
                    continue
                else:
                    return found
