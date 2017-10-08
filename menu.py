# coding:utf-8
import os
import json
from window import Window


class Menu(object):
    @staticmethod
    def get_menu_data(path):
        children = []
        for name in set(os.path.splitext(name)[0] for name in os.listdir(path)):
            child = dict(name=name)
            child["path"] = path + "/" + name
            for ext in [".jpg", ".png", ".svg"]:
                if os.path.isfile(child["path"] + ext):
                    child["icon"] = child["path"] + ext
            if os.path.isdir(child["path"]):
                child["children"] = Menu.get_menu_data(child["path"])
            else:
                child["path"] = child["path"] + ".yaml"
                if not os.path.isfile(child["path"]):
                    continue
            children.append(child)
        return children

    def __init__(self, path):
        self.path = path
        self.cache = {}

    def write(self):
        u"""
        遍历path文件夹下的文件，获取建立菜单需要的菜单数据列表，储存在self.path+"/menu.json"下。
        菜单数据列表为菜单数据构成的列表。每菜单数据结构如下。
        {
            "path": 对应文件夹或yaml文件路径，
            "icon": 对应图标路径，
            "html": 对应帮助路径，
            "name": 菜单名，
            "children": 子菜单数据列表
        }
        该方法在仅需在更新菜单时运行一次。
        """
        if os.path.isdir(self.path):
            with open(self.path+"/menu.json", "w") as data:
                data.write(json.dumps(self.get_menu_data(self.path), indent=4))

    def read(self):
        """
        直接读取self.path+"/menu.json"中的数据创建菜单，避免遍历文件夹。
        """
        with open(self.path + "/menu.json", "r") as data:
            return json.loads(data.read())

    def apply(self, path):
        """
        :param path: yaml文件路径。
        通过yaml文件创建窗口并显示。
        窗口会储存在cache中，避免重复创建。
        若yaml中仅记录一个无参函数，则直接运行。
        """
        if path in self.cache:
            if isinstance(self.cache[path], Window):
                self.cache[path].showNormal()
            else:
                self.cache[path].redo()
        else:
            window = Window(path)
            if len(window.options) == 1 and len(window.options.values()[0].widgets) == 0:
                self.cache[path] = window.options.items()[0].fn
            else:
                self.cache[path] = window
            self.apply(path)

    def reload(self):
        u"""
        重新加载所有已创建窗口对应函数的模块。
        在修改测试函数时避免重新创建窗口。
        """
        for value in self.cache.values():
            if isinstance(value, Window):
                for option in value.options.values():
                    option.fn.reload()
            else:
                value.reload()
