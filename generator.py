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
import uuid
import datetime
import shutil
import traceback
import sys
from tempfile import mkdtemp
from shutil import rmtree
from markdown2 import markdown
from markupsafe import Markup
from jinja2 import Template
from zipfile import ZipFile
from PyQt5.QtCore import QCoreApplication
from xml.dom.minidom import parseString


def createEpub(output, book, win):
    dir = mkdtemp()
    guid = str(uuid.uuid4())
    copyAssets(dir, book.theme)
    os.mkdir(os.path.join(dir, "EPUB", "parts"))
    os.mkdir(os.path.join(dir, "EPUB", "images"))
    os.mkdir(os.path.join(dir, "META-INF"))
    path = os.getcwd()

    copyImages(dir, book)
    writeMimetype(dir)
    writeContainer(dir)

    generatePackage(dir, book, guid)
    toc = generateParts(dir, book)
    generateToc(dir, book, toc)
    generateNcx(dir, book, guid)

    os.chdir(dir)
    files = getAllFiles(dir)
    with ZipFile(output, 'w') as zip:
        for file in files:
            zip.write(file)
    os.chdir(path)
    rmtree(dir)
    win.statusBar().showMessage("Ready")


def getAllFiles(dir):
    file_paths = []
    for root, directories, files in os.walk(dir):
        for filename in files:
            if root == dir:
                filepath = filename
            else:
                filepath = os.path.join(root[len(dir) + 1:], filename)
            file_paths.append(filepath)
    return file_paths


def writeMimetype(dir):
    with open(os.path.join(dir, "mimetype"), "w") as f:
        f.write("application/epub+zip")


def writeContainer(dir):
    midir = os.path.join(dir, "META-INF")
    with open(os.path.join(midir, "container.xml"), "w") as f:
        f.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>")
        f.write("<container xmlns=\"urn:oasis:names:tc:opendocument:xmlns:container\" version=\"1.0\">")
        f.write("  <rootfiles>")
        f.write("    <rootfile full-path=\"EPUB/package.opf\" media-type=\"application/oebps-package+xml\"/>")
        f.write("  </rootfiles>")
        f.write("</container>")


def generatePackage(dir, book, uuid):
    context = {}
    context["uuid"] = uuid
    context["lang"] = book.language
    context["title"] = book.name
    context["date"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    context["version"] = QCoreApplication.applicationVersion()
    context["creator"] = book.creator
    items = []
    spine = []

    for part in book._parts:
        item = {}
        name = part.name.replace(" ", "-").lower()
        item["href"] = os.path.join("parts", name + ".xhtml")
        item["id"] = name
        item["type"] = "application/xhtml+xml"
        items.append(item)
        spine.append(name)

    for root, dirs, files in os.walk(os.path.join(dir, "EPUB", "images")):
        for file in files:
            filename, extension = os.path.splitext(file)
            item = {}
            item["href"] = os.path.join("images", file)
            item["id"] = filename
            item["type"] = "image/" + extension[1:]
            items.append(item)

    context["items"] = items
    context["spine"] = spine
    path = os.getcwd()
    with open(os.path.join(path, "themes", book.theme, "layout", "package.opf"), "r") as fp:
        data = fp.read()
    tmp = Template(data)
    xml = tmp.render(context)
    with open(os.path.join(dir, "EPUB", "package.opf"), "w") as f:
        f.write(xml)


def fixTables(text):
    text = text.replace("<th align=\"center\"", "<th class=\"center\"")
    text = text.replace("<th align=\"right\"", "<th class=\"right\"")
    text = text.replace("<th align=\"left\"", "<th class=\"left\"")
    text = text.replace("<td align=\"center\"", "<td class=\"center\"")
    text = text.replace("<td align=\"right\"", "<td class=\"right\"")
    text = text.replace("<td align=\"left\"", "<td class=\"left\"")
    return text


def generateParts(dir, book):
    toc = []
    item = {}
    item["href"] = "toc.xhtml"
    item["name"] = "Table of Contents"
    item["id"] = "nav"
    item["parts"] = []
    toc.append(item)
    path = os.getcwd()
    for part in book._parts:
        context = {}
        with open(os.path.join(book.source_path, "parts", part.src), "r") as i:
            text = i.read()
        name = part.name.replace(" ", "-").lower()
        html = fixTables(markdown(text, html4tags = False, extras=["fenced-code-blocks", "wiki-tables", "tables", "header-ids"]))
        list = getLinks(html, name)
        for item in list:
            toc.append(item)
        context["content"] = html
        with open(os.path.join(path, "themes", book.theme, "layout", "template.xhtml")) as fp:
            data = fp.read()
        tmp = Template(data)
        xhtml = tmp.render(context)
        xhtml = addLineNumbers(xhtml)
        with open(os.path.join(dir, "EPUB", "parts", name + ".xhtml"), "w") as f:
                f.write(xhtml)
    return toc


def addLineNumbers(html):
    pos = 0
    ret = ""
    end = 0
    while True:
        old_pos = pos
        pos = html.find("<code>", pos + 1)
        if pos < 0:
            break
        end = html.find("</code>", pos + 6)
        inner = html[pos + 6:end - 1]
        ret += html[old_pos:pos] + "<code>"
        pos = end
        line_no = 1
        lines = inner.split("\n")
        for line in lines:
            if len(lines) > 1:
                ret += "<span class=\"line-number\"><span>" + str(line_no) + "</span></span> " + line + "\n"
            else:
                ret += line + "\n"
            line_no += 1
    ret += html[end:]

    return ret


def copyAssets(dir, theme):
    path = os.getcwd()
    shutil.copytree(os.path.join(path, "themes", theme, "assets"), os.path.join(dir, "EPUB"))


def copyImages(dir, book):
    for root, dirs, files in os.walk(os.path.join(book.source_path, "images")):
        for file in files:
            shutil.copy(os.path.join(book.source_path, "images", file), os.path.join(dir, "EPUB", "images"))


def countHash(text):
    count = 0
    for letter in text:
        if letter == "#":
            count += 1
        else:
            break
    return count


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


def generateToc(dir, book, parts):
    path = os.getcwd()
    context = {}
    context["parts"] = parts
    with open(os.path.join(path, "themes", book.theme, "layout", "toc.xhtml"), "r") as fp:
        data = fp.read()
    tmp = Template(data)
    xhtml = tmp.render(context)
    with open(os.path.join(dir, "EPUB", "parts", "toc.xhtml"), "w") as f:
        f.write(xhtml)


def generateNcx(dir, book, uuid):
    items = []
    context = {}
    context["title"] = book.name
    context["uuid"] = uuid
    order = 0
    for part in book._parts:
        order += 1
        item = {}
        name = part.name.replace(" ", "-")
        item["href"] = os.path.join("parts", name.lower() + ".xhtml")
        item["id"] = "navPoint-" + str(order)
        item["name"] = name
        item["order"] = str(order)
        items.append(item)
    context["items"] = items

    try:
        path = os.getcwd()
        with open(os.path.join(path, "themes", book.theme, "layout", "toc.ncx")) as fp:
            data = fp.read()
        tmp = Template(data)
        xhtml = tmp.render(context)
        with open(os.path.join(dir, "EPUB", "toc.ncx"), "w") as f:
            f.write(xhtml)
    except:
        traceback.print_exc(file=sys.stdout)