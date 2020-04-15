import tkinter as tk
from labeled_entry import LabeledEntry


class FractalSettings:
    def __init__(self, varcount):
        self.center = (0, 0)
        self.scale = 4.0
        self.vars = {x: 0.0 for x in range(varcount)}


class FractalSettingWindow:
    def tkinterKeyPressedCallback(self, event):
        key = event.keysym
        if key == "Return":
            self.window.focus_set()
            return

        focus = self.window.focus_get()
        if isinstance(focus, tk.Entry):
            return

        callbackArgs = self.__tkinterKeyToFuncArgs[key]
        callbackArgs[0](*(callbackArgs[1:]))
        self.window.focus_set()
        self.__settingExternalCallback()

    def onMoveCallback(self, direction):
        params = self.params
        params.center = (params.center[0] + params.scale * 0.1 * direction[0],
                         params.center[1] + params.scale * 0.1 * direction[1])

    def onScaleCallback(self, sign):
        params = self.params
        params.scale *= (1/0.9) if sign < 0 else 0.9

    def __settingExternalCallback(self, *args):
        self.viewportCenterImag.Var.set(str(self.params.center[1]))
        self.viewportCenterReal.Var.set(str(self.params.center[0]))
        self.viewportScale.Var.set(str(self.params.scale))
        for index, le in self.ident.items():
            le.Var.set(self.params.vars[index])

    def __tryCastVal(self, stringVar, default, caster):
        try:
            return caster(stringVar.get())
        except ValueError:
            return default

    def __settingChangedCallback(self, *args):
        self.params.center = (self.__tryCastVal(self.viewportCenterReal.Var,
                              self.params.center[0], float),
                              self.params.center[1])
        self.params.center = (self.params.center[0],
                              self.__tryCastVal(self.viewportCenterImag.Var,
                                                self.params.center[1],
                                                float))
        self.params.scale = self.__tryCastVal(self.viewportScale.Var,
                                              self.params.scale,
                                              float)
        for ind, le in self.ident.items():
            self.params.vars[ind] = self.__tryCastVal(le.Var,
                                                      self.params.vars[ind],
                                                      float)

        self.__settingExternalCallback()

    def __init__(self, root, fractal):
        self.params = FractalSettings(len(fractal.identifiers))
        self.fractal = fractal
        self.__tkinterKeyToFuncArgs = {
            "Up": (self.onMoveCallback, (0, 1)),
            "Down": (self.onMoveCallback, (0, -1)),
            "Left": (self.onMoveCallback, (-1, 0)),
            "Right": (self.onMoveCallback, (1, 0)),
            "F1": (self.onScaleCallback, 1),
            "F2": (self.onScaleCallback, -1)
        }

        self.window = tk.Toplevel(root)
        title = f"Fractal \"{fractal.expression.link.getNiceString()}\" data"
        self.window.title(title)

        self.viewportPanel = tk.Frame(self.window)
        self.viewportLabel = tk.Label(self.viewportPanel, 
                                      text="Viewport Settings")
        self.viewportLabel.grid(row=0, column=0, columnspan=4)

        self.viewportCenterReal = LabeledEntry(self.viewportPanel,
                                               "Centet X (Real): ", "0.0",
                                               self.__settingChangedCallback)
        self.viewportCenterReal.gridDefault(1,0)

        self.viewportCenterImag = LabeledEntry(self.viewportPanel,
                                               "Centet Y (Imag): ", "0.0",
                                               self.__settingChangedCallback)
        self.viewportCenterImag.gridDefault(1,2)

        self.viewportScale = LabeledEntry(self.viewportPanel,
                                          "Scale (length of height):",
                                          "1.0",
                                          self.__settingChangedCallback)
        self.viewportScale.gridDefault(2,0)

        self.viewportPanel.pack()

        self.identLabel = tk.Label(self.window, text="Fractal's variables")
        self.identLabel.pack()

        self.identPanel = tk.Frame(self.window)
        self.ident = dict()
        for name, index in fractal.identifiers.items():
            self.ident[index] = LabeledEntry(self.identPanel,
                                             f"[{name}] = ",
                                             "0.0",
                                             self.__settingChangedCallback)
            self.ident[index].gridDefault(index, 0)
        self.identPanel.pack()
        self.window.resizable(False, False)
        self.window.bind("<Key>", self.tkinterKeyPressedCallback)
        self.__settingExternalCallback()
