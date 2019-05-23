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
import os
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QDockWidget, QScrollArea, QSizePolicy, QHBoxLayout, QVBoxLayout, QMainWindow, QSplitter, QListWidget, QListWidgetItem, QTextEdit, QAction, QMessageBox, QFileDialog, QDialog, QStyleFactory
from PyQt5.QtCore import Qt, QCoreApplication, QSettings, QByteArray, QUrl, QPropertyAnimation
from PyQt5.QtGui import QIcon, QKeySequence, QFont, QPalette, QColor
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtQml import QQmlEngine, QQmlComponent
import markdown2
from django.template import Context, Engine
from django.utils.safestring import mark_safe
from projectwizard import ProjectWizard
from expander import Expander
from flatbutton import FlatButton
from hyperlink import HyperLink
from ebook import Ebook
from markdownedit import MarkdownEdit


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
        self.content = Expander("Content", "./images/pages_normal.png", "./images/pages_hover.png", "./images/pages_selected.png")
        self.appearance = Expander("Appearance", "./images/appearance_normal.png", "./images/appearance_hover.png", "./images/appearance_selected.png")
        self.settings = Expander("Settings", "./images/settings_normal.png", "./images/settings_hover.png", "./images/settings_selected.png")

        self.setWindowTitle(QCoreApplication.applicationName() + " " + QCoreApplication.applicationVersion())
        vbox = QVBoxLayout()
        vbox.addWidget(self.content)
        vbox.addWidget(self.appearance)
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
        self.trash_button = FlatButton("./images/trash_normal.png", "./images/trash_hover.png")
        self.up_button = FlatButton("./images/up_normal.png", "./images/up_hover.png", disabled_icon = "./images/up_disabled.png")
        self.down_button = FlatButton("./images/down_normal.png", "./images/down_hover.png", disabled_icon = "./images/down_disabled.png")
        self.up_button.enabled = False
        self.down_button.enabled = False
        button_layout.addWidget(plus_button)
        button_layout.addWidget(self.up_button)
        button_layout.addWidget(self.down_button)
        button_layout.addWidget(self.trash_button)
        content_box.addLayout(button_layout)
        self.content.addLayout(content_box)
        plus_button.clicked.connect(self.addPage)
        self.trash_button.clicked.connect(self.dropPage)
        self.up_button.clicked.connect(self.pageUp)
        self.down_button.clicked.connect(self.pageDown)

        app_box = QVBoxLayout()
        themes_button = HyperLink("Themes")
        menus_button = HyperLink("Menus")
        self.theme_settings_button = HyperLink("Theme Settings")
        self.theme_settings_button.setVisible(False)
        app_box.addWidget(menus_button)
        app_box.addWidget(themes_button)
        app_box.addWidget(self.theme_settings_button)
        self.appearance.addLayout(app_box)

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
        self.setWindowTitle(QCoreApplication.applicationName() + "[*]")

        self.splitter.addWidget(self.text_edit)
        self.splitter.addWidget(self.preview)
        self.setCentralWidget(self.splitter)

        self.content.expanded.connect(self.contentExpanded)
        self.appearance.expanded.connect(self.appearanceExpanded)
        self.settings.expanded.connect(self.settingsExpanded)
        self.content_list.currentItemChanged.connect(self.pageSelectionChanged)

    def addPage(self):
        self.item_edit.setText("")
        self.item_edit.setFocus()
        self.item_anim.setStartValue(0)
        self.item_anim.setEndValue(23)
        self.item_anim.start()

    def addItem(self):
        text = self.item_edit.text()
        if text:
            if not self.book.getPage(text):
                self.book.addPage(text)
                self.loadBook(self.last_book)                
        self.item_anim.setStartValue(23)
        self.item_anim.setEndValue(0)
        self.item_anim.start()

    def dropPage(self):
        item = self.content_list.currentItem().data(1).name
        msgBox = QMessageBox()
        msgBox.setText("You are about to delete the page <i>" + item + "</i>")
        msgBox.setInformativeText("Do you really want to delete the item?")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        msgBox.setDefaultButton(QMessageBox.Cancel)
        ret = msgBox.exec()
        if ret == QMessageBox.Yes:
            self.book.dropPage(item)
            self.loadBook(self.last_book)

    def pageUp(self):
        pass

    def pageDown(self):
        pass

    def pageSelectionChanged(self, item):
        if item:
            page = item.data(1)
            self.filename = os.path.join(self.book.source_path, "pages", page.src)
            with open(self.filename, "r") as f:
                self.text_edit.setText(f.read())
            self.trash_button.enabled = True
        else:
            self.text_edit.setText("")
            self.trash_button.enabled = False
            self.up_button.enabled = False
            self.down_button.enabled = False

    def contentExpanded(self, value):
        if value:
            self.appearance.setExpanded(False)
            self.settings.setExpanded(False)

    def appearanceExpanded(self, value):
        if value:
            self.content.setExpanded(False)
            self.settings.setExpanded(False)

    def settingsExpanded(self, value):
        if value:
            self.content.setExpanded(False)
            self.appearance.setExpanded(False)

    def closeEvent(self, event):
        # if self.maybeSave():
        self.writeSettings()
        event.accept()
        # else:
        #    event.ignore()

    def createMenus(self):
        new_icon = QIcon("./images/new.png")
        open_icon = QIcon("./images/open.png")
        save_icon = QIcon("./images/save.png")
        save_as_icon = QIcon("./images/save_as.png")
        exit_icon = QIcon("./images/exit.png")

        new_act = QAction(new_icon, "&New", self)
        new_act.setShortcuts(QKeySequence.New)
        new_act.setStatusTip("Create a new ebook")
        new_act.triggered.connect(self.newFile)

        open_act = QAction(open_icon, "&Open", self)
        open_act.setShortcuts(QKeySequence.Open)
        open_act.setStatusTip("Open an existing ebook")
        open_act.triggered.connect(self.open)

        exit_act = QAction(exit_icon, "E&xit", self)
        exit_act.setShortcuts(QKeySequence.Quit)
        exit_act.setStatusTip("Exit the application")
        exit_act.triggered.connect(self.close)

        about_act = QAction("&About", self)
        about_act.triggered.connect(self.about)
        about_act.setStatusTip("Show the application's About box")

        file_menu = self.menuBar().addMenu("&File")
        file_menu.addAction(new_act)
        file_menu.addAction(open_act)
        file_menu.addSeparator()
        file_menu.addAction(exit_act)

        help_menu = self.menuBar().addMenu("&Help")
        help_menu.addAction(about_act)

        file_tool_bar = self.addToolBar("File")
        file_tool_bar.addAction(new_act)
        file_tool_bar.addAction(open_act)

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
        for page in self.book.pages:
            item = QListWidgetItem()
            item.setText(page.name)
            item.setData(1, page)
            self.content_list.addItem(item)

        self.setWindowTitle(QCoreApplication.applicationName() + " - " + self.book.name)

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

    def textChanged(self):
        if self.filename:
            with open(self.filename, "w") as f:
                f.write(self.text_edit.toPlainText())

        html = "<html><head></head><link href=\"../Styles/pastie.css\" rel=\"stylesheet\" type=\"text/css\"/><body>"
        html += mark_safe(markdown2.markdown(self.text_edit.toPlainText(), ..., extras=["fenced-code-blocks"]))
        html += "</body></html>"
        self.preview.setHtml(html, baseUrl = QUrl("file://" + os.getcwd() + "/parts/OEBPS/Text/"))

    def createEpub(self):
        path = os.getcwd()
        dirs = [
            path + "/layout",
        ]
        eng = Engine(dirs = dirs, debug = True)
        context = {}
        context["content"] = mark_safe(markdown2.markdown(self.text_edit.toPlainText(), ..., extras=["fenced-code-blocks"]))
        html = eng.render_to_string("template.html", context=context)
        # todo
