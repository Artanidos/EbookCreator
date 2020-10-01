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

from datetime import datetime, date, timedelta
from interfaces import GeneratorInterface
from PyQt5.QtWidgets import QWidget, QDialog, QHBoxLayout, QPushButton, QGridLayout, QLabel, QComboBox

class CalendarGenerator(GeneratorInterface):
    def __init__(self):
        QWidget.__init__(self)
        self.display_name = "Calendar"

    def style(self):
        text = "<!-- the caption is only used for the table of contents -->\n"
        text += '<h1 style="visibility: hidden;">Calendar</h1>\n'
        text += '<style>\n'
        text += '.square\n'
        text += '{\n'
        text += '    height: 50px;\n'
        text += '    width: 60px;\n'
        text += '    border-style: solid;\n'
        text += '    border-width: 1px;\n'
        text += '    border-color: #000000;\n'
        text += '    margin: 5px;\n'
        text += '    padding: 10px;\n'
        text += '    text-align: center;\n'
        text += '}\n'
        text += '.square span\n'
        text += '{\n'
        text += '    font-size: 30px;\n'
        text += '    font-weight: bold;\n'
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
        text += '    background-color: #ff6bcd;\n'
        text += '}\n'
        text += '.ocean\n'
        text += '{\n'
        text += '    background-color: #a7a7ff;\n'
        text += '}\n'
        text += '.heaven\n'
        text += '{\n'
        text += '    background-color: #96ffff;\n'
        text += '}\n'
        text += '.tree\n'
        text += '{\n'
        text += '    page-break-after: always;\n'
        text += '    background-color: #94ff94;\n'
        text += '}\n'
        text += '.sun\n'
        text += '{\n'
        text += '    background-color: #ffff7d;\n'
        text += '}\n'
        text += '.fire\n'
        text += '{\n'
        text += '    background-color: #ffad78;\n'
        text += '}\n'
        text += '.star\n'
        text += '{\n'
        text += '    background-color: #ff8a8a;\n'
        text += '}\n'
        text += '.earth\n'
        text += '{\n'
        text += '    background-color: #b8b8b8;\n'
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
        text += '</style>\n'
        return text

    def header(self, date):
        text = '<div class="header">\n'
        text += '    <span class="center"><strong>' + str(date.year + 5509) + '</strong> | ' + str(date.year) + '</span>\n'
        text += '</div>\n'
        text += '<hr/>\n'
        return text

    def menu_action(self):
        dlg = CalendarDialog(parent=self)
        dlg.exec()
        if not dlg.result:
            return
        day, month, year = dlg.getData()
        actdate = date(year, month, day)
        lastdate = date(year + 1, 12, 31)
        daysPerMonth = 41
        cursor = self.text_edit.textCursor()
        pos = cursor.position()
        text = self.style()
        sday = 1
        dayInWeek = 1
        days = abs((lastdate - actdate).days) + 1
        #days = 18
        for weeks in range(1, days + 1):
            if dayInWeek == 1:
                text += self.header(actdate)
                text += '<div class="greg">\n'
                text += str(actdate.day) + ' ' + actdate.strftime("%A") + '\n'
                text += '</div>\n'
                text += '<div class="square god">\n'
                text += '<span>' + str(sday) + '</span></br>Hors\n'
                text += '</div>\n'
                text += '<hr/>\n'
            elif dayInWeek == 2:
                text += '<div class="greg">\n'
                text += str(actdate.day) + ' ' + actdate.strftime("%A") + '\n'
                text += '</div>\n'
                text += '<div class="square moon">\n'
                text += '<span>' + str(sday) + '</span></br>Orea\n'
                text += '</div>\n'
                text += '<hr/>\n'
            elif dayInWeek == 3:
                text += '<div class="greg">\n'
                text += str(actdate.day) + ' ' + actdate.strftime("%A") + '\n'
                text += '</div>\n'
                text += '<div class="square ocean">\n'
                text += '<span>' + str(sday) + '</span></br>Perun\n'
                text += '</div>\n'
                text += '<hr/>\n'
            elif dayInWeek == 4:
                text += '<div class="greg">\n'
                text += str(actdate.day) + ' ' + actdate.strftime("%A") + '\n'
                text += '</div>\n'
                text += '<div class="square heaven">\n'
                text += '<span>' + str(sday) + '</span></br>Waruna\n'
                text += '</div>\n'
                text += '<hr/>\n'
            elif dayInWeek == 5:
                text += '<div class="greg">\n'
                text += str(actdate.day) + ' ' + actdate.strftime("%A") + '\n'
                text += '</div>\n'
                text += '<div class="square tree">\n'
                text += '<span>' + str(sday) + '</span></br>Indra\n'
                text += '</div>\n'
                text += '<div class="header">\n'
                text += '    <span class="center"><strong>' + actdate.strftime("%B") + '</strong></span>\n'
                text += '</div>\n'
                text += '<hr/>\n'
            elif dayInWeek == 6:
                text += '<div class="greg">\n'
                text += str(actdate.day) + ' ' + actdate.strftime("%A") + '\n'
                text += '</div>\n'
                text += '<div class="square sun">\n'
                text += '<span>' + str(sday) + '</span></br>Stribog\n'
                text += '</div>\n'
                text += '<hr/>\n'
            elif dayInWeek == 7:
                text += '<div class="greg">\n'
                text += str(actdate.day) + ' ' + actdate.strftime("%A") + '\n'
                text += '</div>\n'
                text += '<div class="square fire">\n'
                text += '<span>' + str(sday) + '</span></br>Dea\n'
                text += '</div>\n'
                text += '<hr/>\n'
            elif dayInWeek == 8:
                text += '<div class="greg">\n'
                text += str(actdate.day) + ' ' + actdate.strftime("%A") + '\n'
                text += '</div>\n'
                text += '<div class="square star">\n'
                text += '<span>' + str(sday) + '</span></br>Merzana\n'
                text += '</div>\n'
                text += '<hr/>\n'
            elif dayInWeek == 9:
                text += '<div class="greg">\n'
                text += str(actdate.day) + ' ' + actdate.strftime("%A") + '\n'
                text += '</div>\n'
                text += '<div class="square earth">\n'
                text += '<span>' + str(sday) + '</span></br>Jarilo\n'
                text += '</div>\n'
                text += '<hr/>\n'
                text += '<div class="square note">\n'
                text += 'Notizen\n'
                text += '</div>\n'
            actdate = actdate + timedelta(1)
            sday += 1
            if sday > daysPerMonth:
                sday = 1
                if daysPerMonth == 41:
                    daysPerMonth = 40
                else:
                    daysPerMonth = 41
            dayInWeek += 1
            if dayInWeek > 9:
                dayInWeek = 1

        cursor.insertText(text)
        cursor.setPosition(pos)
        self.text_edit.setTextCursor(cursor)


class CalendarDialog(QDialog):
    def __init__(self, parent=None):
        super(CalendarDialog, self).__init__(parent)
        self.result = False
        self.setWindowTitle("EbookCreator - Calendar")
        box = QHBoxLayout()
        self.ok = QPushButton("Ok")
        self.cancel = QPushButton("Cancel")
        box.addStretch()
        box.addWidget(self.ok)
        box.addWidget(self.cancel)
        layout = QGridLayout()
        ay = datetime.now().year
        am = datetime.now().month
        ad = datetime.now().day
        self.day = QComboBox()
        for d in range(1, 32):
            self.day.addItem(str(d))
        self.day.setCurrentText("21")
        self.month = QComboBox()
        for m in range(1, 13):
            self.month.addItem(str(m))
        self.month.setCurrentText("9")
        self.year = QComboBox()
        for y in range(ay - 100, ay + 50):
            self.year.addItem(str(y))
        self.year.setCurrentText("2020")
        
        layout.addWidget(QLabel("Please insert the first day of the calendar"), 0, 0, 1, 4)
        layout.addWidget(QLabel("  Day"), 1, 0)
        layout.addWidget(self.day, 1, 3, 1, 4)
        layout.addWidget(QLabel("  Month"), 2, 0)
        layout.addWidget(self.month, 2, 3, 1, 4)
        layout.addWidget(QLabel("  Year"), 3, 0)
        layout.addWidget(self.year, 3, 3, 1, 4)
        layout.addLayout(box, 4, 0, 1, 7)
        self.setLayout(layout)

        self.ok.clicked.connect(self.okClicked)
        self.cancel.clicked.connect(self.close)

    def okClicked(self):
        self.result = True
        self.close()

    def getData(self):
        return (int(self.day.currentText()), 
        int(self.month.currentText()), 
        int(self.year.currentText()))