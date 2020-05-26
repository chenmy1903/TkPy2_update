# -*- coding: UTF-8 -*-
import builtins
import io
import keyword
import tkinter as tk

from diff_match_patch import diff_match_patch
from pygments.styles import get_style_by_name, STYLE_MAP
from pygments.token import *
import tokenize

from tkpy2_tools.tkpy_file import read_tkpy_file

highlight_name = read_tkpy_file('config')['default_highlight_name']
font_size = read_tkpy_file('config')['font_size']
font_name = read_tkpy_file('config')['font_name']


class TkPyTextWidget(tk.Text):
    def __init__(self, *args, **kwargs):
        """Construct a text widget with the parent MASTER.

                STANDARD OPTIONS

                    background, borderwidth, cursor,
                    exportselection, font, foreground,
                    highlightbackground, highlightcolor,
                    highlightthickness, insertbackground,
                    insertborderwidth, insertofftime,
                    insertontime, insertwidth, padx, pady,
                    relief, selectbackground,
                    selectborderwidth, selectforeground,
                    setgrid, takefocus,
                    xscrollcommand, yscrollcommand,

                WIDGET-SPECIFIC OPTIONS

                    autoseparators, height, maxundo,
                    spacing1, spacing2, spacing3,
                    state, tabs, undo, width, wrap,

                """
        tk.Text.__init__(self, *args, **kwargs)
# aero_pen_xl
        self.tk.eval('''
            proc widget_proxy {widget widget_command args} {

                # call the real tk widget command with the real args
                set result [uplevel [linsert $args 0 $widget_command]]

                # generate the event for certain types of commands
                if {([lindex $args 0] in {insert replace delete}) ||
                    ([lrange $args 0 2] == {mark set insert}) ||
                    ([lrange $args 0 1] == {xview moveto}) ||
                    ([lrange $args 0 1] == {xview scroll}) ||
                    ([lrange $args 0 1] == {yview moveto}) ||
                    ([lrange $args 0 1] == {yview scroll})} {

                    event generate  $widget <<Change>> -when tail
                }

                # return the result from the real widget command
                return $result
            }
            ''')
        self.tk.eval('''
            rename {widget} _{widget}
            interp alias {{}} ::{widget} {{}} widget_proxy {widget} _{widget}
        '''.format(widget=str(self)))

        self.comment = False
        self.Highlight_line()
        self.tag_configure('line', background='lightgray')

    def Highlight_line(self):
        self.tag_remove('line', 0.0, tk.END)
        self.tag_add('line', "insert linestart", "insert lineend+1c")


count = 0


def code_color(text: tk.Text, style=None):
    """color_config(text)
    p = Percolator(text)
    d = ColorDelegator()
    p.insertfilter(d)"""
    code_color_object = get_style_by_name(style or highlight_name)
    text.config(bg=code_color_object.background_color, bd=0)
    try:
        if not code_color_object.highlight_color:
            raise AttributeError
        text.config(selectbackground=code_color_object.highlight_color)
    except AttributeError:
        text.config(selectbackground='blue')
    code_color_config = code_color_object.styles
    black_colors = ('#000000', '#202020', '#232629', '#111111', '#2f1e2e', '#1e1e27', '#272822', '#002b36')
    if text.cget('bg') in black_colors:
        text.config(insertbackground='white', fg='white')
    else:
        text.config(insertbackground='black', fg='black')
    for i in range(count):
        text.tag_remove(i, 0.0, tk.END)

    def colorize(*args):
        global count
        row1, col1 = args[0].start
        row1, col1 = str(row1), str(col1)
        row2, col2 = args[0].end
        row2, col2 = str(row2), str(col2)
        start = ".".join((row1, col1))
        end = ".".join((row2, col2))
        text.tag_add(str(count), start, end)
        try:
            try:
                text.tag_config(str(count), foreground=args[1].replace(':', ' ').split(' ')[-1], font=args[2])
            except IndexError:
                text.tag_config(str(count), foreground=args[1].replace(':', ' ').split(' ')[-1])
        except tk.TclError:
            try:
                text.tag_config(str(count), foreground=args[1].replace(':', ' ').split(' ')[0])
            except tk.TclError:
                text.tag_config(str(count), font=(args[1].replace(':', ' ').split(' ')[-1], font_size + 1))
        count += 1

    try:
        for i in tokenize.tokenize(io.BytesIO(text.get(1.0, tk.END).encode("utf-8")).readline):
            if i.type == 1:
                if i.string in keyword.kwlist:
                    colorize(i, code_color_config[Keyword])
                elif i.string in dir(builtins):
                    colorize(i, code_color_config[Name.Builtin])
                elif i.string in ['self', 'cls']:
                    colorize(i, code_color_config[Keyword.Type] or code_color_config[Keyword])
                else:
                    if text.cget('bg') not in black_colors:
                        colorize(i, 'black')
                    else:
                        colorize(i, 'white')
            if i.type == tokenize.STRING:
                colorize(i, code_color_config[String])
            elif i.type == tokenize.NUMBER:
                colorize(i, code_color_config[Number])
            elif i.type == tokenize.COMMENT:
                if text.cget('bg') in black_colors:
                    colorize(i, code_color_config[Comment.Special] or code_color_config[Comment])
                else:
                    colorize(i, code_color_config[Comment])
            elif i.type == 53:
                if i.string == "," or i.string == "." or i.string == ":":
                    colorize(i, code_color_config[Keyword])
                elif i.string == "(" or i.string == ")" or i.string == "[" \
                        or i.string == "]" or i.string == "{" or i.string == "}":
                    colorize(i, "darkred")
                else:
                    colorize(i, "green")
    except (tokenize.TokenError, SyntaxError):
        pass


def insert_char(text: tk.Text, char: str, raw: str = '', go=True):
    try:
        sel = text.get(tk.SEL_FIRST, tk.SEL_LAST)
    except tk.TclError:
        pass
    else:
        insert_text = raw + sel + char
        text.delete(tk.SEL_FIRST, tk.SEL_LAST)
        text.edit_separator()
        text.insert(tk.INSERT, insert_text)
        return 'break'
    index = str(text.index(tk.INSERT)).split('.')
    if text.get(f'{index[0]}.{int(index[1])}') == char:
        if char == raw:
            text.mark_set(tk.INSERT, f'{index[0]}.{int(index[1]) + 1}')
            text.see(tk.INSERT)
            return 'break'
    if raw:
        text.insert(tk.INSERT, raw)
        if (char != raw) or (char == '"') or char == "'":
            text.insert(tk.INSERT, char)
    if go:
        text.mark_set(tk.INSERT, f'{index[0]}.{int(index[1]) + 1}')
        text.see(tk.INSERT)
    return 'break'


def assert_text(old_text, new_text):
    dmp = diff_match_patch()
    patches = dmp.patch_make(old_text, new_text)
    diff = dmp.patch_toText(patches)

    patches = dmp.patch_fromText(diff)
    new_text, _ = dmp.patch_apply(patches, old_text)
    return bool(_)


if __name__ == "__main__":
    c = 0
    items = list(STYLE_MAP.keys())


    def next_stules():
        global c
        if c >= len(items) - 1:
            c = 0
        c += 1
        code_color(text, items[c])
        button.config(text='下一个主题 (现在主题: {})'.format(items[c]), bg=text.cget('bg'), fg=text.cget('fg'))


    root = tk.Tk()
    root.title('TkPy2 Code Color')
    text = tk.Text(root, bd=0)
    code_color(text, items[c])
    button = tk.Button(root, text='下一个主题 (现在主题: {})'.format(items[c]), command=next_stules, bg=text.cget('bg'),
                       bd=0, fg=text.cget('fg'))
    text.bind('<KeyRelease>', lambda event: code_color(text, items[c]))
    button.pack(fill=tk.X, side=tk.BOTTOM)
    text.pack(fill=tk.BOTH, expand=True)
    root.mainloop()
