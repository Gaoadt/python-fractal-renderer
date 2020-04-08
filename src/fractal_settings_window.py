import tkinter as tk

class FractalSettings:
    center = (0,0)
    scale = 4.0
    def __init__(self, varcount):
        self.vars = {x : 0.0 for x in range(varcount)}

class FractalSettingWindow:
    params = FractalSettings(10)

    def tkinterKeyPressedCallback(self, event):
        key = event.keysym

        if key == "Return":
            self.window.focus_set()
            return

        focus = self.window.focus_get()
        if isinstance(focus, tk.Entry):
            return

        if key == "Up":
            self.onMoveCallback((0,1))
        if key == "Down":
            self.onMoveCallback((0,-1))
        if key == "Left":
            self.onMoveCallback((-1,0))
        if key == "Right":
            self.onMoveCallback((1,0))
        if key == "F1":
            self.onScaleCallback(1)
        if key == "F2":
            self.onScaleCallback(-1)
        
        self.window.focus_set()
        self.__settingExternalCallback()

    def onMoveCallback(self, direction):
        params = self.params
        params.center = (params.center[0] + params.scale * 0.1 * direction[0], params.center[1] + params.scale * 0.1 * direction[1])

    def onScaleCallback(self, sign):
        params = self.params
        params.scale *= (1/0.9) if sign < 0 else 0.9
    
    def __settingExternalCallback(self, *args):
        self.viewportCenterImagVar.set(str(self.params.center[1]))
        self.viewportCenterRealVar.set(str(self.params.center[0]))
        self.viewportScaleVar.set(str(self.params.scale))

    def __tryCastVal(self, stringVar, default, caster):
        try:
            return caster(stringVar.get())
        except ValueError:
            return default
 
    def __settingChangedCallback(self, *args):
        self.params.center = (self.__tryCastVal(self.viewportCenterRealVar, self.params.center[0], float), self.params.center[1])
        self.params.center = (self.params.center[0], self.__tryCastVal(self.viewportCenterImagVar, self.params.center[1], float))
        self.params.scale = self.__tryCastVal(self.viewportScaleVar, self.params.scale, float)
        self.__settingExternalCallback()

    def __init__(self, root, fractal):
        self.fractal = fractal
        
        self.window = tk.Toplevel(root)
        self.window.title(f"Fractal \"{fractal.expression.link.getNiceString()}\" data")

        self.viewportPanel = tk.Frame(self.window)
        self.viewportLabel = tk.Label(self.viewportPanel, text = "Viewport Settings")
        self.viewportLabel.grid(row = 0, column = 0, columnspan = 4)
        
        self.viewportCenterRealLabel = tk.Label(self.viewportPanel, text = "Center X (Real): ")
        self.viewportCenterRealLabel.grid(row = 1, column = 0)
        self.viewportCenterRealVar = tk.StringVar()
        self.viewportCenterRealVar.set("0.0")
       # self.viewportCenterRealVar.trace_add("write", self.__settingChangedCallback)
        self.viewportCenterRealEntry = tk.Entry(self.viewportPanel, textvariable = self.viewportCenterRealVar)
        self.viewportCenterRealEntry.bind("<FocusOut>",self.__settingChangedCallback)
        self.viewportCenterRealEntry.grid(row = 1, column = 1)

        self.viewportCenterImagLabel = tk.Label(self.viewportPanel, text = "Center Y (Imag): ")
        self.viewportCenterImagLabel.grid(row = 1, column = 2)
        self.viewportCenterImagVar = tk.StringVar()
        self.viewportCenterImagVar.set("0.0")
       # self.viewportCenterImagVar.trace_add("write", self.__settingChangedCallback)
        self.viewportCenterImagEntry = tk.Entry(self.viewportPanel, textvariable = self.viewportCenterImagVar)
        self.viewportCenterImagEntry.bind("<FocusOut>",self.__settingChangedCallback)
        self.viewportCenterImagEntry.grid(row = 1, column = 3)
        
        self.viewportScaleLabel = tk.Label(self.viewportPanel, text = "Scale (length of height):")
        self.viewportScaleLabel.grid(row = 2, column = 0)
        self.viewportScaleVar = tk.StringVar()
        self.viewportScaleVar.set("1.0")
     #   self.viewportScaleVar.trace_add("write", self.__settingChangedCallback)
        self.viewportScaleEntry = tk.Entry(self.viewportPanel, textvariable = self.viewportScaleVar)
        self.viewportScaleEntry.grid(row = 2, column = 1)
        self.viewportScaleEntry.bind("<FocusOut>",self.__settingChangedCallback)

        
        self.viewportPanel.pack()

        self.identLabel = tk.Label(self.window, text = "Fractal's variables")
        self.identLabel.pack()

        self.identPanel = tk.Frame(self.window)
        self.identEditables = dict()
        self.identLabels = dict()
        self.identVars = dict()

        for name, index in fractal.identifiers.items():
            self.identLabels[index] = tk.Label(self.identPanel, text = f"[{name}] = ")
            self.identLabels[index].grid(row = index, column = 0)
            
            self.identVars[index] = tk.StringVar()
            self.identEditables[index] = tk.Entry(self.identPanel, textvariable =self.identVars[index])
            self.identEditables[index].grid(row = index, column = 1) 
            self.identEditables[index].bind("<FocusOut>",self.__settingChangedCallback)
            self.identVars[index].set("0.0")
           # self.identVars[index].trace_add("write", self.__settingChangedCallback)
        self.identPanel.pack()
        self.window.resizable(False, False)
        self.window.bind("<Key>", self.tkinterKeyPressedCallback)
        self.__settingExternalCallback()

        