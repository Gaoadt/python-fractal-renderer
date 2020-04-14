from abc import abstractclassmethod


class IFractalSourceGenerator:
    defaultIdentation = 4

    def __init__(self):
        self.source = []
        self.margin = 0

    def getName(self, expression):
        return expression.getName(self)

    def getArgNames(self, expression):
        return [self.getName(arg.link) for arg in expression.args]

    @abstractclassmethod
    def addAssignment(self, rvalue, expression):
        pass

    def addMargin(self):
        self.margin += self.defaultIdentation

    def removeMargin(self):
        self.margin -= self.defaultIdentation

    def addToSource(self, string):
        self.source.append(" " * self.margin + string)

    def printSource(self):
        print(self.getOneSourceString())

    def getOneSourceString(self):
        return "\n".join(self.source)

    def addBinaryExpression(self, expr):
        names = self.getArgNames(expr)
        result = f"{names[0]} {expr.symbol} {names[1]}"
        self.addAssignment(result, expr)

    def addUnaryExpression(self, expr):
        result = expr.symbol + self.getName(expr.args[0].link)
        self.addAssignment(result, expr)

    def addPowerExpression(self, expr):
        names = self.getArgNames(expr)
        result = f"{names[0]} ** {names[1]}"
        self.addAssignment(result, expr)

    def getNameOperation(self, expr):
        return f"oper{expr.operIndex}"

    def getNameSpecialVar(self, expr):
        return expr.identifierName
