import tkinter as tk
import time
from copy import copy, deepcopy
from threading import Thread
from PIL import Image, ImageDraw, ImageTk
from fractal_settings_window import FractalSettingWindow
from fractal import Fractal
from expression_processor import DefaultExpressionProcessor
from py_fractal_source_generator import PyFractalSourceGenerator


class PyFractalDivergenceCalculator:
    def __init__(self, fractal):
        self.iteration = iterationFractal
        self.iters = fractal.iterations
        self.radius = fractal.radius
        self.time = 0.0
        
    def setVars(self, vars):
        self.vars = copy(vars)

    def getDivergence(self, pos):
        val = 0 + 0j
        for i in range(self.iters):
            val = self.iteration(val, pos, self.vars, self.time)
            if abs(val) > self.radius:
                return i
        return -1

class PyColorProvider:
    width = 100
    height = 100
    blue = 0
    
    def __init__(self, fractal):
        
        self.calculator = PyFractalDivergenceCalculator(fractal)

    def posToComplex(self, position):
        return 0 + 0j

    def getColor(self, position):
        res = self.calculator.getDivergence(self.posToComplex(position))
        return (0,0,0,255) if res < 0 else (255,255,255,255)

class PyFractalWindowBuffer:
    def setVisibility(self, visible):
        stateStr = "normal" if visible else "hidden"
        self.canvas.itemconfig(self.id, state = stateStr)
    
    def render(self, colorProvider):
        self.canvas.delete(self.id)
        self.image = Image.new("RGBA", (colorProvider.width, colorProvider.height), "white")
        self.draw = ImageDraw.Draw(self.image) 
        for i in range(colorProvider.width):
            for j in range(colorProvider.height):
                self.draw.point((i,j), colorProvider.getColor((i,j))) 
        self.photoImage = ImageTk.PhotoImage(image = self.image)
        self.id = self.canvas.create_image(0,0,image = self.photoImage, anchor = tk.NW)
     
    def __init__(self, canvas):
        self.image = Image.new("RGBA", (0,0), "white")
        self.draw = ImageDraw.Draw(self.image)
        
        self.photoImage = ImageTk.PhotoImage(image = self.image)
        self.canvas = canvas
        self.id = canvas.create_image(0,0,image = self.photoImage, anchor = tk.NW)
        

class PyFractalWindow:
    size = (200,200)
    def __init__(self, root, settingsView):
        self.settingsView = settingsView
        self.initTime = time.time()
        self.window = tk.Toplevel(root)
        self.window.title("Py Fractal Renderer")
        self.canvas = tk.Canvas(self.window,width=self.size[0], height=self.size[1], bg = 'black')
        self.buffers = (PyFractalWindowBuffer(self.canvas), PyFractalWindowBuffer(self.canvas))
        self.canvas.pack(expand=tk.YES, fill=tk.BOTH)
        self.buffers[0].setVisibility(True)
        self.canvas.bind("<Configure>",self.cvSizeChanged)
        self.window.bind("<Key>", self.settingsView.tkinterKeyPressedCallback)
        

    def cvSizeChanged(self, event):
        self.size = (event.width, event.height)

    def getLocator(self):
        width = self.size[0] * 1.0
        height = self.size[1] * 1.0
        center = copy(self.settingsView.params.center)
        scale = copy(self.settingsView.params.scale)


        def locator(position):
            nonlocal width
            nonlocal height
            nonlocal center
            nonlocal scale

            
            return (position[0] - width / 2) / height * scale + center[0] + ((height/2 - position[1]) / height * scale + center[1])* 1j
        return locator

    def renderFractal(self, colorProvider):
        colorProvider.width = self.size[0]
        colorProvider.height = self.size[1]
        colorProvider.posToComplex = self.getLocator()
        colorProvider.calculator.setVars(self.settingsView.params.vars) 
        colorProvider.calculator.time = float(time.time()) - float(self.initTime)

        self.buffers = self.buffers[1], self.buffers[0]
        self.buffers[0].render(colorProvider)
        self.buffers[1].setVisibility(False)
        self.buffers[0].setVisibility(True)
        
       

class PyFractalRenderer:
    drawFlag = True
    
    def __init__(self, root, fractal):
        self.fractal = fractal
        self.root = root
        self.generator = PyFractalSourceGenerator()
        self.generator.generateSource(fractal)
        self.generator.defineGlobalIterationFunction(globals())
        self.setting = FractalSettingWindow(root, fractal)
        
        self.win = PyFractalWindow(root, self.setting)
        
        self.win.window.bind("<Destroy>", self.killAll)
        self.setting.window.bind("<Destroy>",self.killAll)

        self.colorProvider = PyColorProvider(fractal)
    
    def runDrawThread(self):
        thread = Thread()
        thread.run = self.__drawLoop
        thread.start()
        self.drawThread = thread
    
    def __drawLoop(self):
        while self.drawFlag:
            try:
                self.win.renderFractal(self.colorProvider)
            except Exception:
                pass
    
    def __kill(self):
        self.drawFlag = False
        if(self.drawThread.daemon):   
            self.drawThread.join()  
        try:
            self.setting.window.destroy()
        except Exception:
            pass
        
        try:
            self.win.window.destroy()
        except Exception:
            pass

    def killAll(self, *args):
        thread = Thread()
        thread.run = self.__kill
        thread.start()
        self.killThread = thread
        
if __name__ == '__main__':
    proc = DefaultExpressionProcessor()
    fractal = Fractal(proc.getParsedExpression("x * x * x + pos + time"),
                      2.0, 100)
    root = tk.Tk()
    renderer = PyFractalRenderer(root, fractal)
    renderer.runDrawThread()
    root.mainloop()
