import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
import time
from threading import Thread

class PyFractalDivergenceCalculator:
    iters = 100
    radius = 2.0
    def getDivergence(self, pos):
        val = 0 + 0j
        for i in range(self.iters):
            val = val * val + pos
            if abs(val) > self.radius:
                return i
        return -1

class PyColorProvider:
    width = 100
    height = 100
    blue = 0
    calculator = PyFractalDivergenceCalculator()

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
    def __init__(self, root):
        self.window = tk.Toplevel(root)
        self.window.title("Py Fractal Renderer")
        self.canvas = tk.Canvas(self.window,width=self.size[0], height=self.size[1], bg = 'black')
        self.buffers = (PyFractalWindowBuffer(self.canvas), PyFractalWindowBuffer(self.canvas))
        self.canvas.pack(expand=tk.YES, fill=tk.BOTH)
        self.buffers[0].setVisibility(True)
        self.canvas.bind("<Configure>",self.cvSizeChanged)
    
    def cvSizeChanged(self, event):
        self.size = (event.width, event.height)

    def getLocator(self):
        width = self.size[0] * 1.0
        height = self.size[1] * 1.0
        def locator(position):
            nonlocal width
            nonlocal height
            scale = 4.0
            
            return (position[0] - width/2) / height * scale+ (position[1] - height/2) / height * scale *1j
        return locator

    def renderFractal(self, colorProvider):
        colorProvider.width = self.size[0]
        colorProvider.height = self.size[1]
        colorProvider.posToComplex = self.getLocator()

        self.buffers = self.buffers[1], self.buffers[0]
        self.buffers[0].render(colorProvider)
        self.buffers[1].setVisibility(False)
        self.buffers[0].setVisibility(True)

class PyFractalRenderer:
    def __init__(self, fractal):
        self.fractal = fractal
        self.colorProvider = PyColorProvider()
 
global image
def run():
    global win
    cp = PyColorProvider()
    cp.width = 1968
    cp.height = 1024
    for i in range(500):
         win.renderFractal(cp)
         cp.blue += 1
         cp.blue %= 256
         print(i)

global win
if __name__ == '__main__':
    root = tk.Tk()
    win = PyFractalWindow(root)
    thread = Thread()
    thread.run = run
    thread.start()
    root.mainloop()