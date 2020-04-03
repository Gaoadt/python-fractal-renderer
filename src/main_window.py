import tkinter as tk
from expression_processor import DefaultExpressionProcessor

proc = DefaultExpressionProcessor()

class MainWindow:

    def __iterations_changed_callback(self, event):
        iterationsStr = self.iterations_string_var.get()
        try:
            int(iterationsStr)
            self.iterations_entry.config(foreground = 'black')
            
        except ValueError:
            self.iterations_entry.config(foreground = 'tomato')
    def __radius_changed_callback(self, event):
        radiusStr = self.radius_string_var.get()
        try:
            float(radiusStr)
            self.radius_entry.config(foreground = 'black')
            
        except ValueError:
            self.radius_entry.config(foreground = 'tomato')
    def __formula_changed_callback(self, event):
        formulaStr = self.formula_string_var.get()
        if(proc.isParseable(formulaStr)):
            self.formula_entry.config(foreground = 'black')
            self.formula_string_var.set(proc.getParsedExpression(formulaStr).getNiceString())
        else:
            self.formula_entry.config(foreground = 'tomato')        

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
        self.iterations_entry.bind("<FocusOut>", self.__iterations_changed_callback)


        self.radius_label = tk.Label(self.main_frame, text =  "Radius of divergence:")
        self.radius_label.grid(row = 1, column = 2)
        self.radius_string_var = tk.StringVar()
        self.radius_string_var.set(2.0)
        self.radius_entry = tk.Entry(self.main_frame, textvariable = self.radius_string_var)
        self.radius_entry.grid(row = 1, column = 3)
        self.radius_entry.bind("<FocusOut>", self.__radius_changed_callback)
        

        self.formula_label = tk.Label(self.main_frame, text =  "Iteration formula: x'(x) = ")
        self.formula_label.grid(row = 2, column = 0)
        self.formula_string_var = tk.StringVar()
        self.formula_string_var.set("x * x + pos")
        self.formula_entry = tk.Entry(self.main_frame, textvariable = self.formula_string_var, width = 100)
        self.formula_entry.grid(row = 2, column = 1, columnspan = 6)
        self.formula_entry.bind("<FocusOut>", self.__formula_changed_callback)
        self.formula_entry.bind("<FocusIn>", self.__formula_changed_callback)

        self.name_label = tk.Label(self.main_frame, text =  "Fractal's name")
        self.name_label.grid(row = 1, column = 5)
        self.name_string_var = tk.StringVar()
        self.name_string_var.set("Some fractal")
        self.name_entry = tk.Entry(self.main_frame, textvariable = self.name_string_var)
        self.name_entry.grid(row = 1, column = 6)


        self.render_button = tk.Button(self.main_frame, text = "Render")
        self.render_button.grid(row = 4, columnspan = 6)

        self.main_frame.pack()
        self.root.mainloop()

if __name__ == '__main__':
    MainWindow()