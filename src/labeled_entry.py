import tkinter as tk


class LabeledEntry:
    def __init__(self, root, labelText, entryDefault, focusOutCallback=None,
                 focusInCallback=None, quickCallback=None):
        self.Label = tk.Label(root, text=labelText)
        self.Var = tk.StringVar()
        self.Var.set(entryDefault)
        self.Entry = tk.Entry(root, textvariable=self.Var)
        if focusOutCallback is not None:
            self.Entry.bind("<FocusOut>", focusOutCallback)
        if focusInCallback is not None:
            self.Entry.bind("<FocusIn>", focusInCallback)
        if quickCallback is not None:
            self.Var.trace_add("write", quickCallback)

    def gridDefault(self, row, column):
        self.Label.grid(row=row, column=column)
        self.Entry.grid(row=row, column=column + 1)
