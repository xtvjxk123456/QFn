# coding:utf-8
import os as _os
import args
from function import Function
from menu import Menu
from window import Window

dataDir = _os.path.dirname(__file__).replace("\\", "/")+"/data"

__all__ = ["Function", "args", "Window", "Menu", "dataDir"]
