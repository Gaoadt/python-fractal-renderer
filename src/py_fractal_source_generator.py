from fractal import Fractal
from ifractal_source_generator import IFractalSourceGenerator


class PyFractalSourceGenerator(IFractalSourceGenerator):
    def getNameConstant(self, expr):
        return str(expr.value)

    def getNameVar(self, expr):
        return f"name[{self.fractal.identifiers[expr.identifierName]}]"

    def addAssignment(self, rvalue, expr):
        self.addToSource(self.getName(expr) + " = " + rvalue)

    def generateSource(self, fractal):
        self.fractal = fractal
        self.addToSource("def iterationFractal(x, pos, name, time):")
        self.addMargin()
        for operation in fractal.postOrder:
            operation.link.addToSource(self)
        self.addToSource(f"return {self.getName(fractal.expression.link)}")
        self.removeMargin()

    def addPowerExpression(self, expr):
        names = self.getArgNames(expr)
        result = f"{names[0]} ** {names[1]}"
        self.addAssignment(result, expr)

    def defineGlobalIterationFunction(self, scope):
        exec("\n".join(self.source), scope)
        self.printSource()


if __name__ == "__main__":
    from expression_processor import DefaultExpressionProcessor
    proc = DefaultExpressionProcessor()
    fract = Fractal(proc.getParsedExpression("x * x + pos + x"), 100, 2.0)
    gen = PyFractalSourceGenerator()
    gen.generateSource(fract)
    gen.printSource()
    gen.defineGlobalIterationFunction(globals())
    print(globals()['iterationFractal'](2, 2, {}, 0))
