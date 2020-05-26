# -*- coding: UTF-8 -*-
from __future__ import print_function, unicode_literals
import ctypes
import sys
import platform
import types
import typing

AllModules = {
    'diff_match_patch': '比较文件的不同',
    'pygments': '代码高亮主题',
    'jedi': '代码自动补全',
    'pickleshare': 'TkPy2设置',
    'flake8': '代码检查',
}


def install(install_function: typing.Union[types.LambdaType, types.FunctionType]):
    assert platform.python_version_tuple()[0] != 2, 'TkPy2只能在Python 3上运行。'

    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except Exception:
            return False

    if is_admin():
        install_function()
    else:
        if sys.version_info[0] == 3:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)

