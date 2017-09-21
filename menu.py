#coding:utf-8
from PySide import QtGui
import os
import yaml

from window import Window, AttributeDict, styleSheet


class Action(QtGui.QAction):

    def __init__(self, parent, path):
        QtGui.QAction.__init__(self, parent)
        self.path = path
        self.setText(os.path.basename(self.path))
        for ext in [".jpg", ".png"]:
            if os.path.isfile(self.path + ext):
                self.setIcon(QtGui.QIcon(self.path + ext))
        self.triggered.connect(self.show_window)
        self.window = None

    def read(self):
        if self.window is None:
            if os.path.isfile(self.path + ".yaml"):
                with open(self.path + ".yaml", "r") as ui:
                    self.window = Window()
                    self.window.loads(yaml.load(ui.read()))
            self.window.showNormal()

    def write(self, window):
        self.window = window
        if not os.path.isfile(os.path.dirname(self.path)):
            os.makedirs(os.path.dirname(self.path))
        with open(self.path + ".yaml", "w") as ui:
            ui.write(yaml.dump(window.dumps()))


class Menu(QtGui.QMenu):

    def __init__(self, parent, path):
        QtGui.QMenu.__init__(self, parent)
        self.path = path
        self.setStyleSheet(styleSheet)
        self.setText(os.path.basename(self.path))
        for ext in [".jpg", ".png"]:
            if os.path.isfile(self.path + ext):
                self.setIcon(QtGui.QIcon(self.path + ext))
        if not os.path.isdir(path):
            os.makedirs(path)
        for name in os.listdir(self.path):
            if os.path.isfile(self.path + "name"):
                self.addMenu(name)
            else:
                self.addAction(os.path.splitext(name))
        self.children = AttributeDict()

    def addMenu(self, text):
        self.childrens[text] = QtGui.QMenu.addMenu(self, Menu(self, self.path + "/" + text))
        return self.childrens[text]

    def addAction(self, text):
        self.childrens[text] = QtGui.QMenu.addAction(self, Action(self, self.path + "/" + text))
        return self.childrens[text]
