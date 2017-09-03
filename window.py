#coding:utf-8

from PySide import QtGui, QtCore

import args
from function import Function


class TabForm(QtGui.QWidget):
    def __init__(self, fn):
        QtGui.QWidget.__init__(self)
        self.fn = Function(fn)
        self.setLayout(QtGui.QFormLayout())
        self.layout().setLabelAlignment(QtCore.Qt.AlignRight)
        self.layout().setFieldGrowthPolicy(QtGui.QFormLayout.ExpandingFieldsGrow)
        self.__widget_dict = {}

    def __call__(self, **kwargs):
        for arg in self.fn.args:
            if arg in kwargs:
                label = " ".join([word.capitalize() for word in arg.split("_")]) + ": "
                self.layout().addRow(label, kwargs[arg])
                self.__widget_dict[arg] = kwargs[arg]
        self.kwargs = self.fn.kwargs

    def __getattr__(self, attr):
        if attr in self.__widget_dict:
            return self.__widget_dict[attr]
        raise AttributeError("{self} has no attribute {attribute}".format(self=self, attribute=self))

    def __repr__(self):
        return "{self.__module__}.{self.__class__.__name__}({self.fn})".format(self=self)

    @property
    def kwargs(self):
        return {key: widget.arg for key, widget in self.__widget_dict.items()}

    @kwargs.setter
    def kwargs(self, kwargs):
        for key, value in kwargs.items():
            if key in self.__widget_dict:
                self.__widget_dict[key].arg = value

    def apply(self):
        self.fn(**self.kwargs)

    def dumps(self):
        return {arg: repr(widget) for arg, widget in self.__widget_dict.items()}

    def loads(self, data):
        self(**{key: eval(value, args.__dict__) for key, value in data.items()})


class Window(QtGui.QDialog):
    applySignal = QtCore.Signal(QtGui.QDialog)
    closeSignal = QtCore.Signal()

    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.setParent(QtGui.QApplication.activeWindow())
        self.setWindowFlags(QtCore.Qt.WindowFlags(1))
        self.resize(546, 350)
        self.setLayout(QtGui.QVBoxLayout())
        self.layout().setContentsMargins(5, 5, 5, 5)
        self.layout().setSpacing(5)
        self.layout().addWidget(QtGui.QTabWidget())
        self.layout().addLayout(QtGui.QHBoxLayout(self))
        self.layout().itemAt(1).layout().setSpacing(5)
        self.layout().itemAt(1).layout().addWidget(QtGui.QPushButton(u"apply and close"))
        self.layout().itemAt(1).layout().addWidget(QtGui.QPushButton(u"apply"))
        self.layout().itemAt(1).layout().addWidget(QtGui.QPushButton(u"close"))
        self.layout().itemAt(1).layout().itemAt(0).widget().clicked.connect(self.apply)
        self.layout().itemAt(1).layout().itemAt(0).widget().clicked.connect(self.close)
        self.layout().itemAt(1).layout().itemAt(1).widget().clicked.connect(self.apply)
        self.layout().itemAt(1).layout().itemAt(2).widget().clicked.connect(self.close)
        self.__tab__dict = {}

    def apply(self):
        self.layout().itemAt(0).widget().currentWidget().apply()
        self.applySignal.emit(self)

    def close(self):
        QtGui.QWidget.close(self)
        self.closeSignal.emit(self)

    def add_function(self, fn):
        form = TabForm(fn)
        self.__tab__dict[form.fn.name] = form
        self.layout().itemAt(0).widget().addTab(form, form.fn.name)
        return form

    def __getattr__(self, attr):
        if attr in self.__tab__dict:
            return self.__tab__dict[attr]

    def dumps(self):
        return {form.fn.fullName: form.dumps() for fn, form in self.__tab__dict.items()}

    def loads(self, data):
        for fn, tab_data in data.items():
            self.add_function(fn).loads(tab_data)
