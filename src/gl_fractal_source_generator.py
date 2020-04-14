from fractal import Fractal
from ifractal_source_generator import IFractalSourceGenerator


class GLFractalSourceGenerator(IFractalSourceGenerator):
    def getNameConstant(self, expr):
        return f"toComplex({str(float(expr.value))})"

    def getNameVar(self, expr):
        return f"xname{self.fractal.identifiers[expr.identifierName]}"

    def addPowerExpression(self, expression):
        raise RuntimeError("""Rewrite expression without ^. 
                                  GLSL doesn't have builtin raising to complex
                                  power, maybe our implementation of this 
                                  operation will be aded later""")

    def addBreakCondition(self):
        fractal = self.fractal
        valSqr = "x[0][0] * x[0][0] + x[0][1] * x[0][1]"
        radSqr = str(float(fractal.radius * fractal.radius))
        self.addToSource(f"if({valSqr} >= {radSqr}) {'{'}")

    def addForLoop(self):
        fractal = self.fractal
        iStr = str(int(fractal.iterations))
        self.addToSource(f"for(int i = 0; i < {iStr}; ++i) {'{'}")

    def addAssignment(self, rvalue, expr):
        self.addToSource("mat2 "+self.getName(expr) + " = " + rvalue+";")

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
            operation.link.addToSource(self)
        self.addToSource(f"return {self.getName(fractal.expression.link)};")
        self.removeMargin()
        self.addToSource("}")
        self.addToSource("")
        self.addToSource("void main() {")
        self.addMargin()
        self.addToSource("mat2 x = mat2(0.0,0.0,0.0,0.0);")
        self.addToSource("int result = -1;")
        self.addForLoop()
        self.addMargin()
        self.addToSource("x = iteration(x);")
        self.addBreakCondition()
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


if __name__ == "__main__":
    from expression_processor import DefaultExpressionProcessor
    proc = DefaultExpressionProcessor()
    fract = Fractal(proc.getParsedExpression("x * x + pos"), 2.0, 100.0)
    gen = GLFractalSourceGenerator()
    gen.generateSource(fract)
    gen.printSource()
