import tkinter as tk
from expression_processor import DefaultExpressionProcessor
from expression_types import Expression
from fractal_data import FractalData
from fractal import Fractal
from fractal_settings_window import FractalSettingWindow

class MainWindow:
    fractal_data = FractalData()

    def __setFieldForeground(self, field, valid):
        if valid:
            field.config(foreground = 'black')
        else:
            field.config(foreground = 'tomato')

    def __dataChangedQuickCallback(self, *args):
        self.fractal_data.setFormula(self.formula_string_var.get())
        self.fractal_data.setRadius(self.radius_string_var.get())
        self.fractal_data.setIterations(self.iterations_string_var.get())

        self.__setFieldForeground(self.formula_entry, self.fractal_data.isExpressionValid())
        self.__setFieldForeground(self.radius_entry, self.fractal_data.isRadiusValid())
        self.__setFieldForeground(self.iterations_entry, self.fractal_data.isIterationsValid())

        if self.fractal_data.isValid():
            self.render_button.config(state = "normal")
        else:
            self.render_button.config(state = "disabled")
    def __dataChangedCallback(self, *args):
        self.__dataChangedQuickCallback(*args)
        if(self.fractal_data.isExpressionValid()):
            self.formula_string_var.set(self.fractal_data.getExpression().getNiceString())
    
    def __renderButtonCallback(self, *args):
        self.__dataChangedCallback()
        if not self.fractal_data.isValid():
            return
        
        fractal = Fractal(self.fractal_data.getExpression(), self.fractal_data.getRadius(), self.fractal_data.getIterations())
        settings = FractalSettingWindow(self.root, fractal)
        

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Python Fractal Renderer by Gaoadt")
        self.main_frame = tk.Frame(self.root)
        
        self.main_label = tk.Label(self.main_frame, text = "Enter formula and parameters")
        self.main_label.grid(columnspan = 6)
        
        self.iterations_label = tk.Label(self.main_frame, text =  "Number of iterations:")
        self.iterations_label.grid(row = 1, column = 0)
        self.iterations_string_var = tk.StringVar()
        self.iterations_string_var.set(100)
        self.iterations_entry = tk.Entry(self.main_frame, textvariable = self.iterations_string_var)
        self.iterations_entry.grid(row = 1, column = 1)
        self.iterations_entry.bind("<FocusOut>", self.__dataChangedCallback)
        self.iterations_entry.bind("<FocusIn>", self.__dataChangedCallback)

        self.radius_label = tk.Label(self.main_frame, text =  "Radius of divergence:")
        self.radius_label.grid(row = 1, column = 2)
        self.radius_string_var = tk.StringVar()
        self.radius_string_var.set(2.0)
        self.radius_entry = tk.Entry(self.main_frame, textvariable = self.radius_string_var)
        self.radius_entry.grid(row = 1, column = 3)
        self.radius_entry.bind("<FocusOut>", self.__dataChangedCallback)
        self.radius_entry.bind("<FocusIn>", self.__dataChangedCallback)
        

        self.formula_label = tk.Label(self.main_frame, text =  "Iteration formula: x'(x) = ")
        self.formula_label.grid(row = 2, column = 0)
        self.formula_string_var = tk.StringVar()
        self.formula_string_var.set("x * x + pos")
        self.formula_entry = tk.Entry(self.main_frame, textvariable = self.formula_string_var, width = 100)
        self.formula_entry.grid(row = 2, column = 1, columnspan = 6)
        self.formula_entry.bind("<FocusOut>", self.__dataChangedCallback)
        self.formula_entry.bind("<FocusIn>", self.__dataChangedCallback)
        self.formula_string_var.trace_add("write", self.__dataChangedQuickCallback)

        self.name_label = tk.Label(self.main_frame, text =  "Fractal's name")
        self.name_label.grid(row = 1, column = 5)
        self.name_string_var = tk.StringVar()
        self.name_string_var.set("Some fractal")
        self.name_entry = tk.Entry(self.main_frame, textvariable = self.name_string_var)
        self.name_entry.grid(row = 1, column = 6)
        self.name_entry.bind("<FocusOut>", self.__dataChangedCallback)
        self.name_entry.bind("<FocusIn>", self.__dataChangedCallback)


        self.render_button = tk.Button(self.main_frame, text = "Render")
        self.render_button.grid(row = 4, columnspan = 6)
        self.render_button.bind("<Button-1>", self.__renderButtonCallback)
        self.main_frame.pack()
        self.root.resizable(False, False)
        self.root.mainloop()



if __name__ == '__main__':
    MainWindow()
