import tkinter as tk

class FractalSettingWindow:
    
    def __settingChangedCallback(self, *args):
        pass

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
        self.viewportCenterRealVar.trace_add("write", self.__settingChangedCallback)
        self.viewportCenterRealEntry = tk.Entry(self.viewportPanel, textvariable = self.viewportCenterRealVar)
        self.viewportCenterRealEntry.grid(row = 1, column = 1)

        self.viewportCenterImagLabel = tk.Label(self.viewportPanel, text = "Center X (Real): ")
        self.viewportCenterImagLabel.grid(row = 1, column = 2)
        self.viewportCenterImagVar = tk.StringVar()
        self.viewportCenterImagVar.set("0.0")
        self.viewportCenterImagVar.trace_add("write", self.__settingChangedCallback)
        self.viewportCenterImagEntry = tk.Entry(self.viewportPanel, textvariable = self.viewportCenterImagVar)
        self.viewportCenterImagEntry.grid(row = 1, column = 3)
        
        self.viewportScaleLabel = tk.Label(self.viewportPanel, text = "Scale (length of height):")
        self.viewportScaleLabel.grid(row = 2, column = 0)
        self.viewportScaleVar = tk.StringVar()
        self.viewportScaleVar.set("1.0")
        self.viewportScaleVar.trace_add("write", self.__settingChangedCallback)
        self.viewportScaleEntry = tk.Entry(self.viewportPanel, textvariable = self.viewportScaleVar)
        self.viewportScaleEntry.grid(row = 2, column = 1)

        
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
            self.identVars[index].set("0.0")
            self.identVars[index].trace_add("write", self.__settingChangedCallback)
        self.identPanel.pack()
        self.window.resizable(False, False)

        