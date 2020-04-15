import tkinter as tk
from labeled_entry import LabeledEntry
from fractal_data import FractalData
from fractal import Fractal
from fractal_settings_window import FractalSettingWindow
from renderer_manager import RendererManager
from functools import partial


class MainWindow:
    fractal_data = FractalData()
    rendererManager = RendererManager()

    def __setFieldForeground(self, field, valid):
        fgColor = 'black' if valid else 'tomato'
        field.config(foreground=fgColor)

    def __dataChangedQuickCallback(self, *args):
        for le, (setVal, isVal) in self.__callbackDict.items():
            setVal(le.Var.get())
            self.__setFieldForeground(le.Entry, isVal())
        rButtonState = "normal" if self.fractal_data.isValid() else "disabled"
        for button in self.buttons:
            button.config(state=rButtonState)

    def __dataChangedCallback(self, *args):
        self.__dataChangedQuickCallback(*args)
        if(self.fractal_data.isExpressionValid()):
            niceString = self.fractal_data.getExpression().getNiceString()
            self.formula.Var.set(niceString)

    def makeMainframeLE(self, labeldef, entrydef):
        return LabeledEntry(self.main_frame, labeldef,
                            entrydef, self.__dataChangedCallback,
                            self.__dataChangedCallback,
                            self.__dataChangedQuickCallback)

    def __renderCallback(self, factory, *args):
        self.__dataChangedCallback()
        if not self.fractal_data.isValid():
            return
        fractal = Fractal(self.fractal_data.getExpression(),
                          self.fractal_data.getRadius(),
                          self.fractal_data.getIterations())
        self.rendererManager.renderFractal(factory, fractal)

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Python Fractal Renderer by Gaoadt")
        self.main_frame = tk.Frame(self.root)
        self.main_label_text = "Enter formula and parameters"
        self.main_label = tk.Label(self.main_frame, text=self.main_label_text)
        self.main_label.grid(columnspan=6)
        self.iterations = self.makeMainframeLE("Number of iterations", "100")
        self.iterations.gridDefault(1, 0)
        self.radius = self.makeMainframeLE("Radius of divergence", "2.0")
        self.radius.gridDefault(1, 3)
        self.formula = self.makeMainframeLE("Iterations formula x'(x)=",
                                            "x * x + pos")
        self.formula.Label.grid(row=2, column=0)
        self.formula.Entry.config(width=100)
        self.formula.Entry.grid(row=2, column=1, columnspan=6)
        self.name = self.makeMainframeLE("Fractal's name", "Some fractal")
        self.name.gridDefault(1, 5)
        self.__callbackDict = {
            self.formula: (self.fractal_data.setFormula,
                           self.fractal_data.isExpressionValid),
            self.radius: (self.fractal_data.setRadius,
                          self.fractal_data.isRadiusValid),
            self.iterations: (self.fractal_data.setIterations,
                              self.fractal_data.isIterationsValid)
        }
        self.buttons = []
        for ind, factory in enumerate(self.rendererManager.rendererFactories):
            self.buttons.append(tk.Button(self.main_frame,
                                          text=factory.renderString))
            self.buttons[ind].grid(row=4+ind, columnspan=6)
            self.buttons[ind].bind("<Button-1>", partial(self.__renderCallback,
                                                         factory))
            factory.setFactoryRootWindow(self.root)
        self.main_frame.pack()
        self.root.resizable(False, False)
        self.root.mainloop()


if __name__ == '__main__':
    MainWindow()
