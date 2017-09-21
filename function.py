# coding:utf-8

u"""
为函数提供封装，记录运行日志，参数的查询、验证、记录等功能。
"""

import os
import sys
import time
import socket
import traceback
import json
import inspect


class Log(object):
    u"""
    用来记录代码日志。
    """
    def __init__(self, path):
        u"""
        :param path: 日志路径。
        """
        self.path = path

    def __call__(self, *texts):
        u"""
        :param texts: 日志文本 <str>。
        记录日志文本到日志路径。
        """
        for text in texts:
            print text
        texts = [text + '\r\n' for text in texts]
        if not os.path.isfile(self.path):
            if not os.path.isdir(os.path.dirname(self.path)):
                os.makedirs(os.path.dirname(self.path))
        else:
            with open(self.path, 'r') as log:
                texts.extend(log.readlines()[:1000])
        with open(self.path, 'w') as log:
            log.writelines(texts)

    @property
    def time(self):
        u"""
        :return: 当前时间。
        """
        return time.strftime('%Y/%m/%d %H:%M')

    @property
    def error(self):
        u"""
        :return: 当前错误信息。
        """
        return traceback.format_exc().replace('\n', '\r\n')

    def open(self):
        u"""
        :return: 打开日志。
        """
        if os.path.isfile(self.path):
            os.startfile(self.path)

    def __repr__(self):
        return "{self.__module__}.{self.__class__.__name__}('{self.path}')".format(self=self)


class Json(object):
    u"""
    用来读/写json文件。
    """
    def __init__(self, path):
        u"""
        :param path: json文件路径。
        """
        self.path = path
        self.__data = None

    def __nonzero__(self):
        return os.path.isfile(self.path)

    def read(self):
        u"""
        :return: json文件记录的数据
        """
        if self.__data is None:
            return self.reload()
        else:
            return self.__data

    def write(self, data):
        u"""
        将python数据写入json文件；
        :param data: python数据；
        """
        if not os.path.isfile(self.path):
            json_dir = os.path.dirname(self.path)
            if not os.path.isdir(json_dir):
                os.makedirs(json_dir)
        self.__data = data
        with open(self.path, 'w') as write:
            write.write(json.dumps(data))

    def reload(self):
        u"""
        当json文件以write函数之外的方式发生改变时，用reload来更新数据数据
        :return: json文件记录的数据
        """
        if os.path.isfile(self.path):
            with open(self.path, 'r') as read:
                self.__data = json.loads(read.read())
                return self.__data

    def delete(self):
        u"""
        删除json文件
        """
        if os.path.isfile(self.path):
            os.remove(self.path)

    def __repr__(self):
        return "{self.__module__}.{self.__class__.__name__}('{self.path}')".format(self=self)


class Function(object):
    u"""
    function fn: 函数
    str name: 函数名。
    str module: 函数所在模块名。
    str fullName: 函数的长名称 module.name
    str help: 函数的帮助__doc__
    list args: 函数参数的键名
    bool keywords：是否存在**kwargs
    dict default: 默认参数的键值对
    Log log: 用来将运行日志记录到data/log/主机名.log
    Json json: 用来将储存到data/json/主机名/fullName.json
    """
    log = Log("{other}/data/log/{hostname}.log".format(other=os.path.dirname(__file__),
                                                       hostname=socket.gethostname()))

    def __init__(self, fn):
        if isinstance(fn, (str, unicode)):
            splits = fn.split(".")
            module_name = ".".join(splits[:-1])
            __import__(module_name)
            self.fn = getattr(sys.modules[module_name], splits[-1])
        elif isinstance(fn, Function):
            self.fn = fn.fn
        else:
            self.fn = fn
        self.name = self.fn.__name__
        self.module = self.fn.__module__
        self.fullName = self.module + "." + self.name
        self.json = Json("{other}/data/json/{hostname}/{name}.json".format(other=os.path.dirname(__file__),
                                                                           hostname=socket.gethostname(),
                                                                           name=self.fullName))
        args_pec = inspect.getargspec(self.fn)
        self.help = self.fn.__doc__
        self.args = args_pec.args
        self.keywords = bool(args_pec.keywords)
        if args_pec.defaults:
            self.default = dict(zip(args_pec.args[-len(args_pec.defaults)-1:], args_pec.defaults))
            if not self.json:
                self.json.write(self.default)
        else:
            self.default = {}

    def __contains__(self, arg):
        u"""
        :param arg: 参数名<str>
        :return: 函数是否具有该参数<bool>
        """
        if self.keywords:
            return True
        if arg in self.args:
            return True
        return False

    @property
    def kwargs(self):
        u"""
        记录/查询上次运行的参数，供redo调用；
        """
        if isinstance(self.json.read(), dict):
            return {key: value for key, value in self.json.read().items() if key in self}
        else:
            return {}

    @kwargs.setter
    def kwargs(self, kwargs):
        if isinstance(kwargs, dict):
            self.json.write({key: value for key, value in kwargs.items() if key in self})

    def redo(self):
        u"""
        使用上次运行记录的参数再次执行函数；
        """
        self(**self.kwargs)

    def __call__(self, **kwargs):
        u"""
        记录参数，执行函数，若运行错误，记录错误信息到日志。
        """
        try:
            self.fn(**kwargs)
            self.kwargs = kwargs
        except:
            self.log(self.log.time, self.fullName, self.log.error)
            self.log.open()
            raise

    def __repr__(self):
        u"""
        :return: QFn.function.Function(fn.fullName)
        """
        return "{self.__module__}.{self.__class__.__name__}('{self.fullName}')".format(self=self)

    def reload(self):
        u"""
        重新加载函数。
        """
        reload(sys.modules[self.module])
        self.fn = getattr(sys.modules[self.module], self.name)
