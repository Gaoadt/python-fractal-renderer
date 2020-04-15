class IFractalRenderer:
    def setDestroyCallback(self, callback):
        self._callback = callback


class IFractalRendererFactory:
    _renderString = ""
    @property
    def renderString(self):
        return self._renderString

    def setFactoryRootWindow(self, root):
        self.rootWindow = root

    def _rendererType(self, *args):
        raise RuntimeError("Renderer hasn't been initialized")

    def renderFractal(self, fractal):
        renderer = self._rendererType(self.rootWindow, fractal)
        renderer.runDrawThread()
        return renderer


class PyFractalRendererFactory(IFractalRendererFactory):
    _renderString = "Render Python"

    def __init__(self):
        from py_fractal_renderer import PyFractalRenderer
        self._rendererType = PyFractalRenderer


class GLFractalRendererFactory(IFractalRendererFactory):
    _renderString = "Render OpenGL"

    def __init__(self):
        from gl_fractal_renderer import GLFractalRenderer
        self._rendererType = GLFractalRenderer


class RendererManager:
    def __init__(self):
        self.__factories = []
        try:
            self.__factories.append(PyFractalRendererFactory())
        except Exception:
            pass

        try:
            self.__factories.append(GLFractalRendererFactory())
        except Exception:
            pass

        self.renderer = None

    def __rendererDestroyed(self):
        self.renderer = None

    @property
    def rendererFactories(self):
        return self.__factories

    def renderFractal(self, factory, fractal):
        if self.renderer is not None:
            self.renderer.destroy()
        self.renderer = factory.renderFractal(fractal)
        self.renderer.setDestroyCallback(self.__rendererDestroyed)
