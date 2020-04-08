from fractal import Fractal
from expression_types import *
from expression_processor import *
from ifractal_source_generator import *

class GLFractalSourceGenerator(IFractalSourceGenerator):    
    def getName(self, expr):
        if isinstance(expr, NamedVarExpr):
            return f"xname{self.fractal.identifiers[expr.identifierName]}"
        if isinstance(expr, SpecialVarExpr):
            return expr.identifierName
        if isinstance(expr, ConstantExpr):
            return f"toComplex({str(float(expr.value))})"
        return f"oper{expr.operIndex}"
    
    def addOperation(self, expr):
        result = f"mat2 {self.getName(expr)} = "
        if isinstance(expr, SpecialVarExpr):
            return
        elif isinstance(expr, ConstantExpr):
            return
        elif isinstance(expr, NamedVarExpr):
            return
        elif isinstance(expr, UnaryExpr):
            result += expr.symbol + self.getName(expr.args[0].link)
        elif isinstance(expr, PowerExpr):
            raise RuntimeError("Rewrite expression without ^. GLSL doesn't have builtin raising to complex power, maybe our implementation of this operation will be aded later")
        elif isinstance(expr, BinaryExpr):
            result += f"{self.getName(expr.args[0].link)} {expr.symbol} {self.getName(expr.args[1].link)}"
        self.addToSource(result + ";")

    def generateSource(self, fractal):
        self.fractal = fractal
        self.addToSource("#version 410")
        self.addToSource("")
        self.addToSource("// GLSL Fragment shader")
        self.addToSource("// This shader has been create by Fractal Renderer")
        self.addToSource("// Author: Gregory Minakov")
        self.addToSource("")
        self.addToSource("const vec4 inColor = vec4(0.0,0.0,0.0,1.0);")
        self.addToSource("const vec4 outColor = vec4(1.0,1.0,1.0,1.0);")
        self.addToSource(f"const float radius = {str(float(fractal.radius))};")
        self.addToSource("in mat2 pos;")
        self.addToSource(f"uniform mat2 time;")
        for varIndex in self.fractal.identifiers.values():
            self.addToSource(f"uniform mat2 xname{varIndex};")
        self.addToSource("")
        self.addToSource("mat2 toComplex(float x) {")
        self.addMargin()
        self.addToSource("return mat2(x,0,0,x);")
        self.removeMargin()
        self.addToSource("}")
        self.addToSource("")
        self.addToSource("mat2 iteration(mat2 x) {")
        self.addMargin()
        for operation in fractal.postOrder:
            self.addOperation(operation.link)   
        self.addToSource(f"return {self.getName(fractal.expression.link)};")
        self.removeMargin()
        self.addToSource("}")
        self.addToSource("")
        self.addToSource("void main() {")
        self.addMargin()
        self.addToSource("mat2 x = mat2(0.0,0.0,0.0,0.0);")
        self.addToSource("int result = -1;")
        self.addToSource(f"for(int i = 0; i < {str(int(fractal.iterations))}; ++i) {'{'}")
        self.addMargin()
        self.addToSource("x = iteration(x);")
        self.addToSource(f"if(x[0][0] * x[0][0] + x[0][1] * x[0][1] >= {str(float(fractal.radius * fractal.radius))}) {'{'}")
        self.addMargin()
        self.addToSource("result = i;")
        self.addToSource("break;")
        self.removeMargin()
        self.addToSource("}")
        self.removeMargin()
        self.addToSource("}")
        self.addToSource("if(result < 0) {")
        self.addMargin()
        self.addToSource("gl_FragColor = inColor;")
        self.removeMargin()
        self.addToSource("}else{")
        self.addMargin()
        self.addToSource("gl_FragColor = outColor;")
        self.removeMargin()
        self.addToSource("}")
        self.removeMargin()
        self.addToSource("}")
        
    def defineGlobalIterationFunction(self, scope):
        exec("\n".join(self.source), scope)
        self.printSource()
        

if __name__ == "__main__":
    proc = DefaultExpressionProcessor()
    fract = Fractal(proc.getParsedExpression("x * x + pos"), 2.0, 100.0)
    gen  = GLFractalSourceGenerator()
    gen.generateSource(fract)
    gen.printSource()
    

