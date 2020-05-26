# -*- coding: UTF-8 -*-
import jedi
from .text import TkPyTextWidget


def goto_definition(event):
    assert isinstance(event.widget, TkPyTextWidget)
    text = event.widget

    source = text.get("1.0", "end")
    index = text.index("insert")
    index_parts = index.split(".")
    line, column = int(index_parts[0]), int(index_parts[1])
    # TODO: find current editor filename
    script = jedi.Script(source, line=line, column=column, path="")
    defs = script.goto_definitions()
    if len(defs) > 0:
        module_path = defs[0].module_path
        module_name = defs[0].module_name
        line = defs[0].line
        print(line, module_name, module_path)
