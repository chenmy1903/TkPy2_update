# -*- coding: UTF-8 -*-
"""
TkPy2++ 一个升级版的TkPy2 IDE
"""
import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as tkFileDialog
import tkinter.messagebox as tkMessageBox

from idlelib.editor import TK_TABWIDTH_DEFAULT

import defaultconfigs
from tkpy2_tools.text import TkPyTextWidget, insert_char, assert_text
from tkpy2_tools.tkpy_file import tkpy_file
from tkpy2_tools.linenumbers import TextLineNumbers


class EditorFrame(ttk.Frame):
    def __init__(self, master=None, *args, **kwargs):
        ttk.Frame.__init__(self, master, *args, **kwargs)
        self.config_file = tkpy_file('config', defaultconfigs.configs).read()
        self.yesnoopenautosave = tk.BooleanVar(value=self.config_file['auto_save'])
        self.code_save = True
        self.yesnosavefile = False
        self.file_name = None
        self.defaultextension = self.config_file['defaultextension']
        self.all_file_types = self.config_file['all_filetypes']
        self.text = TkPyTextWidget(self, font=(self.config_file['font_name'],
                                               self.config_file['font_size']),
                                   undo=True, maxundo=self.config_file['max_undo'], bd=0)
        self.linenumbers = TextLineNumbers(self, bd=0)
        self.xcrollbar = ttk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.ycrollbar = ttk.Scrollbar(self)

    def get_start(self):
        if isinstance(self.master, (tk.Tk, tk.Toplevel)):
            self.master.title(self.config_file['init_title'])
        self.ycrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        self.ycrollbar.config(command=self.text.yview)
        self.text.config(yscrollcommand=self.ycrollbar.set)
        if self.config_file['show_x_crollbar']:
            self.text.config(xscrollcommand=self.xcrollbar.set, wrap=tk.NONE)
            self.xcrollbar.pack(fill=tk.X, side=tk.BOTTOM)
            self.xcrollbar.config(command=self.text.xview)
        if self.config_file['show_line_numbers']:
            self.text.bind("<<Change>>", lambda event: self.linenumbers.redraw())
            self.text.bind("<Configure>", lambda event: self.linenumbers.redraw())
            self.linenumbers.attach(self.text)
            self.linenumbers.pack(fill=tk.Y, side=tk.LEFT)
        self.text.pack(fill=tk.BOTH, expand=True)
        self.text.insert(tk.END, self.config_file['init_text'])
        self.text.bind('"', lambda event: insert_char(self.text, '"', '"'))
        self.text.bind("'", lambda event: insert_char(self.text, "'", "'"))
        self.text.bind("(", lambda event: insert_char(self.text, ")", '('))
        self.text.bind("[", lambda event: insert_char(self.text, "]", '['))
        self.text.bind("{", lambda event: insert_char(self.text, "}", '{'))

        self.text.bind(")", lambda event: insert_char(self.text, ")", ')'))
        self.text.bind("]", lambda event: insert_char(self.text, "]", ']'))
        self.text.bind("}", lambda event: insert_char(self.text, "}", '}'))
        self.text.bind('<BackSpace>', lambda event: self.BackSpace())
        self.text.bind('<KeyRelease>', lambda event: self.assert_text())
        self.text.bind('<Control-s>', lambda event: self.save())
        self.text.bind('<Control-Shift-S>', lambda event: self.save('saveas'))
        self.set_tk_tabwidth(self.config_file['tabs_width'] or TK_TABWIDTH_DEFAULT)

    def BackSpace(self):
        index = str(self.text.index(tk.INSERT)).split('.')
        index[1] = str(int(index[1]) - 1 if int(index[1]) - 1 >= 0 else 0)
        if float('.'.join(index)) < float(f'{index[0]}.{int(index[1]) + 1}'):
            if self.text.get(f'{index[0]}.{int(index[1]) + 1}') in (')', ']', '}', '"', "'") and self.text.get(
                    f'{index[0]}.{int(index[1])}') in ('(', '[', '{', '"', "'"):
                self.text.delete(f'{index[0]}.{int(index[1]) + 1}')
                self.text.delete(f'{index[0]}.{int(index[1])}')
                return 'break'

    def pack_configure(self, **kwargs):
        self.get_start()
        ttk.Frame.pack(self, **kwargs)

    pack = pack_configure

    def place_configure(self, **kwargs):
        self.get_start()
        ttk.Frame.place(self, **kwargs)

    place = place_configure

    def grid_configure(self, **kwargs):
        self.get_start()
        ttk.Frame.grid(self, **kwargs)

    grid = grid_configure

    def get_tk_tabwidth(self):
        current = self.text['tabs'] or TK_TABWIDTH_DEFAULT
        return int(current)

    def set_tk_tabwidth(self, newtabwidth: int):
        text = self.text
        if self.get_tk_tabwidth() != newtabwidth:
            # Set text widget tab width
            pixels = text.tk.call("font", "measure", text["font"],
                                  "-displayof", text.master,
                                  "n" * newtabwidth)
            text.configure(tabs=pixels)

    def open(self, filename: str):
        self.file_name = filename
        self.text.config(state=tk.NORMAL)
        with open(filename, 'r', encoding=self.config_file['default_encoding']) as f:
            self.text.delete(0.0, tk.END)
            self.text.insert(tk.END, f.read()[0: -1])
        try:
            self.save()
        except (PermissionError, OSError):
            self.text.config(state=tk.DISABLED)

    def save(self, mode='save', *, title='保存'):
        if mode == 'save':
            if not self.file_name:
                self.file_name = tkFileDialog.asksaveasfilename(title=title, defaultextension=self.defaultextension,
                                                                filetypes=self.all_file_types)
                if not self.file_name:
                    return
            with open(self.file_name, 'w', encoding=self.config_file['default_encoding']) as f:
                f.write(self.text.get(0.0, tk.END))
            self.code_save = True
            self.yesnosavefile = True
            self.master.title(self.config_file['init_title'] + ' - ' + self.file_name)
        elif mode == 'auto_save':
            f = tkpy_file('config', defaultconfigs.configs)
            f.add('auto_save', (not self.yesnoopenautosave.get()))
            self.yesnoopenautosave.set(f.read('auto_save'))
            self.assert_text()
        elif mode == 'saveas':
            self.file_name = None
            self.yesnosavefile = False
            self.code_save = False
            self.save(title='另存为')

    def assert_text(self):
        if self.yesnosavefile:
            if self.yesnoopenautosave.get():
                self.save()
                self.code_save = True
            else:
                try:
                    with open(self.file_name, encoding=self.config_file['default_encoding']) as f:
                        if assert_text(f.read(), self.text.get(0.0, tk.END)):
                            if isinstance(self.master, (tk.Tk, tk.Toplevel)):
                                self.master.title(self.config_file['init_title'] + ' - ' +
                                                  self.file_name + ' (未保存文件)')
                            self.code_save = False
                        else:
                            self.code_save = True
                            self.master.title(self.config_file['init_title'] + ' - ' + self.file_name)
                except (FileExistsError, FileNotFoundError):
                    tkMessageBox.showinfo('提示', '文件被移动、删除或被重命名。')
                    self.code_save = False
                    self.yesnosavefile = False
                    self.assert_text()
        else:
            data = assert_text(self.config_file['init_text'] + '\n', self.text.get(0.0, tk.END))
            if data:
                if isinstance(self.master, (tk.Tk, tk.Toplevel)):
                    self.master.title(self.config_file['init_title'] + ' (未保存文件)')
                self.code_save = False
            else:
                if isinstance(self.master, (tk.Tk, tk.Toplevel)):
                    self.master.title(self.config_file['init_title'])
                self.code_save = True


def main():
    root = tk.Tk()
    root.title('TkPy2 Editor')
    edit = EditorFrame(root)
    edit.pack(fill=tk.BOTH, expand=True)
    root.mainloop()


if __name__ == '__main__':
    main()
