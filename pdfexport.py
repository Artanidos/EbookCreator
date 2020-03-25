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
from tempfile import mkdtemp
from generator import addLineNumbers
from jinja2 import Template
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
        toc, htm, html = generateParts(book, html)
        html += generateToc(book, toc)
        html += "<p style=\"page-break-before: always\">"
        html += htm
        html += "\n</body>\n</html>"
        h = HTML(string=html)
        css = CSS(string='@page { size: A5; margin: 0cm }')
        h.write_pdf(filename, stylesheets=[css])
        QApplication.restoreOverrideCursor()
        self.status_bar.showMessage("Ready")

def generateParts(book, xhtml):
    toc = []
    item = {}
    item["href"] = "toc.xhtml"
    item["name"] = "Table of Contents"
    item["id"] = "nav"
    item["parts"] = []
    toc.append(item)

    partNo = 1
    html = ""
    for part in book._parts:
        with open(os.path.join(book.source_path, "parts", part.src), "r") as i:
            text = i.read()
        name = part.name.replace(" ", "-").lower()
        htm = fixTables(markdown(text, html4tags = False, extras=["fenced-code-blocks", "wiki-tables", "tables", "header-ids"]))
        list = getLinks(htm, name)
        for item in list:
            toc.append(item)
        htm = addLineNumbers(htm)
        # fix img tags
        book.source_path
        htm = htm.replace("../images", "file://" + os.path.join(book.source_path, "images"))
        if partNo < len(book._parts):
            htm += "<p style=\"page-break-before: always\">"
        # should be true for cover page
        if part.pdfOnly:
            xhtml += htm
        else:
            html += htm
        partNo += 1
        
    return toc, html, xhtml

def fixTables(text):
    text = text.replace("<th align=\"center\"", "<th class=\"center\"")
    text = text.replace("<th align=\"right\"", "<th class=\"right\"")
    text = text.replace("<th align=\"left\"", "<th class=\"left\"")
    text = text.replace("<td align=\"center\"", "<td class=\"center\"")
    text = text.replace("<td align=\"right\"", "<td class=\"right\"")
    text = text.replace("<td align=\"left\"", "<td class=\"left\"")
    return text

def getLinks(text, part_name):
    nodes = []
    list = []
    for line in text.split("\n"):
        if not line:
            continue
        if line.startswith("<h1 "):
            c = 1
        elif line.startswith("<h2 "):
            c = 2
        elif line.startswith("<h3 "):
            c = 3
        elif line.startswith("<h4 "):
            c = 4
        elif line.startswith("<h5 "):
            c = 5
        elif line.startswith("<h6 "):
            c = 6
        else:
            c = 0
        if c > 0:
            start = line.find("id=")
            end = line.find('"', start + 4)
            id = line[start + 4:end]

            start = line.find(">", end) + 1
            end = line.find("<", start + 1)
            name = line[start:end]
            item = {}
            item["href"] = part_name + ".xhtml#" + id
            item["name"] = name
            item["id"] = id
            item["parts"] = []
            if len(nodes) < c:
                nodes.append(item)
            else:
                nodes[c - 1] = item
            if c == 1:
                list.append(item)
            else:
                nodes[c - 2]["parts"].append(item)
    return list

def generateToc(book, parts):
    path = os.getcwd()
    context = {}
    context["parts"] = parts
    with open(os.path.join(path, "themes", book.theme, "layout", "toc.xhtml"), "r") as fp:
        data = fp.read()
    tmp = Template(data)
    xhtml = tmp.render(context)
    return xhtml
