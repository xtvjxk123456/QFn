# coding:utf-8

from PySide import QtGui, QtCore
import os
import args
from function import Function

with open(os.path.dirname(__file__)+"/data/qss/gray.qss") as _qss:
    styleSheet = _qss.read()


class AttributeDict(dict):
    def __getattr__(self, attr):
        u"""
        :param attr: 属性名。
        :return: 将attr当作字典中的key查询到的值。
        当通过AttributeDict.attr访问dict不存在的属性时调用。
        """
        return self.__getitem__(attr)


class Message(object):

    def __init__(self, title):
        u"""
        :param title: 窗口标题，用来区别信息类型。
        """
        self._title = title

    @property
    def message(self):
        """
        仅在首次调用该属性时创建窗口实例，避免在导入模块时创建。
        :return: <PySide.QtGui.QMessageBox>
        """
        if "_message" not in self.__dict__:
            self.__dict__["_message"] = QtGui.QMessageBox()
            self.message.setWindowTitle(self._title)
            self.message.setStyleSheet(
                """
                background: #484848;color: 
                rgb(200,200,200);
                font-size: 18px;
                border-color: #404040;
                """)
        return self.__dict__["_message"]

    def __call__(self, text):
        u"""
        :param text: 提示内容。同一种信息类型公用一种提示窗口实例<str>。
        将text内容在提示窗口中显示来对用户进行提示。
        """
        self.message.setText(text)
        self.message.move(QtGui.QCursor.pos())
        self.message.show()


class Option(QtGui.QWidget):
    u"""
    函数组件。
    Message message: 函数帮助显示装口。
    Function fn: 组件对应函数。
    html：函数帮助网页储存地址。
    """
    message = Message("function help")

    def __init__(self, fn):
        u"""
        :param fn: python函数<function>。
        """
        QtGui.QWidget.__init__(self)
        self.fn = Function(fn)
        self.setStyleSheet(styleSheet)
        self.setLayout(QtGui.QFormLayout())
        self.layout().setLabelAlignment(QtCore.Qt.AlignRight)
        self.layout().setFieldGrowthPolicy(QtGui.QFormLayout.ExpandingFieldsGrow)
        self.menu = QtGui.QMenu(self)
        self.menu.addAction("reset").triggered.connect(self.reset)
        self.menu.addAction("help").triggered.connect(self.help)
        self.widgets = AttributeDict()
        self.html = None

    def __call__(self, **kwargs):
        u"""
        :param kwargs: {由参数名和参数组件键值对{str arg: QWidget widget……}
        参数名将下划线转空格、首字母大小、后缀加：。
        例：point_on_curve>Point On Curve:
        以 参数名:参数组件 的形式竖向添加到选项组件。
        添加顺序为原函数参数顺数。
        可适当改变原函数参数名和参数顺序来让界面好看一些。
        """
        keys = [arg for arg in self.fn.args if arg in kwargs]
        keys.extend(set(key for key in kwargs if key in self.fn) - set(keys))
        for key in keys:
            label = " ".join([word.capitalize() for word in key.split("_")]) + " : "
            self.layout().addRow(label, kwargs[key])
            self.widgets[key] = kwargs[key]
        self.kwargs = self.fn.kwargs

    def __repr__(self):
        return "{self.__module__}.{self.__class__.__name__}('{self.fn.fullName}')".format(self=self)

    @property
    def kwargs(self):
        u"""
        由函数组件的参数名和参数组件表示的参数值构成的键值对。
        """
        return {key: value.arg for key, value in self.widgets.items()}

    @kwargs.setter
    def kwargs(self, kwargs):
        for key, value in kwargs.items():
            if key in self.widgets:
                self.widgets[key].arg = value

    def dump(self):
        u"""
        将所有组建转化为可写入yaml的通用数据。
        :return: 由参数名和可通过eval生成参数组件的字符串构成的键值对{str arg: str widget……}
        """
        return {key: repr(value) for key, value in self.widgets.items()}

    def load(self, data):
        u"""
        :param data: 由参数名和可通过eval生成参数组件的字符串构成的键值对{str arg: str widget……}
        将通用数据转化为参数组件。
        """
        self(**{key: eval(value, args.__dict__) for key, value in data.items()})

    def reset(self):
        u"""
        :return: 将参数组建的表示的值设置成函数默认值。
        """
        self.kwargs = self.fn.default

    def help(self):
        u"""
        若设置了相关网页帮助，则打开网页。否则，显示函数帮助。
        """
        if self.html:
            os.startfile(self.html)
        else:
            self.message(self.fn.help)

    def contextMenuEvent(self, event):
        u"""
        右击时，显示右键菜单。
        """
        self.menu.exec_(event.globalPos())


class Window(QtGui.QDialog):
    """
    功能函数窗口。
    与maya通用菜单类似的窗口布局。
    QtCore.Signal applySignal: 执行apply函数时按钮时发射。
    QtCore.Signal closeSignal: 执行close函数时按钮时发射。
    QtCore.Signal showSignal: 执行showNormal函数时时发射。
    AttributeDict options: 由函数名称和函数组件构成的键值对。
    """
    applySignal = QtCore.Signal()
    closeSignal = QtCore.Signal()
    showSignal = QtCore.Signal()

    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.setParent(QtGui.QApplication.activeWindow())
        self.setWindowFlags(QtCore.Qt.WindowFlags(1))
        self.resize(546, 350)
        self.setStyleSheet(styleSheet)
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
        self.options = AttributeDict()

    def showNormal(self):
        u"""
        显示窗口
        """
        QtGui.QWidget.showNormal(self)
        self.showSignal.emit()

    def close(self):
        u"""
        关闭窗口。
        """
        QtGui.QWidget.close(self)
        self.closeSignal.emit()

    def apply(self):
        u"""
        运行当前选择的函数组件。
        """
        option = self.layout().itemAt(0).widget().currentWidget()
        option.fn(**option.kwargs)
        self.applySignal.emit()

    def add(self, fn):
        u"""
        :param fn: python函数。
        添加相应的函数组件。
        """
        option = Option(fn)
        self.options[option.fn.name] = option
        self.layout().itemAt(0).widget().addTab(option, option.fn.name)
        return option

    def dumps(self):
        u"""
        将所有函数组件为可写入yaml的通用数据。
        :return: 由函数数名和函数组件dump生产的通用数据构成的键值对{str arg: dict option……}
        """
        return {option.fn.fullName: option.dump() for option in self.options.values()}

    def loads(self, data):
        u"""
        :param data: 由函数数名和函数组件dump生产的通用数据构成的键值对{str arg: dict option……}
        将通用数据转化为窗口的Option。
        """
        for fn, tab_data in data.items():
            self.add(fn).load(tab_data)


