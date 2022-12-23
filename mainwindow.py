#############################################################################
# Copyright (C) 2022 Olaf Japp
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
from pathlib import Path
from shutil import copy
from autocorrect import Speller
import inspect
from threading import Thread, Lock
from markdown2 import markdown
from importlib import import_module
from PyQt5.QtCore import (QByteArray, QCoreApplication, QPropertyAnimation,
                          QSettings, Qt, QUrl, QSize, pyqtSignal, QMarginsF)
from PyQt5.QtGui import (QColor, QFont, QIcon, QKeySequence, QPalette,
                         QTextCursor, QImage, QPixmap)
from PyQt5.QtQml import QQmlComponent, QQmlEngine
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import (QAction, QApplication, QDialog, QDockWidget,
                             QFileDialog, QHBoxLayout, QLineEdit, QListWidget,
                             QListWidgetItem, QMainWindow, QMessageBox,
                             QScrollArea, QSizePolicy, QSplitter, QProxyStyle,
                             QStyleFactory, QTextEdit, QVBoxLayout, QWidget, QStyle)

from ebook import Ebook
from expander import Expander
from flatbutton import FlatButton
from plugin import Plugins
from generator import createEpub, addLineNumbers
from hyperlink import HyperLink
from markdownedit import MarkdownEdit
from projectwizard import ProjectWizard
from settings import Settings
from dark import DarkFusion
from settingsdialog import SettingsDialog
from pdfexport import PdfExport
from interfaces import GeneratorInterface
from plugins.calendar import CalendarGenerator

import resources


class MainWindow(QMainWindow):
    htmlReady = pyqtSignal(str)

    def __init__(self, app):
        QMainWindow.__init__(self)
        self.install_directory = os.getcwd()

        self.app = app
        self.book = None
        self.last_book = ""
        self.filename = ""
        self._part_is_new = False
        self.tread_running = False
        self.initTheme()
        self.createUi()
        self.loadPlugins()
        self.createMenus()
        self.createStatusBar()
        self.readSettings()
        
        self.text_edit.textChanged.connect(self.textChanged)

    def initTheme(self):
        settings = QSettings(QSettings.IniFormat, QSettings.UserScope, QCoreApplication.organizationName(), QCoreApplication.applicationName())
        self.theme = settings.value("theme", "DarkFusion")
        hilite_color = settings.value("hiliteColor", self.palette().highlight().color().name())
        self.changeStyle(self.theme, hilite_color)

    def showEvent(self, event):
        if self.last_book:
            self.loadBook(self.last_book)

    def changeStyle(self, theme, hilite_color):
        self.theme = theme
        if theme == "DarkFusion":
            QApplication.setStyle(DarkFusion(hilite_color))
        else:
            QApplication.setStyle(QStyleFactory.create(theme))
            pal = self.app.palette()
            pal.setColor(QPalette.Highlight, QColor(hilite_color))
            self.app.setPalette(pal)

    def createUi(self):
        self.content = Expander("Content", ":/images/parts.svg")
        self.images = Expander("Images", ":/images/images.svg")
        self.settings = Expander("Settings", ":/images/settings.svg")

        self.setWindowTitle(QCoreApplication.applicationName() + " " + QCoreApplication.applicationVersion())
        vbox = QVBoxLayout()
        vbox.addWidget(self.content)
        vbox.addWidget(self.images)
        vbox.addWidget(self.settings)
        vbox.addStretch()

        self.content_list = QListWidget()
        self.content_list.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        content_box = QVBoxLayout()
        content_box.addWidget(self.content_list)
        self.item_edit = QLineEdit()
        self.item_edit.setMaximumHeight(0)
        self.item_edit.editingFinished.connect(self.editItemFinished)
        self.item_anim = QPropertyAnimation(self.item_edit, "maximumHeight".encode("utf-8"))
        content_box.addWidget(self.item_edit)
        button_layout = QHBoxLayout()
        plus_button = FlatButton(":/images/plus.svg")
        self.edit_button = FlatButton(":/images/edit.svg")
        self.trash_button = FlatButton(":/images/trash.svg")
        self.up_button = FlatButton(":/images/up.svg")
        self.down_button = FlatButton(":/images/down.svg")
        self.trash_button.enabled = False
        self.up_button.enabled = False
        self.down_button.enabled = False
        button_layout.addWidget(plus_button)
        button_layout.addWidget(self.up_button)
        button_layout.addWidget(self.down_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.trash_button)
        content_box.addLayout(button_layout)
        self.content.addLayout(content_box)
        plus_button.clicked.connect(self.addPart)
        self.trash_button.clicked.connect(self.dropPart)
        self.up_button.clicked.connect(self.partUp)
        self.down_button.clicked.connect(self.partDown)
        self.edit_button.clicked.connect(self.editPart)

        self.image_list = QListWidget()
        self.image_list.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        image_box = QVBoxLayout()
        image_box.addWidget(self.image_list)
        image_button_layout = QHBoxLayout()
        image_plus_button = FlatButton(":/images/plus.svg")
        self.image_trash_button = FlatButton(":/images/trash.svg")
        self.image_trash_button.enabled = False
        image_button_layout.addWidget(image_plus_button)
        image_button_layout.addWidget(self.image_trash_button)
        image_box.addLayout(image_button_layout)
        self.images.addLayout(image_box)
        image_plus_button.clicked.connect(self.addImage)
        self.image_trash_button.clicked.connect(self.dropImage)

        scroll_content = QWidget()
        scroll_content.setLayout(vbox)
        scroll = QScrollArea()
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setWidget(scroll_content)
        scroll.setWidgetResizable(True)
        scroll.setMaximumWidth(200)
        scroll.setMinimumWidth(200)

        self.navigationdock = QDockWidget("Navigation", self)
        self.navigationdock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.navigationdock.setWidget(scroll)
        self.navigationdock.setObjectName("Navigation")
        self.addDockWidget(Qt.LeftDockWidgetArea, self.navigationdock)

        self.splitter = QSplitter()
        self.text_edit = MarkdownEdit()
        self.text_edit.setFont(QFont("Courier", 15)) # 11 on Linux
        self.preview = QWebEngineView()
        self.preview.setMinimumWidth(300)
        self.setWindowTitle(QCoreApplication.applicationName())

        self.splitter.addWidget(self.text_edit)
        self.splitter.addWidget(self.preview)
        self.setCentralWidget(self.splitter)

        self.content.expanded.connect(self.contentExpanded)
        self.images.expanded.connect(self.imagesExpanded)
        self.settings.expanded.connect(self.settingsExpanded)
        self.settings.clicked.connect(self.openSettings)
        self.content_list.currentItemChanged.connect(self.partSelectionChanged)
        self.image_list.currentItemChanged.connect(self.imageSelectionChanged)
        self.image_list.itemDoubleClicked.connect(self.insertImage)

        self.text_edit.undoAvailable.connect(self.undoAvailable)
        self.text_edit.redoAvailable.connect(self.redoAvailable)
        self.text_edit.copyAvailable.connect(self.copyAvailable)

        QApplication.clipboard().dataChanged.connect(self.clipboardDataChanged)

    def undoAvailable(self, value):
        self.undo_act.setEnabled(value)

    def redoAvailable(self, value):
        self.redo_act.setEnabled(value)

    def copyAvailable(self, value):
        self.copy_act.setEnabled(value)
        self.cut_act.setEnabled(value)

    def clipboardDataChanged(self):
        md = QApplication.clipboard().mimeData()
        self.paste_act.setEnabled(md.hasText())

    def openSettings(self):
        dlg = Settings(self.book, self.install_directory)
        dlg.exec()
        if dlg.saved:
            self.setWindowTitle(QCoreApplication.applicationName() + " - " + self.book.name)

    def addPart(self):
        self.item_edit.setText("")
        self.item_edit.setFocus()
        self.item_anim.setStartValue(0)
        self.item_anim.setEndValue(23)
        self.item_anim.start()
        self._part_is_new = True

    def addItem(self):
        text = self.item_edit.text()
        if text:
            if not self.book.getPart(text):
                self.book.addPart(text)
                self.loadBook(self.last_book)

    def updateItem(self):
        text = self.item_edit.text()
        if text:
            if not self.book.getPart(text):
                self.book.updatePart(self.content_list.currentItem().data(1).name, text)
                self.loadBook(self.last_book)

    def editItemFinished(self):
        if self._part_is_new:
            self.addItem()
        else:
            self.updateItem()
        self.item_anim.setStartValue(23)
        self.item_anim.setEndValue(0)
        self.item_anim.start()

    def editPart(self):
        item = self.content_list.currentItem().data(1).name
        self.item_edit.setText(item)
        self.item_edit.setFocus()
        self.item_anim.setStartValue(0)
        self.item_anim.setEndValue(23)
        self.item_anim.start()
        self._part_is_new = False

    def dropPart(self):
        item = self.content_list.currentItem().data(1).name
        msgBox = QMessageBox()
        msgBox.setText("You are about to delete the part <i>" + item + "</i>")
        msgBox.setInformativeText("Do you really want to delete the item?")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        msgBox.setDefaultButton(QMessageBox.Cancel)
        ret = msgBox.exec()
        if ret == QMessageBox.Yes:
            self.book.dropPart(item)
            self.loadBook(self.last_book)

    def addImage(self):
        fileName = ""
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setNameFilter("Image Files(*.png *.jpg *.bmp *.gif);;All (*)")
        dialog.setWindowTitle("Load Image")
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        dialog.setAcceptMode(QFileDialog.AcceptOpen)
        if dialog.exec_():
            fileName = dialog.selectedFiles()[0]
        del dialog
        if not fileName:
            return

        base = os.path.basename(fileName)
        if not os.path.exists(os.path.join(self.book.source_path, "images", base)):
            copy(fileName, os.path.join(self.book.source_path, "images"))
        item = QListWidgetItem()
        item.setText(Path(fileName).name)
        item.setData(1, os.path.join(self.book.source_path, "images", Path(fileName).name))
        self.image_list.addItem(item)

    def dropImage(self):
        item = self.image_list.currentItem()
        image = item.data(1)
        filename = os.path.join(self.book.source_path, "parts", image)
        os.remove(filename)
        self.loadImages()

    def loadImages(self):
        self.image_list.clear()
        for root, dir, files in os.walk(os.path.join(self.book.source_path, "images")):
            for file in files:
                filename = os.path.join(self.book.source_path, "images", Path(file).name)
                item = QListWidgetItem()
                item.setToolTip("Doubleclick image to insert into text")
                item.setText(Path(file).name)
                item.setData(1, filename)
                self.image_list.addItem(item)

    def partUp(self):
        pos = self.content_list.currentRow()
        item = self.content_list.takeItem(pos)
        self.content_list.insertItem(pos - 1, item)
        self.content_list.setCurrentRow(pos - 1)
        self.book.partUp(item.data(1).name)

    def partDown(self):
        pos = self.content_list.currentRow()
        item = self.content_list.takeItem(pos)
        self.content_list.insertItem(pos + 1, item)
        self.content_list.setCurrentRow(pos + 1)
        self.book.partDown(item.data(1).name)

    def partSelectionChanged(self, item):
        if item:
            part = item.data(1)
            self.filename = os.path.join(self.book.source_path, "parts", part.src)
            with open(self.filename, "r") as f:
                t = f.read()
                self.text_edit.setPlainText(t)
            self.trash_button.enabled = True
            self.up_button.enabled = self.content_list.currentRow() > 0
            self.down_button.enabled = self.content_list.currentRow() < self.content_list.count() - 1
            self.edit_button.enabled = True
        else:
            self.text_edit.setText("")
            self.trash_button.enabled = False
            self.up_button.enabled = False
            self.down_button.enabled = False
            self.edit_button.enabled = False

    def imageSelectionChanged(self, item):
        if item:
            self.image_trash_button.enabled = True
        else:
            self.image_trash_button.enabled = False

    def contentExpanded(self, value):
        if value:
            self.images.setExpanded(False)
            self.settings.setExpanded(False)

    def imagesExpanded(self, value):
        if value:
            self.content.setExpanded(False)
            self.settings.setExpanded(False)

    def appearanceExpanded(self, value):
        if value:
            self.content.setExpanded(False)
            self.images.setExpanded(False)
            self.settings.setExpanded(False)

    def settingsExpanded(self, value):
        if value:
            self.content.setExpanded(False)
            self.images.setExpanded(False)

    def closeEvent(self, event):
        self.writeSettings()
        event.accept()

    def createMenus(self):
        new_icon = QIcon(QPixmap(":/images/new.svg"))
        open_icon = QIcon(QPixmap(":/images/open.svg"))
        book_icon = QIcon(QPixmap(":/images/book.svg"))
        bold_icon = QIcon(QPixmap(":/images/bold.svg"))
        italic_icon = QIcon(QPixmap(":/images/italic.svg"))
        image_icon = QIcon(QPixmap(":/images/image.svg"))
        table_icon = QIcon(QPixmap(":/images/table.svg"))
        á_icon = QIcon(QPixmap(":/images/á.svg"))
        ã_icon = QIcon(QPixmap(":/images/ã.svg"))
        é_icon = QIcon(QPixmap(":/images/é.svg"))
        ê_icon = QIcon(QPixmap(":/images/ê.svg"))
        ó_icon = QIcon(QPixmap(":/images/ó.svg"))

        new_act = QAction(new_icon, "&New", self)
        new_act.setShortcuts(QKeySequence.New)
        new_act.setStatusTip("Create a new ebook project")
        new_act.triggered.connect(self.newFile)
        new_act.setToolTip("Create new ebook project")

        open_act = QAction(open_icon, "&Open", self)
        open_act.setShortcuts(QKeySequence.Open)
        open_act.setStatusTip("Open an existing ebook project")
        open_act.triggered.connect(self.open)
        open_act.setToolTip("Open an existing ebook project")

        book_act = QAction(book_icon, "&Create Book", self)
        book_act.setShortcuts(QKeySequence.SaveAs)
        book_act.setStatusTip("Create an ebook")
        book_act.triggered.connect(self.create)
        book_act.setToolTip("Create an ebook")

        pdf_act = QAction("Create &PDF", self)
        pdf_act.setStatusTip("Create PDF")
        pdf_act.setToolTip("Create PDF")
        pdf_act.triggered.connect(self.pdfExport)

        settings_act = QAction("&Settings", self)
        settings_act.setStatusTip("Open settings dialog")
        settings_act.triggered.connect(self.settingsDialog)
        settings_act.setToolTip("Open settings dialog")

        exit_act = QAction("E&xit", self)
        exit_act.setShortcuts(QKeySequence.Quit)
        exit_act.setStatusTip("Exit the application")
        exit_act.triggered.connect(self.close)

        self.undo_act = QAction("Undo", self)
        self.undo_act.setShortcut(QKeySequence.Undo)
        self.undo_act.setEnabled(False)
        self.undo_act.triggered.connect(self.doUndo)

        self.redo_act = QAction("Redo", self)
        self.redo_act.setShortcut(QKeySequence.Redo)
        self.redo_act.setEnabled(False)
        self.undo_act.triggered.connect(self.doRedo)

        self.cut_act = QAction("Cu&t", self)
        self.cut_act.setShortcut(QKeySequence.Cut)
        self.cut_act.triggered.connect(self.doCut)
        self.cut_act.setEnabled(False)

        self.copy_act = QAction("&Copy", self)
        self.copy_act.setShortcut(QKeySequence.Copy)
        self.copy_act.triggered.connect(self.doCopy)
        self.copy_act.setEnabled(False)

        self.paste_act = QAction("&Paste", self)
        self.paste_act.setShortcut(QKeySequence.Paste)
        self.paste_act.triggered.connect(self.doPaste)
        self.paste_act.setEnabled(False)

        bold_act = QAction(bold_icon, "Bold", self)
        bold_act.setShortcut(Qt.CTRL + Qt.Key_B)
        bold_act.triggered.connect(self.bold)

        italic_act = QAction(italic_icon, "Italic", self)
        italic_act.setShortcut(Qt.CTRL + Qt.Key_I)
        italic_act.triggered.connect(self.italic)

        image_act = QAction(image_icon, "Image", self)
        image_act.setShortcut(Qt.CTRL + Qt.Key_G)
        image_act.triggered.connect(self.insertImage)
        image_act.setToolTip("Insert an image")

        table_act = QAction(table_icon, "Table", self)
        table_act.setShortcut(Qt.CTRL + Qt.Key_T)
        table_act.triggered.connect(self.insertTable)
        table_act.setToolTip("Insert a table")

        á_act = QAction(á_icon, "á", self)
        á_act.triggered.connect(self.insertLetterA1)
        á_act.setToolTip("Insert letter á")

        ã_act = QAction(ã_icon, "ã", self)
        ã_act.triggered.connect(self.insertLetterA2)
        ã_act.setToolTip("Insert letter ã")

        é_act = QAction(é_icon, "é", self)
        é_act.triggered.connect(self.insertLetterE1)
        é_act.setToolTip("Insert letter é")

        ê_act = QAction(ê_icon, "ê", self)
        ê_act.triggered.connect(self.insertLetterE2)
        ê_act.setToolTip("Insert letter ê")

        ó_act = QAction(ó_icon, "ó", self)
        ó_act.triggered.connect(self.insertLetterO1)
        ó_act.setToolTip("Insert letter ó")

        about_act = QAction("&About", self)
        about_act.triggered.connect(self.about)
        about_act.setStatusTip("Show the application's About box")

        spell_act = QAction("&Spellcheck", self)
        spell_act.setShortcut(Qt.CTRL + Qt.Key_P)
        spell_act.triggered.connect(self.spellCheck)
        spell_act.setStatusTip("Spellcheck")

        file_menu = self.menuBar().addMenu("&File")
        file_menu.addAction(new_act)
        file_menu.addAction(open_act)
        file_menu.addAction(book_act)
        file_menu.addAction(pdf_act)
        file_menu.addSeparator()
        file_menu.addAction(settings_act)
        file_menu.addSeparator()
        file_menu.addAction(exit_act)

        edit_menu = self.menuBar().addMenu("&Edit")
        edit_menu.addAction(self.undo_act)
        edit_menu.addAction(self.redo_act)
        edit_menu.addSeparator()
        edit_menu.addAction(self.cut_act)
        edit_menu.addAction(self.copy_act)
        edit_menu.addAction(self.paste_act)

        format_menu = self.menuBar().addMenu("&Format")
        format_menu.addAction(bold_act)
        format_menu.addAction(italic_act)

        insert_menu = self.menuBar().addMenu("&Insert")
        insert_menu.addAction(image_act)
        insert_menu.addAction(table_act)

        for key in Plugins.generatorPluginNames():
            gen = Plugins.getGeneratorPlugin(key)
            if gen:
                act = QAction(gen.display_name, self)
                #act.triggered.connect(self.insertTable)
                #act.setToolTip("Insert a table")
                insert_menu.addAction(act)
                act.triggered.connect(gen.menu_action)

        help_menu = self.menuBar().addMenu("&Help")
        help_menu.addAction(about_act)
        help_menu.addAction(spell_act)

        file_tool_bar = self.addToolBar("File")
        file_tool_bar.addAction(new_act)
        file_tool_bar.addAction(open_act)
        file_tool_bar.addAction(book_act)

        format_tool_bar = self.addToolBar("Format")
        format_tool_bar.addAction(bold_act)
        format_tool_bar.addAction(italic_act)

        insert_toolbar = self.addToolBar("Insert")
        insert_toolbar.addAction(image_act)
        insert_toolbar.addAction(table_act)
        insert_toolbar.addAction(á_act)
        insert_toolbar.addAction(ã_act)
        insert_toolbar.addAction(é_act)
        insert_toolbar.addAction(ê_act)
        insert_toolbar.addAction(ó_act)

    def doUndo(self):
        self.text_edit.undo()

    def doRedo(self):
        self.text_edit.redo()

    def doCut(self):
        self.text_edit.cut()

    def doCopy(self):
        self.text_edit.copy()

    def doPaste(self):
        self.text_edit.paste()

    def insertImage(self):
        if not self.book:
            QMessageBox.warning(self, QCoreApplication.applicationName(), "You have to load or create a book first!")
            return
        if not self.filename:
            QMessageBox.warning(self, QCoreApplication.applicationName(), "You have to select part from the book content first!")
            return
        if self.image_list.count() == 0:
            QMessageBox.warning(self, QCoreApplication.applicationName(), "You have to add an image to the image list first!")
            return
        if not self.image_list.currentItem():
            QMessageBox.warning(self, QCoreApplication.applicationName(), "You have to select an image from the image list first!")
            return

        item = self.image_list.currentItem()
        filename = item.text()
        cursor = self.text_edit.textCursor()
        pos = cursor.position()
        base = filename.split(".")[0].replace("_", "-")
        cursor.insertText("![" + base + "](../images/" + filename + " \"" + base + "\")")
        cursor.setPosition(pos)
        self.text_edit.setTextCursor(cursor)

    def insertTable(self):
        cursor = self.text_edit.textCursor()
        pos = cursor.position()
        cursor.insertText("| alignLeft | alignCenter | unAligned | alignRight |\n"
                          "|  :---     |   :---:     |   ---     |   ---:     |\n"
                          "|  cell a   |   cell b    |   cell c  |   cell d   |\n"
                          "|  cell e   |   cell f    |   cell g  |   cell h   |\n")
        cursor.setPosition(pos)
        self.text_edit.setTextCursor(cursor)

    def insertLetterA1(self):
        cursor = self.text_edit.textCursor()
        pos = cursor.position()
        cursor.insertText("á")
        cursor.setPosition(pos + 1)
        self.text_edit.setTextCursor(cursor)

    def insertLetterA2(self):
        cursor = self.text_edit.textCursor()
        pos = cursor.position()
        cursor.insertText("ã")
        cursor.setPosition(pos + 1)
        self.text_edit.setTextCursor(cursor)

    def insertLetterE1(self):
        cursor = self.text_edit.textCursor()
        pos = cursor.position()
        cursor.insertText("é")
        cursor.setPosition(pos + 1)
        self.text_edit.setTextCursor(cursor)

    def insertLetterE2(self):
        cursor = self.text_edit.textCursor()
        pos = cursor.position()
        cursor.insertText("ê")
        cursor.setPosition(pos + 1)
        self.text_edit.setTextCursor(cursor)

    def insertLetterO1(self):
        cursor = self.text_edit.textCursor()
        pos = cursor.position()
        cursor.insertText("ó")
        cursor.setPosition(pos + 1)
        self.text_edit.setTextCursor(cursor)

    def createStatusBar(self):
        self.statusBar().showMessage("Ready")

    def about(self):
        QMessageBox.about(self, "About " + QCoreApplication.applicationName(), "EbookCreator\nVersion: " + QCoreApplication.applicationVersion() + "\n(C) Copyright 2020 CrowdWare. All rights reserved.\n\nThis program is provided AS IS with NO\nWARRANTY OF ANY KIND, INCLUDING THE\nWARRANTY OF DESIGN, MERCHANTABILITY AND\nFITNESS FOR A PATICULAR PURPOSE.")

    def newFile(self):
        dlg = ProjectWizard(self.install_directory, parent = self)
        dlg.loadBook.connect(self.loadBook)
        dlg.show()

    def open(self):
        fileName = ""
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setNameFilter("EbookCreator (book.qml);;All (*)")
        dialog.setWindowTitle("Load Ebook")
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        dialog.setAcceptMode(QFileDialog.AcceptOpen)
        dialog.setDirectory(os.path.join(self.install_directory, "sources"))
        if dialog.exec_():
            fileName = dialog.selectedFiles()[0]
        del dialog
        if not fileName:
            return
        self.loadBook(fileName)

    def writeSettings(self):
        settings = QSettings(QSettings.IniFormat, QSettings.UserScope, QCoreApplication.organizationName(), QCoreApplication.applicationName())
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("lastBook", self.last_book)

    def readSettings(self):
        settings = QSettings(QSettings.IniFormat, QSettings.UserScope, QCoreApplication.organizationName(), QCoreApplication.applicationName())
        geometry = settings.value("geometry", QByteArray())
        self.last_book = settings.value("lastBook")
        if not geometry:
            availableGeometry = QApplication.desktop().availableGeometry(self)
            self.resize(int(availableGeometry.width() / 1.5), int(availableGeometry.height() / 1.5))
            self.move(int((availableGeometry.width() - self.width()) / 2), int((availableGeometry.height() - self.height()) / 2))
        else:
            self.restoreGeometry(geometry)

    def bold(self):
        if not self.filename:
            QMessageBox.warning(self, QCoreApplication.applicationName(), "You have to select part from the book content first!")
            return
        cursor = self.text_edit.textCursor()
        pos = cursor.position()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.WordUnderCursor)
        cursor.insertText("**" + cursor.selectedText() + "**")
        cursor.setPosition(pos + 2)
        self.text_edit.setTextCursor(cursor)

    def italic(self):
        if not self.filename:
            QMessageBox.warning(self, QCoreApplication.applicationName(), "You have to select part from the book content first!")
            return
        cursor = self.text_edit.textCursor()
        pos = cursor.position()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.WordUnderCursor)
        cursor.insertText("*" + cursor.selectedText() + "*")
        cursor.setPosition(pos + 1)
        self.text_edit.setTextCursor(cursor)

    def create(self):
        filename = ""
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setNameFilter("ePub3 (*.epub);;All (*)")
        dialog.setWindowTitle("Create Ebook")
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setDirectory(self.book.source_path)
        dialog.setDefaultSuffix("epub")
        if dialog.exec_():
            filename = dialog.selectedFiles()[0]
        del dialog
        if not filename:
            return
        QApplication.setOverrideCursor(Qt.WaitCursor)
        createEpub(filename, self.book, self)
        QApplication.restoreOverrideCursor()

    def loadStatusChanged(self, status):
        if status == 1:
            self.book = self.component.create()
            if self.book is not None:
                self.book.setFilename(self.last_book)
                self.book.setWindow(self)
            else:
                for error in self.component.errors():
                    print(error.toString())
                return

            self.content_list.clear()
            for part in self.book.parts:
                item = QListWidgetItem()
                item.setText(part.name)
                item.setData(1, part)
                self.content_list.addItem(item)

            self.loadImages()
            self.setWindowTitle(QCoreApplication.applicationName() + " - " + self.book.name)

            self.content.setExpanded(True)
            self.content_list.setCurrentRow(0)
        elif status == 3:
            for error in self.component.errors():
                print(error.toString())
            return

    def loadBook(self, filename):
        self.last_book = filename
        self.filename = ""
        engine = QQmlEngine()
        self.component = QQmlComponent(engine)
        self.component.statusChanged.connect(self.loadStatusChanged)
        self.component.loadUrl(QUrl.fromLocalFile(filename))

    def settingsDialog(self):
        dlg = SettingsDialog(self.theme, self.palette().highlight().color().name(), parent=self)
        dlg.exec()
        if dlg.theme != self.theme or dlg.hilite_color != self.palette().highlight().color().name():
            settings = QSettings(QSettings.IniFormat, QSettings.UserScope, QCoreApplication.organizationName(), QCoreApplication.applicationName())
            settings.setValue("theme", dlg.theme)
            settings.setValue("hiliteColor", dlg.hilite_color)

            msgBox = QMessageBox()
            msgBox.setText("Please restart the app to change the theme!")
            msgBox.exec()

    def textChanged(self):
        text = self.text_edit.toPlainText()
        if self.filename:
            with open(self.filename, "w") as f:
                f.write(text)

        self.lock = Lock()
        with self.lock:
            if not self.tread_running:
                self.tread_running = True
                self.htmlReady.connect(self.previewReady)
                thread = Thread(target=self.createHtml, args=(text,))
                thread.daemon = True
                thread.start()

    def previewReady(self, html):
        self.preview.setHtml(html, baseUrl=QUrl(Path(os.path.join(self.book.source_path, "parts", "index.html")).as_uri()))
        self.htmlReady.disconnect()
        with self.lock:
            self.tread_running = False

    def createHtml(self, text):
        html = '<html>\n<head>\n'
        html += '<link href="../css/pastie.css" rel="stylesheet" type="text/css"/>\n'
        html += '<link href="../css/stylesheet.css" rel="stylesheet" type="text/css"/>\n'
        html += '</head>\n<body>\n'
        html += markdown(text, html4tags=False, extras=["fenced-code-blocks", "wiki-tables", "tables", "header-ids"])
        html += '\n</body>\n</html>'
        html = addLineNumbers(html)
        self.htmlReady.emit(html)

    def pdfExport(self):
        p = PdfExport(self.book, self.statusBar())

    def spellCheck(self):
        if not self.filename:
            QMessageBox.warning(self, QCoreApplication.applicationName(), "You have to select part from the book content first!")
            return
        cursor = self.text_edit.textCursor()
        pos = cursor.position()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.WordUnderCursor)
        spell = Speller(lang='en')
        changed = spell(cursor.selectedText())
        if changed != cursor.selectedText():
            cursor.insertText(changed)
            self.text_edit.setTextCursor(cursor)

    def loadPlugins(self):
        # check if we are running in a frozen environment (pyinstaller --onefile)
        if getattr(sys, "frozen", False):
            bundle_dir = sys._MEIPASS
            # if we are running in a onefile environment, then copy all plugin to /tmp/...
            if bundle_dir != os.getcwd():
                if not os.path.exists(os.path.join(bundle_dir, "plugins")):
                    os.mkdir(os.path.join(bundle_dir, "plugins"))
                for root, dirs, files in os.walk(os.path.join(os.getcwd(), "plugins")):
                    for file in files:
                        shutil.copy(os.path.join(root, file), os.path.join(bundle_dir, "plugins"))
                    break # do not copy __pycache__
        else:
            bundle_dir = os.getcwd()
        
        plugins_dir = os.path.join(bundle_dir, "plugins")
        for root, dirs, files in os.walk(plugins_dir):
            for file in files:
                modulename, ext = os.path.splitext(file)
                if ext == ".py":
                    module = import_module("plugins." + modulename)
                    for name, klass in inspect.getmembers(module, inspect.isclass):
                        if klass.__module__ == "plugins." + modulename:
                            instance = klass()
                            if isinstance(instance, GeneratorInterface):
                                Plugins.addGeneratorPlugin(name, instance)
                                instance.setTextEdit(self.text_edit)
            break # not to list __pycache__
