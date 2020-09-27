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

from interfaces import GeneratorInterface
from PyQt5.QtWidgets import QWidget

class CalendarGenerator(GeneratorInterface):
    def __init__(self):
        QWidget.__init__(self)
        self.display_name = "Calendar"

    def menu_action(self):
        cursor = self.text_edit.textCursor()
        pos = cursor.position()
        text = "<!-- the caption is only used for the table of contents -->"
        text += '<h1 style="visibility: hidden;">Calendar</h1>\n'
        text += '<style>\n'
        text += '.square\n'
        text += '{\n'
        text += '    height: 50px;\n'
        text += '    width: 120px;\n'
        text += '    border-style: solid;\n'
        text += '    border-width: 1px;\n'
        text += '    border-color: #000000;\n'
        text += '    margin: 5px;\n'
        text += '    padding: 10px;\n'
        text += '}\n'
        text += '.greg\n'
        text += '{\n'
        text += '    height: 20px;\n'
        text += '    margin-top: 20px;\n'
        text += '    margin-left: 15px;\n'
        text += '}\n'
        text += '.god\n'
        text += '{\n'
        text += '    background-color: #FFFFFF;\n'
        text += '}\n'
        text += '.moon\n'
        text += '{\n'
        text += '    background-color: #800080;\n'
        text += '    color: #FFFFFF;\n'
        text += '}\n'
        text += '.ocean\n'
        text += '{\n'
        text += '    background-color: #0000FF;\n'
        text += '    color: #FFFFFF;\n'
        text += '}\n'
        text += '.heaven\n'
        text += '{\n'
        text += '    background-color: #00FFFF;\n'
        text += '    color: #000000;\n'
        text += '}\n'
        text += '.tree\n'
        text += '{\n'
        text += '    page-break-after: always;\n'
        text += '    background-color: #008000;\n'
        text += '    color: #FFFFFF;\n'
        text += '}\n'
        text += '.sun\n'
        text += '{\n'
        text += '    background-color: #FFFF00;\n'
        text += '    color: #000000;\n'
        text += '}\n'
        text += '.fire\n'
        text += '{\n'
        text += '    background-color: #FF6600;\n'
        text += '    color: #000000;\n'
        text += '}\n'
        text += '.star\n'
        text += '{\n'
        text += '    background-color: #FF0000;\n'
        text += '    color: #FFFFFF;\n'
        text += '}\n'
        text += '.earth\n'
        text += '{\n'
        text += '    background-color: #000000;\n'
        text += '    color: #FFFFFF;\n'
        text += '}\n'
        text += '.note\n'
        text += '{\n'
        text += '    page-break-after: always;\n'
        text += '    background-color: #FFFFFF;\n'
        text += '    color: #000000;\n'
        text += '    width: 100%;\n'
        text += '    border-width: 0px;\n'
        text += '}\n'
        text += '.year\n'
        text += '{\n'
        text += '    text-align: center;\n'
        text += '    font-weight: bold;\n'
        text += '}\n'
        text += '.header\n'
        text += '{\n'
        text += '    position: relative;\n'
        text += '    top: 5px;\n'
        text += '    height: 40px;\n'
        text += '    width: 100%;\n'
        text += '    background-color: #FFFFFF;\n'
        text += '    display: flex;\n'
        text += '    flex-direction: row;\n'
        text += '    align-items: center;\n'
        text += '    justify-content: center;\n'
        text += '}\n'
        text += 'span.center\n'
        text += '{\n'
        text += '    text-align: center;\n'
        text += '    order: 2;\n'
        text += '    flex-grow: 0;\n'
        text += '}\n'
        text += 'span.left\n'
        text += '{\n'
        text += '    order: 1;\n'
        text += '    flex-grow: 1;\n'
        text += '    text-align: center;\n'
        text += '}\n'
        text += 'span.right\n'
        text += '{\n'
        text += '    order: 3;\n'
        text += '    flex-grow: 1;\n'
        text += '    text-align: center;\n'
        text += '}\n'
        text += '</style>\n\n'
        text += '<h1 style="visibility: hidden;">Calendar</h1>\n'
        text += '<div class="header">\n'
        text += '    <span class="left">KW 38</span>\n'
        text += '    <span class="center"><strong>2020</strong> | 7528</span>\n'
        text += '    <span class="right"></span>\n'
        text += '</div>\n'
        text += '<hr/>\n'
        text += '<div class="greg">\n'
        text += '14 Montag\n'
        text += '</div>\n'
        text += '<div class="square god">\n'
        text += '35 Gottestag\n'
        text += '</div>\n'
        text += '<hr/>\n'
        text += '<div class="greg">\n'
        text += '15 Dienstag\n'
        text += '</div>\n'
        text += '<div class="square moon">\n'
        text += '36 Mondtag\n'
        text += '</div>\n'
        text += '<hr/>\n'
        text += '<div class="greg">\n'
        text += '16 Mittwoch\n'
        text += '</div>\n'
        text += '<div class="square ocean">\n'
        text += '37 Ozeantag\n'
        text += '</div>\n'
        text += '<hr/>\n'
        text += '<div class="greg">\n'
        text += '17 Donnerstag\n'
        text += '</div>\n'
        text += '<div class="square heaven">\n'
        text += '38 Himmelstag\n'
        text += '</div>\n'
        text += '<hr/>\n'
        text += '<div class="greg">\n'
        text += '18 Freitag\n'
        text += '</div>\n'
        text += '<div class="square tree">\n'
        text += '39 Baumtag\n'
        text += '</div>\n'
        text += '<div class="header">\n'
        text += '    <span class="left">KW 39</span>\n'
        text += '    <span class="center"><strong>2020</strong> | 7528</span>\n'
        text += '    <span class="right"></span>\n'
        text += '</div>\n'
        text += '<hr/>\n'
        text += '<div class="greg">\n'
        text += '19 Samstag\n'
        text += '</div>\n'
        text += '<div class="square sun">\n'
        text += '40 Sonnentag\n'
        text += '</div>\n'
        text += '<hr/>\n'
        text += '<div class="greg">\n'
        text += '20 Montag\n'
        text += '</div>\n'
        text += '<div class="square fire">\n'
        text += '41 Feuertag\n'
        text += '</div>\n'
        text += '<hr/>\n'
        text += '<div class="greg">\n'
        text += '21 Dienstag\n'
        text += '</div>\n'
        text += '<div class="square star">\n'
        text += '42 Sterntag\n'
        text += '</div>\n'
        text += '<hr/>\n'
        text += '<div class="greg">\n'
        text += '22 Mittwoch\n'
        text += '</div>\n'
        text += '<div class="square earth">\n'
        text += '43 Erdtag\n'
        text += '</div>\n'
        text += '<hr/>\n'
        text += '<div class="square note">\n'
        text += 'Notizen\n'
        text += '</div>\n'
        cursor.insertText(text)
        cursor.setPosition(pos)
        self.text_edit.setTextCursor(cursor)
