from abc import abstractclassmethod
from copy import deepcopy


class IExpression:
    @abstractclassmethod
    def getNiceString(self):
        pass


class ExpressionLink:
    link = None


class Expression(IExpression):
    operIndex = -1
    needsSubLinking = False
    _valence = 0
    _symbol = ''
    _priority = 0

    def __init__(self):
        self._args = [ExpressionLink() for i in range(self.valence)]

    @property
    def valence(self):
        return self._valence

    @property
    def symbol(self):
        return self._symbol

    @property
    def args(self):
        return self._args

    @property
    def priority(self):
        return self._priority

    def setSubexprs(self, *args):
        for i in range(self.valence):
            self._args[i].link = args[i]
        self.needsSubLinking = False
        return self

    @abstractclassmethod
    def getNiceString(self):
        pass

    def getArgNiceString(self, index):
        return self._args[index].link.getNiceString()

    def getArgNiceStrings(self):
        return [self.getArgNiceString(index) for index in range(self.valence)]

    def surroundByBrackets(self, string):
        return f"({string})"

    def print(self):
        return f"{self.symbol} {[v.link.print() for v in self.args]}"

    def addToSource(self, sourceGenerator):
        pass

    def getName(self, sourceGenerator):
        return sourceGenerator.getNameOperation(self)


class BinaryExpr(Expression):
    _valence = 2
    _priority = 0

    def getArgNiceStringsWithBrackets(self):
        argStrs = self.getArgNiceStrings()
        if(self.args[0].link.priority < self.priority):
            argStrs[0] = self.surroundByBrackets(argStrs[0])

        if(self.args[1].link.priority <= self.priority):
            argStrs[1] = self.surroundByBrackets(argStrs[1])
        return argStrs

    def getNiceString(self):
        argStrs = self.getArgNiceStringsWithBrackets()
        return f"{argStrs[0]} {self.symbol} {argStrs[1]}"

    def addToSource(self, sourceGenerator):
        sourceGenerator.addBinaryExpression(self)


class AssociativeBinaryExpr(BinaryExpr):
    def getArgNiceStringsWithBrackets(self):
        argStrs = self.getArgNiceStrings()
        if(self.args[0].link.priority < self.priority):
            argStrs[0] = self.surroundByBrackets(argStrs[0])

        if(self.args[1].link.priority <= self.priority):
            if self.args[1].link.priority == self.priority:
                if isinstance(self, type(self.args[1].link)):
                    argStrs[1] = self.surroundByBrackets(argStrs[1])
            else:
                argStrs[1] = self.surroundByBrackets(argStrs[1])
        return argStrs


class UnaryExpr(Expression):
    _valence = 1
    _priority = 50

    def setSubexpr(self, value):
        self.args[0].link = value
        return self

    def getNiceString(self):
        return f"{self.symbol}{self.args[0].link.getNiceString()}"

    def addToSource(self, sourceGenerator):
        sourceGenerator.addUnaryExpression(self)


class MultiplyExpr(AssociativeBinaryExpr):
    _symbol = "*"
    _priority = 1


class SumExpr(AssociativeBinaryExpr):
    _symbol = "+"


class PowerExpr(BinaryExpr):
    _symbol = "^"
    _priority = 2

    def addToSource(self, sourceGenerator):
        sourceGenerator.addPowerExpression(self)


class SubtractExpr(BinaryExpr):
    _symbol = "-"


class DivideExpr(BinaryExpr):
    _symbol = "/"
    _priority = 1


class ConstantExpr(Expression):
    _priority = 100

    def __init__(self, value):
        super().__init__()
        self.value = value

    def getNiceString(self):
        if(self.value.is_integer()):
            return str(int(self.value))
        return str(self.value)

    def print(self):
        return str(self.value)

    def getName(self, sourceGenerator):
        return sourceGenerator.getNameConstant(self)


class IdentifierExpression(Expression):
    _priority = 100

    def __init__(self, identifierName):
        super().__init__()
        self.identifierName = identifierName

    def print(self):
        return self.identifierName

    def getNiceString(self):
        return self.identifierName


class NamedVarExpr(IdentifierExpression):
    def getName(self, sourceGenerator):
        return sourceGenerator.getNameVar(self)


class SpecialVarExpr(IdentifierExpression):
    def getName(self, sourceGenerator):
        return sourceGenerator.getNameSpecialVar(self)


class NamedVarFactory:
    keywords = ["pos", "x", "time"]

    def getVarByName(self, name):
        if name in self.keywords:
            return SpecialVarExpr(name)
        else:
            return NamedVarExpr(name)


class UnaryMinus(UnaryExpr):
    _symbol = "-"


class UnaryPlus(UnaryExpr):
    _symbol = '+'


class IExpressionFactory:
    _expressions = []
    @property
    def expressions(self):
        return self._expressions

    def getExpression(self, character):
        exprType = self.getExpressionType(character)
        if exprType is None:
            return None
        return exprType()

    def getExpressionType(self, character):
        for exp in self._expressions:
            if(exp.symbol == character):
                return type(exp)
        return None


class UnaryExprFactory(IExpressionFactory):
    _expressions = [UnaryMinus(), UnaryPlus()]


class BinaryExprFactory(IExpressionFactory):
    _expressions = [SumExpr(), MultiplyExpr(), SubtractExpr(),
                    DivideExpr(), PowerExpr()]

    def makeMultiplication(self, *expressions):
        expressions = [expr for expr in expressions if expr is not None]
        if len(expressions) == 0:
            return None
        currentExpr = expressions[0]
        for i in range(1, len(expressions)):
            nextExpr = MultiplyExpr()
            nextExpr.setSubexprs(currentExpr, expressions[i])
            currentExpr = nextExpr
        return currentExpr


class ConstantExprFactory(IExpressionFactory):
    _expressions = [ConstantExpr(0)]

    def getExpression(self, strConstant):
        return ConstantExpr(float(strConstant))
