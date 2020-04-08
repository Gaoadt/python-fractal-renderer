from fractal import Fractal
from expression_types import *
from expression_processor import *

class PyFractalSourceGenerator:
    source = []
    margin = 0

    def addMargin(self):
        self.margin += 4
    
    def removeMargin(self):
        self.margin -= 4

    def addToSource(self, string):
        self.source.append(" " * self.margin + string)
    

    def getName(self, expr):
        if isinstance(expr, NamedVarExpr):
            return f"name_{self.fractal.identifiers[expr.identifierName]}"
        if isinstance(expr, SpecialVarExpr):
            return expr.identifierName
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
        self.addToSource("def iterationFractal(x, pos):")
        self.addMargin()
        for operation in fractal.postOrder:
            self.addOperation(operation.link)   
        self.addToSource("return oper0")
        self.removeMargin()
        
    def printSource(self):
        print("\n".join(self.source))
    
    def defineGlobalIterationFunction(self, scope):
        exec("\n".join(self.source), scope)
        

if __name__ == "__main__":
    proc = DefaultExpressionProcessor()
    fract = Fractal(proc.getParsedExpression("x * x + pos + x"), 100, 2.0)
    gen  = PyFractalSourceGenerator()
    gen.generateSource(fract)
    gen.printSource()
    gen.defineGlobalIterationFunction(globals())
    print(iterationFractal(2,2))
    

