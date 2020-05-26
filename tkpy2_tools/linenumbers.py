# -*- coding: UTF-8 -*-
import tkinter as tk

from tkpy2_tools.tkpy_file import read_tkpy_file
from tkpy2_tools.text import TkPyTextWidget, code_color

config = read_tkpy_file('config')


class TextLineNumbers(tk.Canvas):
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.textwidget = None

    def attach(self, text_widget: tk.Text):
        self.textwidget = text_widget
        code_color(self.textwidget)
        self.config(bg=self.textwidget['bg'])

    def redraw(self):
        """redraw line numbers"""
        self.delete("all")
        self.textwidget.Highlight_line()
        code_color(self.textwidget)
        i = self.textwidget.index("@0,0")

        while True:
            self.config(
                width=config['font_size'] * max(
                    [len(str(i)) for i in range(len(self.textwidget.get(0.0, tk.END).split('\n')))]))
            dline = self.textwidget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = str(i).split(".")[0]
            if linenum != str(self.textwidget.index(tk.INSERT)).split('.')[0]:
                self.create_text(5, y, anchor=tk.NW, text=linenum, fill='gray',
                                 font=(config['font_name'], config['font_size']))
                # self.textwidget.tag_add('LineNumberHighlight', self.textwidget.index('insert').split('.')[0] + '.0',
                #                       self.textwidget.index(
                #                            '{}.end'.format(self.textwidget.index('insert').split('.')[0])))
            else:
                self.create_text(5, y, anchor=tk.NW, text=linenum, fill='#4989f3',
                                 font=(config['font_name'], config['font_size']))
            i = self.textwidget.index("%s+1line" % i)


if __name__ == "__main__":
    root = tk.Tk()
    root.title('TkPy2 Test')
    text = TkPyTextWidget(root, font=(config['font_name'], config['font_size']))
    scrollbar = tk.Scrollbar(root, command=text.yview)
    text.config(yscrollcommand=scrollbar.set)
    linenumber = TextLineNumbers(root)
    linenumber.pack(side=tk.LEFT, fill=tk.Y)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    text.pack(fill=tk.BOTH, expand=True)
    linenumber.attach(text)
    text.bind("<<Change>>", lambda event: linenumber.redraw())
    text.bind("<Configure>", lambda event: linenumber.redraw())
    text.bind("<KeyRelease>", lambda event: linenumber.redraw())
    root.mainloop()
