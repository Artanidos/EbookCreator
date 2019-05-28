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
from tempfile import mkdtemp
from shutil import rmtree
from markdown2 import markdown
from django.template import Context, Engine
from django.utils.safestring import mark_safe
from zipfile import ZipFile
from PyQt5.QtCore import QCoreApplication


def createEpub(output, book, win):
    dir = mkdtemp()
    guid = str(uuid.uuid4())
    copyAssets(dir, book.theme)
    os.mkdir(os.path.join(dir, "OEBPS", "parts"))
    os.mkdir(os.path.join(dir, "OEBPS", "images"))
    os.mkdir(os.path.join(dir, "META-INF"))
    path = os.getcwd()

    copyImages(dir, book)
    writeMimetype(dir)
    writeContainer(dir)
    generatePackage(dir, book, guid)
    generateParts(dir, book)
    generateToc(dir, book)
    generateTocNcx(dir, book, guid)

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
        f.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
        f.write("<container xmlns=\"urn:oasis:names:tc:opendocument:xmlns:container\" version=\"1.0\">\n")
        f.write("    <rootfiles>\n")
        f.write("        <rootfile full-path=\"OEBPS/package.opf\" media-type=\"application/oebps-package+xml\"/>\n")
        f.write("    </rootfiles>\n")
        f.write("</container>\n")


def generatePackage(dir, book, uuid):
    context = {}
    context["uuid"] = uuid
    context["lang"] = book.language
    context["title"] = book.name
    context["date"] = datetime.datetime.now().strftime("%Y-%m-%d")
    context["version"] = QCoreApplication.applicationVersion()
    context["creator"] = book.creator
    context["publisher"] = book.publisher
    items = []
    spine = ["toc"]
    item = {}
    item["href"] = os.path.join("parts", "toc.xhtml")
    item["id"] = "toc"
    item["type"] = "application/xhtml+xml"
    items.append(item)

    for part in book._parts:
        item = {}
        item["href"] = os.path.join("parts", part.name + ".xhtml")
        item["id"] = part.name
        item["type"] = "application/xhtml+xml"
        items.append(item)
        spine.append(part.name)

    for root, dirs, files in os.walk(os.path.join(dir, "OEBPS", "images")):
        for file in files:
            filename, extension = os.path.splitext(file)
            item = {}
            item["href"] = os.path.join("images", file)
            item["id"] = filename
            item["type"] = "image/" + extension[1:]
            items.append(item)

    context["spine"] = ["nav", "toc"]
    context["items"] = items
    context["spine"] = spine
    path = os.getcwd()
    dirs = [
        path + "/themes/" + book.theme + "/layout",
    ]
    eng = Engine(dirs = dirs, debug = False)
    xml = eng.render_to_string("package.opf", context = context)
    with open(os.path.join(dir, "OEBPS", "package.opf"), "w") as f:
        f.write(xml)


def generateParts(dir, book):
    path = os.getcwd()
    dirs = [
        path + "/themes/" + book.theme + "/layout",
    ]
    eng = Engine(dirs = dirs, debug = False)
    for part in book._parts:
        context = {}
        with open(os.path.join(book.source_path, "parts", part.src), "r") as i:
            text = i.read()
        context["content"] = mark_safe(markdown(text, html4tags = False, extras=["fenced-code-blocks", "tables"]))
        xhtml = eng.render_to_string("template.xhtml", context = context)
        with open(os.path.join(dir, "OEBPS", "parts", part.name + ".xhtml"), "w") as f:
                f.write(xhtml)


def copyAssets(dir, theme):
    path = os.getcwd()
    shutil.copytree(os.path.join(path, "themes", theme, "assets"), os.path.join(dir, "OEBPS"))


def copyImages(dir, book):
    for root, dirs, files in os.walk(os.path.join(book.source_path, "images")):
        for file in files:
            shutil.copy(os.path.join(book.source_path, "images", file), os.path.join(dir, "OEBPS", "images"))


def generateToc(dir, book):
    path = os.getcwd()
    parts = []
    toc = {}
    toc["href"] = "toc.xhtml"
    toc["name"] = "Toc"
    parts.append(toc)
    context = {}
    for part in book._parts:
        item = {}
        item["href"] = part.name + ".xhtml"
        item["name"] = part.name
        parts.append(item)

    context["parts"] = parts
    dirs = [
        path + "/themes/" + book.theme + "/layout",
    ]
    eng = Engine(dirs = dirs, debug = False)
    xhtml = eng.render_to_string("toc.xhtml", context = context)
    with open(os.path.join(dir, "OEBPS", "parts", "toc.xhtml"), "w") as f:
        f.write(xhtml)


def generateTocNcx(dir, book, uuid):
    order = 0
    path = os.getcwd()
    parts = []
    toc = {}
    toc["href"] = os.path.join("parts", "toc.xhtml")
    toc["id"] = "navPoint-" + str(order)
    toc["label"] = "Toc"
    toc["order"] = str(order)
    order = order + 1
    parts.append(toc)
    context = {}
    context["uuid"] = uuid
    context["title"] = book.name
    for part in book._parts:
        item = {}
        item["href"] = os.path.join("parts", part.name + ".xhtml")
        item["id"] = "navPoint-" + str(order)
        item["label"] = part.name
        item["order"] = str(order)
        parts.append(item)
        order = order + 1

    context["navs"] = parts
    dirs = [
        path + "/themes/" + book.theme + "/layout",
    ]
    eng = Engine(dirs = dirs, debug = False)
    xhtml = eng.render_to_string("toc.ncx", context = context)
    with open(os.path.join(dir, "OEBPS", "toc.ncx"), "w") as f:
        f.write(xhtml)
