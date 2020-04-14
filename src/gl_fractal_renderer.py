import time
import tkinter as tk
import OpenGL.GL as gl
import OpenGL.GL.VERSION.GL_1_0 as gl_v1
import OpenGL.GLUT as glut

from gl_fractal_source_generator import GLFractalSourceGenerator
from fractal_settings_window import FractalSettingWindow
from threading import Thread


class GLShaderCompilationError(Exception):
    def __init__(self, log):
        super().__init__(self, log)


class GLShaderLinkError(Exception):
    def __init__(self, log):
        super().__init__(self, log)


class GLUTEvent:
    pass


class GLFractalWindow:
    __glutKeyToTkinter = {
        glut.GLUT_KEY_UP: "Up",
        glut.GLUT_KEY_DOWN: "Down",
        glut.GLUT_KEY_LEFT: "Left",
        glut.GLUT_KEY_RIGHT: "Right",
        glut.GLUT_KEY_F1: "F1",
        glut.GLUT_KEY_F2: "F2"
    }

    def __glutSpecialKeyHandler(self, key, *args):
        event = GLUTEvent()
        event.keysym = self.__glutKeyToTkinter[key]
        self.settingView.tkinterKeyPressedCallback(event)

    def __glCreateShader(self, shader_type, shader_source_string):

        shader = gl.glCreateShader(shader_type)
        gl.glShaderSource(shader, shader_source_string)
        gl.glCompileShader(shader)
        compilationStatus = gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS)
        compiledSuccesfully = compilationStatus == gl.GL_TRUE
        if not compiledSuccesfully:
            error = gl.glGetShaderInfoLog(shader).decode("ascii")
            raise GLShaderCompilationError(error)
        return shader

    def __glCreateFragmentShader(self, shader_source):
        return self.__glCreateShader(gl.GL_FRAGMENT_SHADER, shader_source)

    def __glGetUniformLocation(self, uniform):
        return gl.glGetUniformLocation(self.shaderProgram, uniform)

    def __glSetupVarloc(self):
        self.timeloc = self.__glGetUniformLocation("time")
        self.varloc = {}
        for index in self.fractalSettings.vars.keys():
            self.varloc[index] = self.__glGetUniformLocation(f"xname{index}")

    def __glDraw(self):
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_COLOR_ARRAY)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        width = glut.glutGet(glut.GLUT_WINDOW_WIDTH)
        height = glut.glutGet(glut.GLUT_WINDOW_HEIGHT)
        if width == 0:
            return

        wh = width * 1.0 / height
        ctime = float(time.time()) - float(self.initTime)
        gl.glUniformMatrix2fv(self.timeloc, 1, False, [ctime, 0.0, 0.0, ctime])
        for varIndex, varValue in self.fractalSettings.vars.items():
            cValue = [varValue, 0.0, 0.0, varValue]
            gl.glUniformMatrix2fv(self.varloc[varIndex], 1, False, cValue)
        st = self.fractalSettings
        vertexAttrib = [st.center[0], st.center[1], st.scale, wh]
        gl.glVertexAttrib4f(1, *vertexAttrib)
        gl.glBegin(gl.GL_TRIANGLE_FAN)
        gl.glVertex2f(-1, -1)
        gl.glVertex2f(-1, 1)
        gl.glVertex2f(1, 1)
        gl.glVertex2f(1, -1)
        gl.glEnd()
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glDisableClientState(gl.GL_COLOR_ARRAY)
        glut.glutSwapBuffers()

    def __glInit(self):
        self.initTime = time.time()
        glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGB)
        glut.glutInitWindowSize(1000, 1000)
        glut.glutInitWindowPosition(50, 50)
        glut.glutInit([])
        glut.glutCreateWindow(b"OpenGL Fractal Renderer")

        self.gpu_vendor = gl_v1.glGetString(gl.GL_VENDOR).decode("ascii")
        self.gpu_model = gl_v1.glGetString(gl.GL_RENDERER).decode("ascii")
        self.gpu_attrib_count = gl.glGetInteger(gl.GL_MAX_VERTEX_ATTRIBS)

        print(f"Found {self.gpu_vendor} {self.gpu_model}")
        print(f"GPU supports {self.gpu_attrib_count} vertex attributes")

        self.shaderProgram = gl.glCreateProgram()
        self.shaderVertex = self.__glCreateShader(gl.GL_VERTEX_SHADER, """
        #version 410
        layout(location = 0) in vec4 vertexPosition;
        //[0] - centerX, [1] - centerY, [2] - scaleH, [3] - width / height
        layout(location = 1) in vec4 centerAndScale;
        out mat2 pos;
        void main() {
            gl_Position = vertexPosition;
            float x = centerAndScale[0] + vertexPosition[0] / 2.0
             * centerAndScale[2] * centerAndScale[3];
            float y = centerAndScale[1] + vertexPosition[1] / 2.0
             * centerAndScale[2] ;
            pos = mat2(x,y,-y,x);
        }
        """)

        self.shaderSourceGenerator = GLFractalSourceGenerator()
        self.shaderSourceGenerator.generateSource(self.fractal)
        self.shaderSource = self.shaderSourceGenerator.getOneSourceString()
        self.shaderFragment = self.__glCreateFragmentShader(self.shaderSource)
        self.shaderSourceGenerator.printSource()

        gl.glAttachShader(self.shaderProgram, self.shaderVertex)
        gl.glAttachShader(self.shaderProgram, self.shaderFragment)
        gl.glLinkProgram(self.shaderProgram)

        linkStatus = gl.glGetProgramiv(self.shaderProgram, gl.GL_LINK_STATUS)
        if linkStatus != gl.GL_TRUE:
            error = gl.glGetProgramInfoLog(self.shaderProgram).decode("ascii")
            raise GLShaderLinkError(error)

        gl.glUseProgram(self.shaderProgram)
        self.__glSetupVarloc()
        glut.glutSpecialFunc(self.__glutSpecialKeyHandler)
        glut.glutDisplayFunc(self.__glDraw)
        glut.glutIdleFunc(self.__glDraw)
        glut.glutMainLoop()

    def __init__(self, settingView, fractal):
        self.settingView = settingView
        self.fractalSettings = self.settingView.params
        self.fractal = fractal
        self.__glInit()


class GLFractalRenderer:
    def __createWindow(self):
        args = [self.settingView, self.fractal]
        self.__init_subclass__window = GLFractalWindow(*args)

    def __init__(self, root, fractal):
        self.fractal = fractal
        self.root = root
        self.settingView = FractalSettingWindow(self.root, self.fractal)

        self.glutMainLoopThread = Thread()
        self.glutMainLoopThread.run = self.__createWindow
        self.glutMainLoopThread.start()
