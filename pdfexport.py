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
from PyQt5.QtWidgets import QApplication, QFileDialog 
from PyQt5.QtCore import Qt, QUrl
from weasyprint import HTML, CSS


class PdfExport():
    def __init__(self, book, status_bar):
        self.status_bar = status_bar
        self.install_directory = os.getcwd()

        filename = ""
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setNameFilter("PDF (*.pdf);;All (*)")
        dialog.setWindowTitle("Create PDF")
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setDirectory(book.source_path)
        dialog.setDefaultSuffix("pdf")
        if dialog.exec_():
            filename = dialog.selectedFiles()[0]
        del dialog
        if not filename:
            return
        
        QApplication.setOverrideCursor(Qt.WaitCursor)
        html = "<html>\n<head>\n"
        html += "<link href=\"file://" + os.path.join(book.source_path, "css", "pastie.css") + "\" rel=\"stylesheet\" type=\"text/css\"/>\n"
        html += "<link href=\"file://" + os.path.join(book.source_path, "css", "stylesheet.css") + "\" rel=\"stylesheet\" type=\"text/css\"/>\n"
        html += "</head>\n<body>\n"
        partNo = 1
        for part in book._parts:
            self.status_bar.showMessage("Processing " + part.name)
            with open(os.path.join(book.source_path, "parts", part.src), "r") as i:
                text = i.read()
                htm = markdown(text, html4tags = False, extras=["fenced-code-blocks", "wiki-tables", "tables", "header-ids"])
                htm = addLineNumbers(htm)
                # fix img tags
                book.source_path
                html += htm.replace("../images", "file://" + os.path.join(book.source_path, "images"))
                if partNo < len(book._parts):
                    html += "<p style=\"page-break-before: always\">"
                partNo += 1
        html += "\n</body>\n</html>"
        h = HTML(string=html)
        css = CSS(string='@page { size: A5; margin: 0cm }')
        h.write_pdf(filename, stylesheets=[css])
        self.status_bar.showMessage("Ready")
        QApplication.restoreOverrideCursor()