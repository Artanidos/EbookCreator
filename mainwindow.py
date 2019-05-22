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
from PyQt5.QtWidgets import QApplication, QMainWindow, QSplitter, QTreeView, QTextEdit, QAction, QMessageBox, QFileDialog, QDialog, QStyleFactory
from PyQt5.QtCore import Qt, QCoreApplication, QSettings, QByteArray, QUrl
from PyQt5.QtGui import QIcon, QKeySequence, QFont, QPalette, QColor
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtQml import QQmlEngine, QQmlComponent
import markdown2
from django.template import Context, Engine
from django.utils.safestring import mark_safe
from projectwizard import ProjectWizard


class MainWindow(QMainWindow):
    def __init__(self, install_directory):
        QMainWindow.__init__(self)
        self.install_directory = install_directory
        self.book = None
        self.cur_file = ""
        self.splitter1 = QSplitter()
        self.splitter2 = QSplitter()
        self.treeview = QTreeView()
        self.treeview.setMinimumWidth(100)
        self.treeview.setMaximumWidth(300)
        self.text_edit = QTextEdit("")
        self.text_edit.setFont(QFont("Courier", 11))
        self.preview = QWebEngineView()
        self.preview.setMinimumWidth(300)
        self.setWindowTitle(QCoreApplication.applicationName() + "[*]")
        self.splitter2.addWidget(self.text_edit)
        self.splitter2.addWidget(self.preview)
        self.splitter1.addWidget(self.treeview)
        self.splitter1.addWidget(self.splitter2)
        self.setCentralWidget(self.splitter1)
        self.createMenus()
        self.createStatusBar()
        self.readSettings()
        self.text_edit.document().contentsChanged.connect(self.documentWasModified)
        self.text_edit.textChanged.connect(self.textChanged)

    def closeEvent(self, event):
        #if self.maybeSave():
        self.writeSettings()
        event.accept()
        #else:
        #    event.ignore()

    def documentWasModified(self):
        self.setWindowModified(self.text_edit.document().isModified())

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
        
        #save_act = QAction(save_icon, "&Save", self)
        #save_act.setShortcuts(QKeySequence.Save)
        #save_act.setStatusTip("Save the document to disk")
        #save_act.triggered.connect(self.save)

        #save_as_act = QAction(save_as_icon, "Save &As...", self)
        #save_as_act.setShortcuts(QKeySequence.SaveAs)
        #save_as_act.setStatusTip("Save the document under a new name")
        #save_as_act.triggered.connect(self.saveAs)

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
        #file_tool_bar.addAction(save_act)

    def createStatusBar(self):
        self.statusBar().showMessage("Ready")

    def about(self):
        QMessageBox.about(self, "About " + QCoreApplication.applicationName(),
            "Using this appication you are able to create an ebook based on the markdown language.")

    def newFile(self):
        dlg = ProjectWizard(self.install_directory, parent = self)
        dlg.loadBook.connect(self.loadBook)
        dlg.show()

    def loadBook(self, filename):
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
        self.setWindowTitle(QCoreApplication.applicationName() + " - " + self.book.name + "[*]")

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

    def save(self):
        pass
        #if not self.cur_file:
        #    return self.saveAs()
        #else:
        #    return self.saveFile(self.cur_file)

    def saveAs(self):
        pass
        #dialog = QFileDialog(self)
        #dialog.setWindowModality(Qt.WindowModal)
        #dialog.setAcceptMode(QFileDialog.AcceptSave)
        #if dialog.exec() != QDialog.Accepted:
        #    return False
        #return self.saveFile(dialog.selectedFiles()[0])

    def maybeSave(self):
        pass
        #if not self.text_edit.document().isModified():
        #    return True
        #ret = QMessageBox.warning(self, QCoreApplication.applicationName(),
        #                        "The document has been modified.\n"
        #                        "Do you want to save your changes?",
        #                        QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
        #if ret == QMessageBox.Save:
        #    return self.save()
        #elif ret == QMessageBox.Cancel:
        #    return False
        #return True

    def loadFile(self, fileName):
        pass
        #with open(fileName, mode= "r") as f:
        #    text = f.read()

        #QApplication.setOverrideCursor(Qt.WaitCursor)
        #self.setCurrentFile(fileName)
        #self.text_edit.setPlainText(text)
        #self.text_edit.document().setModified(False)
        #self.setWindowModified(False)
        #QApplication.restoreOverrideCursor()        
        #self.statusBar().showMessage("File loaded", 2000)

    def saveFile(self, fileName):
        pass
        #QApplication.setOverrideCursor(Qt.WaitCursor)
        #with open(fileName, "w") as f:
        #    f.write(self.text_edit.toPlainText())
        #QApplication.restoreOverrideCursor()

        #self.setCurrentFile(fileName)
        #self.text_edit.document().setModified(False)
        #self.setWindowModified(False)
        #self.statusBar().showMessage("File saved", 2000)

    def setCurrentFile(self, fileName):
        pass
        #self.cur_file = fileName
        #shown_name = self.cur_file
        #if not self.cur_file:
        #    shown_name = "untitled.txt"
        #self.setWindowFilePath(shown_name)

    def writeSettings(self):
        settings = QSettings(QCoreApplication.organizationName(), QCoreApplication.applicationName())
        settings.setValue("geometry", self.saveGeometry())

    def readSettings(self):
        settings = QSettings(QCoreApplication.organizationName(), QCoreApplication.applicationName());
        geometry = settings.value("geometry", QByteArray())
        if not geometry:
            availableGeometry = QApplication.desktop().availableGeometry(self)
            self.resize(availableGeometry.width() / 3, availableGeometry.height() / 2)
            self.move((availableGeometry.width() - self.width()) / 2,
                (availableGeometry.height() - self.height()) / 2)
        else:
            self.restoreGeometry(geometry)

    def textChanged(self):
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
 