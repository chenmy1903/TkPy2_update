# -*- coding: UTF-8 -*-
import platform

configs = {
    'default_highlight_name': 'default',
    'font_size': 10,
    'font_name': '黑体',
    'show_line_numbers': True,
    'show_x_crollbar': True,
    'init_text': '# -*- coding: UTF-8 -*-\n\n',
    'init_title': 'TkPy2++ Editor (Python {})'.format(platform.python_version()),
    'max_undo': None,
    'Error_color': 'red',
    'Warning_color': 'yellow',
    'Info_color': 'light_blue',
    'indent_with_tabs': False,
    'tabs_width': 4,
    'auto_save': False,
    'auto_format_pep8': True,
    'show_run_code_warning': False,
    'default_encoding': 'UTF-8',
    'defaultextension': '.py',
    'all_filetypes': (
        ('所有支持的类型', ('.py', '.pyw')),
        ('Python 源文件', '.py'),
        ('Python 无终端源文件', '.pyw')
    )
}


def init_configs(config=configs):
    from tkpy2_tools.tkpy_file import tkpy_file
    f = tkpy_file('config', config)
    f.reset()
    return f


if __name__ == "__main__":
    for key, value in init_configs().read().items():
        print(key, repr(value) if isinstance(value, str) else value, sep=': ')
