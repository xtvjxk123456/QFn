#coding:utf-8
from PySide import QtGui, QtCore
import os


class Action(QtGui.QAction):

    def __init__(self,yaml, parent):
        self.yaml = yaml
        name = os.path.splitext(os.path.basename(self.yaml.path))[0]
        QtGui.QAction.__init__(self, name, parent)


class Menu(QtGui.QMenu):

    def __init__(self, yamls):
        self.yamls = yamls
        print os.path.basename(yamls.__path__)
        QtGui.QMenu.__init__(self, os.path.basename(yamls.__path__))
        for elem in self.yamls:
            if isinstance(elem, self.yamls.__class__):
                self.addMenu(Menu(elem))
            else:
                self.addAction(Action(elem, self))
                action = QtGui.QAction("ttt", self)
                action = QtGui.QWidgetAction(self)
                self.addAction(action)
                action.createWidget(QtGui.QPushButton("aaa"))
                action.setText("eee")
                action.createWidget(QtGui.QPushButton("aaa"))
                action.setDefaultWidget(QtGui.QPushButton("sss"))

