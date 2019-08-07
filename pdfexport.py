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
from pathlib import Path
from markdown2 import markdown
from generator import addLineNumbers
from PyQt5.QtWebEngineWidgets import QWebEnginePage
from PyQt5.QtGui import QPageLayout, QPageSize
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QUrl


class PdfExport():
    def __init__(self, filename, book, status_bar):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.filename = filename
        self.status_bar = status_bar
        
        html = "<html>\n<head>\n"
        html += "<link href=\"../css/pastie.css\" rel=\"stylesheet\" type=\"text/css\"/>\n"
        html += "<link href=\"../css/stylesheet.css\" rel=\"stylesheet\" type=\"text/css\"/>\n"
        html += "</head>\n<body>\n"
        for part in book._parts:
            self.status_bar.showMessage("Processing " + part.name)
            with open(os.path.join(book.source_path, "parts", part.src), "r") as i:
                text = i.read()
                htm = markdown(text, html4tags = False, extras=["fenced-code-blocks", "wiki-tables", "tables", "header-ids"])
                htm = addLineNumbers(htm)
                html += htm
        html += "\n</body>\n</html>"

        self.status_bar.showMessage("Loading HTML")
        self.page = QWebEnginePage()
        self.page.loadFinished.connect(self.loadFinished)
        self.page.pdfPrintingFinished.connect(self.printFinished)
        self.page.setHtml(html, QUrl(Path(os.path.join(book.source_path, "parts", "index.html")).as_uri()))

    def loadFinished(self, ok):
        if ok:
            self.status_bar.showMessage("Printing PDF")
            self.page.printToPdf(self.filename, pageLayout=QPageLayout(QPageSize(QPageSize.A5), QPageLayout.Portrait, QMarginsF(30.0, 30.0, 30.0, 30.0)))
        else:
            self.status_bar.showMessage("There was an error printing the PDF")

    def printFinished(self, filename, success):
        QApplication.restoreOverrideCursor()
        if success:
            self.status_bar.showMessage("PDF created")
        else:
            self.status_bar.showMessage("There was an error printing the PDF")