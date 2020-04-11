from abc import abstractclassmethod
from copy import deepcopy


class IExpression:
    @abstractclassmethod
    def getNiceString(self):
        pass


class ExpressionLink:
    link = None

class Expression(IExpression):
    symbol = ''
    valence = 0
    operIndex = -1

    def setArgs(self, *args):
        for i in range(self.valence):
            self.args[i].link = args[i]
        self.needsSubLinking = False
        return self

    def print(self):
        return f"{self.symbol}({','.join([x.link.print() for x in self.args])})"
    
    @abstractclassmethod
    def getNiceString(self):
        pass

    def __deepcopy__(self, memo={}):
        new = self.__class__()
        new.__dict__.update(self.__dict__)
        new.args = deepcopy(self.args, memo)
        return new

class BinaryExpr(Expression):
    valence = 2
    args = [ExpressionLink(), ExpressionLink()]
    priority = 0
    needsSubLinking = False

    def getNiceString(self):
        str1 = self.args[0].link.getNiceString()
        if(self.args[0].link.priority < self.priority):
            str1 = f"({str1})"
        
        str2 = self.args[1].link.getNiceString()
        if(self.args[1].link.priority <= self.priority):
            str2 = f"({str2})"

        return f"{str1} {self.symbol} {str2}"

class AssociativeBinaryExpr(BinaryExpr):
    def getNiceString(self):
        str1 = self.args[0].link.getNiceString()
        if(self.args[0].link.priority <= self.priority):
            if(type(self.args[0].link) != type(self)):
                str1 = f"({str1})"
        
        str2 = self.args[1].link.getNiceString()
        if(self.args[1].link.priority <= self.priority):
            if(type(self.args[1].link) != type(self)):
                str2 = f"({str2})"

        return f"{str1} {self.symbol} {str2}"

class UnaryExpr(Expression):
    valence = 1
    args = [ExpressionLink()]
    needsSubLinking = False
    def setArg(self, value):
        self.args[0].link = value
        return self
    def getNiceString(self):
        return f"{self.symbol}{self.args[0].link.getNiceString()}"

class MultiplyExpr(AssociativeBinaryExpr):
    symbol = "*"
    priority = 1



class SumExpr(AssociativeBinaryExpr):
    symbol = "+"

class PowerExpr(BinaryExpr):
    symbol = "^"
    priority = 2

class SubtractExpr(BinaryExpr):
    symbol = "-"

class DivideExpr(BinaryExpr):
    symbol = "/"
    priority = 1


class ConstantExpr(Expression):
    valence = 0
    args = []
    priority = 100
    needsSubLinking = False
    def __init__(self, value):
        self.value = value
    def print(self):
        return str(self.value)
    def getNiceString(self):
        if(self.value.is_integer()):
            return str(int(self.value))
        return str(self.value)

class NamedVarExpr(Expression):
    valence = 0
    needsSubLinking = False
    priority = 100
    args = []
    def __init__(self, identifierName):
        self.identifierName = identifierName
    def print(self):
        return self.identifierName
    def getNiceString(self):
        return self.identifierName


class SpecialVarExpr(Expression):
    valence = 0
    needsSubLinking = False
    priority = 100
    args = []
    def __init__(self, identifierName):
        self.identifierName = identifierName
    def print(self):
        return self.identifierName
    def getNiceString(self):
        return self.identifierName

class NamedVarFactory:
    keywords = ["pos", "x", "time"]
    def getVarByName(self, name):
        if name in self.keywords:
            return SpecialVarExpr(name)
        else:
            return NamedVarExpr(name)

class UnaryMinus(UnaryExpr):
    priority = 50
    symbol = "-"
    def getNiceString(self):
        return f"({self.symbol}{self.args[0].link.getNiceString()})"

class UnaryPlus(UnaryExpr):
    priority = 50
    symbol = '+'
    def getNiceString(self):
        return f"{self.args[0].link.getNiceString()}"


