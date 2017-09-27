# coding:utf-8
import os as _os
import args
from function import Function
from window import Window
from menu import Menu
import fn

dataDir = _os.path.dirname(__file__).replace("\\", "/")+"/data"

__all__ = ["Function", "args", "Window", "Menu", "dataDir"]
