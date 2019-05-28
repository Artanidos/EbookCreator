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

import sys
from os import path, remove, walk
from pathlib import Path
from shutil import copy

from django.utils.safestring import mark_safe
from markdown2 import markdown
from PyQt5.QtCore import (QByteArray, QCoreApplication, QPropertyAnimation,
                          QSettings, Qt, QUrl, QSize)
from PyQt5.QtGui import (QColor, QFont, QIcon, QKeySequence, QPalette,
                         QTextCursor, QImage, QPixmap)
from PyQt5.QtQml import QQmlComponent, QQmlEngine
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import (QAction, QApplication, QDialog, QDockWidget,
                             QFileDialog, QHBoxLayout, QLineEdit, QListWidget,
                             QListWidgetItem, QMainWindow, QMessageBox,
                             QScrollArea, QSizePolicy, QSplitter,
                             QStyleFactory, QTextEdit, QVBoxLayout, QWidget)

from ebook import Ebook
from expander import Expander
from flatbutton import FlatButton
from generator import createEpub
from hyperlink import HyperLink
from markdownedit import MarkdownEdit
from projectwizard import ProjectWizard
from settings import Settings


class MainWindow(QMainWindow):
    def __init__(self, install_directory):
        QMainWindow.__init__(self)
        self.install_directory = install_directory
        self.book = None
        self.last_book = ""
        self.filename = ""

        self.createUi()
        self.createMenus()
        self.createStatusBar()
        self.readSettings()
        self.text_edit.textChanged.connect(self.textChanged)

        if self.last_book:
            self.loadBook(self.last_book)

    def createUi(self):
        self.content = Expander("Content", "./images/parts_normal.png", "./images/parts_hover.png", "./images/parts_selected.png")
        self.images = Expander("Images", "./images/images_normal.png", "./images/images_hover.png", "./images/images_selected.png")
        # self.appearance = Expander("Appearance", "./images/appearance_normal.png", "./images/appearance_hover.png", "./images/appearance_selected.png")
        self.settings = Expander("Settings", "./images/settings_normal.png", "./images/settings_hover.png", "./images/settings_selected.png")

        self.setWindowTitle(QCoreApplication.applicationName() + " " + QCoreApplication.applicationVersion())
        vbox = QVBoxLayout()
        vbox.addWidget(self.content)
        vbox.addWidget(self.images)
        # vbox.addWidget(self.appearance)
        vbox.addWidget(self.settings)
        vbox.addStretch()

        self.content_list = QListWidget()
        self.content_list.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        content_box = QVBoxLayout()
        content_box.addWidget(self.content_list)
        self.item_edit = QLineEdit()
        self.item_edit.setMaximumHeight(0)
        self.item_edit.editingFinished.connect(self.addItem)
        self.item_anim = QPropertyAnimation(self.item_edit, "maximumHeight".encode("utf-8"))
        content_box.addWidget(self.item_edit)
        button_layout = QHBoxLayout()
        plus_button = FlatButton("./images/plus_normal.png", "./images/plus_hover.png")
        self.trash_button = FlatButton("./images/trash_normal.png", "./images/trash_hover.png", disabled_icon = "./images/trash_disabled.png")
        self.up_button = FlatButton("./images/up_normal.png", "./images/up_hover.png", disabled_icon = "./images/up_disabled.png")
        self.down_button = FlatButton("./images/down_normal.png", "./images/down_hover.png", disabled_icon = "./images/down_disabled.png")
        self.trash_button.enabled = False
        self.up_button.enabled = False
        self.down_button.enabled = False
        button_layout.addWidget(plus_button)
        button_layout.addWidget(self.up_button)
        button_layout.addWidget(self.down_button)
        button_layout.addWidget(self.trash_button)
        content_box.addLayout(button_layout)
        self.content.addLayout(content_box)
        plus_button.clicked.connect(self.addPart)
        self.trash_button.clicked.connect(self.dropPart)
        self.up_button.clicked.connect(self.partUp)
        self.down_button.clicked.connect(self.partDown)

        self.image_list = QListWidget()
        self.image_list.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        image_box = QVBoxLayout()
        image_box.addWidget(self.image_list)
        image_button_layout = QHBoxLayout()
        image_plus_button = FlatButton("./images/plus_normal.png", "./images/plus_hover.png")
        self.image_trash_button = FlatButton("./images/trash_normal.png", "./images/trash_hover.png", disabled_icon = "./images/trash_disabled.png")
        self.image_trash_button.enabled = False
        image_button_layout.addWidget(image_plus_button)
        image_button_layout.addWidget(self.image_trash_button)
        image_box.addLayout(image_button_layout)
        self.images.addLayout(image_box)
        image_plus_button.clicked.connect(self.addImage)
        self.image_trash_button.clicked.connect(self.dropImage)

        # app_box = QVBoxLayout()
        # themes_button = HyperLink("Themes")
        # menus_button = HyperLink("Menus")
        # self.theme_settings_button = HyperLink("Theme Settings")
        # self.theme_settings_button.setVisible(False)
        # app_box.addWidget(menus_button)
        # app_box.addWidget(themes_button)
        # app_box.addWidget(self.theme_settings_button)
        # self.appearance.addLayout(app_box)

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
        self.text_edit.setFont(QFont("Courier", 11))
        self.preview = QWebEngineView()
        self.preview.setMinimumWidth(300)
        self.setWindowTitle(QCoreApplication.applicationName())

        self.splitter.addWidget(self.text_edit)
        self.splitter.addWidget(self.preview)
        self.setCentralWidget(self.splitter)

        self.content.expanded.connect(self.contentExpanded)
        self.images.expanded.connect(self.imagesExpanded)
        # self.appearance.expanded.connect(self.appearanceExpanded)
        self.settings.expanded.connect(self.settingsExpanded)
        self.settings.clicked.connect(self.openSettings)
        self.content_list.currentItemChanged.connect(self.partSelectionChanged)
        self.image_list.currentItemChanged.connect(self.imageSelectionChanged)
        self.image_list.itemDoubleClicked.connect(self.insertImage)

    def openSettings(self):
        dlg = Settings(self.book)
        dlg.exec()
        if dlg.saved:
            self.setWindowTitle(QCoreApplication.applicationName() + " - " + self.book.name)

    def addPart(self):
        self.item_edit.setText("")
        self.item_edit.setFocus()
        self.item_anim.setStartValue(0)
        self.item_anim.setEndValue(23)
        self.item_anim.start()

    def addItem(self):
        text = self.item_edit.text()
        if text:
            if not self.book.getPart(text):
                self.book.addPart(text)
                self.loadBook(self.last_book)
        self.item_anim.setStartValue(23)
        self.item_anim.setEndValue(0)
        self.item_anim.start()

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
        copy(fileName, path.join(self.book.source_path, "images"))
        item = QListWidgetItem()
        item.setText(Path(fileName).name)
        item.setData(1, path.join(self.book.source_path, "images", Path(fileName).name))
        self.image_list.addItem(item)

    def dropImage(self):
        item = self.image_list.currentItem()
        image = item.data(1)
        filename = path.join(self.book.source_path, "parts", image)
        remove(filename)
        self.loadImages()

    def loadImages(self):
        self.image_list.clear()
        for root, dir, files in walk(path.join(self.book.source_path, "images")):
            for file in files:
                filename = path.join(self.book.source_path, "images", Path(file).name)
                item = QListWidgetItem()
                item.setToolTip("Doubleclick image to insert into text")
                item.setText(Path(file).name)
                item.setData(1, filename)
                self.image_list.addItem(item)

    def partUp(self):
        pass

    def partDown(self):
        pass

    def partSelectionChanged(self, item):
        if item:
            part = item.data(1)
            self.filename = path.join(self.book.source_path, "parts", part.src)
            with open(self.filename, "r") as f:
                self.text_edit.setText(f.read())
            self.trash_button.enabled = True
        else:
            self.text_edit.setText("")
            self.trash_button.enabled = False
            self.up_button.enabled = False
            self.down_button.enabled = False

    def imageSelectionChanged(self, item):
        if item:
            self.image_trash_button.enabled = True
        else:
            self.image_trash_button.enabled = False

    def contentExpanded(self, value):
        if value:
            self.images.setExpanded(False)
            # self.appearance.setExpanded(False)
            self.settings.setExpanded(False)

    def imagesExpanded(self, value):
        if value:
            self.content.setExpanded(False)
            # self.appearance.setExpanded(False)
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
            # self.appearance.setExpanded(False)

    def closeEvent(self, event):
        self.writeSettings()
        event.accept()

    def createMenus(self):
        new_icon = QIcon("./images/new.png")
        open_icon = QIcon("./images/open.png")
        book_icon = QIcon("./images/book.png")
        exit_icon = QIcon("./images/exit.png")
        bold_icon = QIcon("./images/bold.png")
        italic_icon = QIcon("./images/italic.png")
        image_icon = QIcon("./images/image.png")
        table_icon = QIcon("./images/table.png")

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

        exit_act = QAction(exit_icon, "E&xit", self)
        exit_act.setShortcuts(QKeySequence.Quit)
        exit_act.setStatusTip("Exit the application")
        exit_act.triggered.connect(self.close)

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

        about_act = QAction("&About", self)
        about_act.triggered.connect(self.about)
        about_act.setStatusTip("Show the application's About box")

        file_menu = self.menuBar().addMenu("&File")
        file_menu.addAction(new_act)
        file_menu.addAction(open_act)
        file_menu.addAction(book_act)
        file_menu.addSeparator()
        file_menu.addAction(exit_act)

        format_menu = self.menuBar().addMenu("&Format")
        format_menu.addAction(bold_act)
        format_menu.addAction(italic_act)

        insert_menu = self.menuBar().addMenu("&Insert")
        insert_menu.addAction(image_act)
        insert_menu.addAction(table_act)

        help_menu = self.menuBar().addMenu("&Help")
        help_menu.addAction(about_act)

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
        cursor.insertText("![AltText](../images/" + filename + " \"Title\")")
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

    def createStatusBar(self):
        self.statusBar().showMessage("Ready")

    def about(self):
        QMessageBox.about(self, "About " + QCoreApplication.applicationName(), "Using this appication you are able to create an ebook based on the markdown language.")

    def newFile(self):
        dlg = ProjectWizard(self.install_directory, parent = self)
        dlg.loadBook.connect(self.loadBook)
        dlg.show()

    def loadBook(self, filename):
        self.last_book = filename
        self.filename = ""
        engine = QQmlEngine()
        component = QQmlComponent(engine)
        component.loadUrl(QUrl(filename))
        self.book = component.create()
        if self.book is not None:
            self.book.setFilename(filename)
            self.book.setWindow(self)
        else:
            for error in component.errors():
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

    def open(self):
        fileName = ""
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setNameFilter("EbookCreator (book.qml);;All (*)")
        dialog.setWindowTitle("Load Ebook")
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        dialog.setAcceptMode(QFileDialog.AcceptOpen)
        dialog.setDirectory(path.join(self.install_directory, "sources"))
        if dialog.exec_():
            fileName = dialog.selectedFiles()[0]
        del dialog
        if not fileName:
            return
        self.loadBook(fileName)

    def writeSettings(self):
        settings = QSettings(QCoreApplication.organizationName(), QCoreApplication.applicationName())
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("lastBook", self.last_book)

    def readSettings(self):
        settings = QSettings(QCoreApplication.organizationName(), QCoreApplication.applicationName())
        geometry = settings.value("geometry", QByteArray())
        self.last_book = settings.value("lastBook")
        if not geometry:
            availableGeometry = QApplication.desktop().availableGeometry(self)
            self.resize(availableGeometry.width() / 3, availableGeometry.height() / 2)
            self.move((availableGeometry.width() - self.width()) / 2, (availableGeometry.height() - self.height()) / 2)
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

    def textChanged(self):
        if self.filename:
            with open(self.filename, "w") as f:
                f.write(self.text_edit.toPlainText())

        html = "<html>\n<head>\n"
        html += "<link href=\"../css/pastie.css\" rel=\"stylesheet\" type=\"text/css\"/>\n"
        html += "<link href=\"../css/stylesheet.css\" rel=\"stylesheet\" type=\"text/css\"/>\n"
        html += "</head>\n<body>\n"
        html += mark_safe(markdown(self.text_edit.toPlainText(), html4tags = False, extras=["fenced-code-blocks", "tables"]))
        html += "\n</body>\n</html>"
        self.preview.setHtml(html, baseUrl = QUrl(Path(path.join(self.book.source_path, "parts", "index.html")).as_uri()))
        print(html)

    def create(self):
        filename = ""
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setNameFilter("ePub3 (*.epub);;All (*)")
        dialog.setWindowTitle("Create Ebook")
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setDirectory(self.install_directory)
        dialog.setDefaultSuffix("epub")
        if dialog.exec_():
            filename = dialog.selectedFiles()[0]
        del dialog
        if not filename:
            return
        QApplication.setOverrideCursor(Qt.WaitCursor)
        createEpub(filename, self.book, self)
        QApplication.restoreOverrideCursor()
