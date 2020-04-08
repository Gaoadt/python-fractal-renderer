from fractal import Fractal
from expression_types import *
from expression_processor import *
from ifractal_source_generator import *

class PyFractalSourceGenerator(IFractalSourceGenerator):
    def getName(self, expr):
        if isinstance(expr, NamedVarExpr):
            return f"name[{self.fractal.identifiers[expr.identifierName]}]"
        if isinstance(expr, SpecialVarExpr):
            return expr.identifierName
        if isinstance(expr, ConstantExpr):
            return str(expr.value)
        return f"oper{expr.operIndex}"
    
    def addOperation(self, expr):
        result = self.getName(expr) + " = "
        if isinstance(expr, SpecialVarExpr):
            return
        elif isinstance(expr, ConstantExpr):
            return
        elif isinstance(expr, NamedVarExpr):
            return
        elif isinstance(expr, UnaryExpr):
            result += expr.symbol + self.getName(expr.args[0].link)
        elif isinstance(expr, PowerExpr):
            result += f"{self.getName(expr.args[0].link)} ** {self.getName(expr.args[1].link)}"
        elif isinstance(expr, BinaryExpr):
            result += f"{self.getName(expr.args[0].link)} {expr.symbol} {self.getName(expr.args[1].link)}"
        self.addToSource(result)

    def generateSource(self, fractal):
        self.fractal = fractal
        self.addToSource("def iterationFractal(x, pos, name, time):")
        self.addMargin()
        for operation in fractal.postOrder:
            self.addOperation(operation.link)   
        self.addToSource(f"return {self.getName(fractal.expression.link)}")
        self.removeMargin()
    
    def defineGlobalIterationFunction(self, scope):
        exec("\n".join(self.source), scope)
        self.printSource()
        

if __name__ == "__main__":
    proc = DefaultExpressionProcessor()
    fract = Fractal(proc.getParsedExpression("x * x + pos + x"), 100, 2.0)
    gen  = PyFractalSourceGenerator()
    gen.generateSource(fract)
    gen.printSource()
    gen.defineGlobalIterationFunction(globals())
    print(iterationFractal(2,2,{}))
    

