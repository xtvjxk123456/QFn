# coding:utf-8

from PySide import QtGui, QtCore
import os
import yaml

from window import Window, AttributeDict
from function import Function


class Action(QtGui.QAction):
    windowSignal = QtCore.Signal(Window)

    def __init__(self, path, parent=None):
        QtGui.QAction.__init__(self, parent)
        self.path = path
        self.setText(os.path.basename(self.path))
        for ext in [".jpg", ".png"]:
            if os.path.isfile(self.path + ext):
                self.setIcon(QtGui.QIcon(self.path + ext))
        self.triggered.connect(self.read)
        self.window = None

    def read(self):
        if self.window is None:
            if os.path.isfile(self.path + ".yaml"):
                with open(self.path + ".yaml", "r") as ui:
                    data = yaml.load(ui.read())
                    if len(data) == 1 and len(data.values()[0]) == 0:
                        Function(data.keys()[0])()
                    else:
                        self.window = Window()
                        self.window.loads(data)
                        self.window.showNormal()
                        if os.path.isfile(self.path + ".html"):
                            for option in self.window.options:
                                option.html = self.path + ".html"
                        self.windowSignal.emit(self.window)
        else:
            self.window.showNormal()

    def write(self, window):
        self.window = window
        if not os.path.isdir(os.path.dirname(self.path)):
            os.makedirs(os.path.dirname(self.path))
        with open(self.path + ".yaml", "w") as ui:
            ui.write(yaml.dump(window.dumps(), default_flow_style=False))


class Menu(QtGui.QMenu):

    def __init__(self, path, parent=None):
        QtGui.QMenu.__init__(self, parent)
        self.path = path
        self.setTitle(os.path.basename(self.path))
        for ext in [".jpg", ".png"]:
            if os.path.isfile(self.path + ext):
                self.setIcon(QtGui.QIcon(self.path + ext))
        if not os.path.isdir(path):
            os.makedirs(path)
        self.items = AttributeDict()
        for name in os.listdir(self.path):
            if os.path.isfile(self.path + "/" + name):
                name, ext = os.path.splitext(name)
                if ext == ".yaml":
                    self.addAction(name)
            else:
                self.addMenu(name)

    def addMenu(self, text):
        self.items[text] = Menu(self.path + "/" + text, self)
        QtGui.QMenu.addMenu(self, self.items[text])
        return self.items[text]

    def addAction(self, text):
        self.items[text] = Action(self.path + "/" + text, self)
        QtGui.QMenu.addAction(self, self.items[text])
        return self.items[text]

    def install(self):
        for menuBar in QtGui.QApplication.activeWindow().children():
            if isinstance(menuBar, QtGui.QMenuBar):
                menuBar.addMenu(self)
                break

    def uninstall(self):
        for menuBar in QtGui.QApplication.activeWindow().children():
            if isinstance(menuBar, QtGui.QMenuBar):
                menuBar.removeAction(menuBar.addMenu(self))
                break
