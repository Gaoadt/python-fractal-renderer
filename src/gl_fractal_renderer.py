from OpenGL.GL import *
from OpenGL.GL.glget import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from fractal import *
from expression_processor import *
from gl_fractal_source_generator import *
from fractal_settings_window import FractalSettingWindow
import tkinter as tk
from threading import Thread
import time

class GLShaderCompilationError(Exception):
    def __init__(self, log):
        super(Exception, self).__init__(self, log)

class GLUTEvent:
    pass

class GLFractalWindow:
    
    __glutKeyToTkinter = {
        GLUT_KEY_UP : "Up",
        GLUT_KEY_DOWN : "Down",
        GLUT_KEY_LEFT : "Left",
        GLUT_KEY_RIGHT : "Right",
        GLUT_KEY_F1 : "F1",
        GLUT_KEY_F2 : "F2"
    }
    
    def __glutSpecialKeyHandler(self, key, *args):
        event = GLUTEvent()
        event.keysym = self.__glutKeyToTkinter[key]
        self.settingView.tkinterKeyPressedCallback(event)
        
    def __glCreateShader(self, shader_type, shader_source_string):

        shader = glCreateShader(shader_type)
        glShaderSource(shader, shader_source_string)
        glCompileShader(shader)
        compiledSuccesfully = glGetShaderiv(shader,GL_COMPILE_STATUS) == GL_TRUE
        if not compiledSuccesfully:
            raise GLShaderCompilationError(glGetShaderInfoLog(shader).decode("ascii"))
        return shader


    def __glDraw(self):

        glEnableClientState(GL_VERTEX_ARRAY) 
        glEnableClientState(GL_COLOR_ARRAY)      
         
        glClear(GL_COLOR_BUFFER_BIT)    
        
        if glutGet(GLUT_WINDOW_WIDTH) == 0:
            return
        wh = glutGet(GLUT_WINDOW_WIDTH) * 1.0 / glutGet(GLUT_WINDOW_HEIGHT)
        
        ctime = float(time.time()) - float(self.initTime)
        glUniformMatrix2fv(self.timeloc, 1, False, [ctime, 0.0, 0.0, ctime])
        for varIndex, varValue in self.fractalSettings.vars.items():
           glUniformMatrix2fv(self.varloc[varIndex], 1, False, [varValue,0.0,0.0,varValue])
        glVertexAttrib4f(1,self.fractalSettings.center[0], self.fractalSettings.center[1], self.fractalSettings.scale, wh)
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(-1, -1)
        glVertex2f(-1, 1)
        glVertex2f(1, 1)
        glVertex2f(1, -1)
        
        glEnd()
        glDisableClientState(GL_VERTEX_ARRAY) 
        glDisableClientState(GL_COLOR_ARRAY) 
       
        glutSwapBuffers()

    def __glInit(self):
        self.initTime = time.time()
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
        glutInitWindowSize(1000, 1000)
        glutInitWindowPosition(50, 50)
        glutInit([])
        glutCreateWindow(b"OpenGL Fractal Renderer")

        self.gpu_vendor = OpenGL.GL.VERSION.GL_1_0.glGetString(GL_VENDOR).decode("ascii")
        self.gpu_model = OpenGL.GL.VERSION.GL_1_0.glGetString(GL_RENDERER).decode("ascii")
        self.gpu_attrib_count = glGetInteger(GL_MAX_VERTEX_ATTRIBS)
        
        print(f"Found {self.gpu_vendor} {self.gpu_model}")
        print(f"GPU supports {self.gpu_attrib_count} vertex attributes")

        self.shaderProgram = glCreateProgram()
        self.shaderVertex = self.__glCreateShader(GL_VERTEX_SHADER, """
        #version 410
        layout(location = 0) in vec4 vertexPosition;
        //[0] - centerX, [1] - centerY, [2] - scaleH, [3] - width / height
        layout(location = 1) in vec4 centerAndScale;
        out mat2 pos;
        void main() {
            gl_Position = vertexPosition;
            float x = centerAndScale[0] + vertexPosition[0] / 2.0 * centerAndScale[2] * centerAndScale[3];
            float y = centerAndScale[1] + vertexPosition[1] / 2.0 * centerAndScale[2] ;
            pos = mat2(x,y,-y,x);
        }
        """)

        self.shaderSourceGenerator = GLFractalSourceGenerator()
        self.shaderSourceGenerator.generateSource(self.fractal)
        self.shaderFragment = self.__glCreateShader(GL_FRAGMENT_SHADER, self.shaderSourceGenerator.getOneSourceString())
        self.shaderSourceGenerator.printSource()
        
        
       

        glAttachShader(self.shaderProgram, self.shaderVertex)
        glAttachShader(self.shaderProgram, self.shaderFragment)

        
        

        glLinkProgram(self.shaderProgram)

        if glGetProgramiv(self.shaderProgram, GL_LINK_STATUS) != GL_TRUE:
            print("Failure")
            print(glGetProgramInfoLog(self.shaderProgram))
        glUseProgram(self.shaderProgram)
        
        self.timeloc = glGetUniformLocation(self.shaderProgram, "time")
        self.varloc = {varIndex : glGetUniformLocation(self.shaderProgram, f"xname{varIndex}") for varIndex, value in self.fractalSettings.vars.items()}

        glutSpecialFunc(self.__glutSpecialKeyHandler)
        glutDisplayFunc(self.__glDraw)
        glutIdleFunc(self.__glDraw)
        glutMainLoop()

    def __init__(self, settingView, fractal):
       self.settingView = settingView
       self.fractalSettings = self.settingView.params
       self.fractal = fractal
       self.__glInit()


class GLFractalRenderer:
    def __createWindow(self):
        self.__init_subclass__window = GLFractalWindow(self.settingView, self.fractal)

    def __init__(self,root,fractal):
        self.fractal = fractal
        self.root = root
        self.settingView = FractalSettingWindow(self.root, self.fractal)

        self.glutMainLoopThread = Thread()
        self.glutMainLoopThread.run = self.__createWindow
        self.glutMainLoopThread.start()

        
        

if __name__ == '__main__':
    GLFractalRenderer()
    