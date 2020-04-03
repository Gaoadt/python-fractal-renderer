from abc import abstractclassmethod
from copy import copy, deepcopy
import sys
class IExpressionProcessor:
    @abstractclassmethod
    def getParsedExpression(self, expressionString):
        pass

class IExpression:
    @abstractclassmethod
    def getNiceString(self):
        pass

class ExpressionOperator:
    def __init__(self, symbolString, valence = 1):
        self.symbolString = symbolString
        self.valence = valence

class Expression(IExpression):
    symbol =''
    valence = 0

    def setArgs(self, *args):
        for i in range(self.valence):
            self.args[i] = args[i]
        self.needsSubLinking = False
        return self

    def print(self):
        return f"{self.symbol}({','.join([x.print() for x in self.args])})"
    
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
    args = [None, None]
    priority = 0
    needsSubLinking = False

    def getNiceString(self):
        str1 = self.args[0].getNiceString()
        if(self.args[0].priority < self.priority):
            str1 = f"({str1})"
        
        str2 = self.args[1].getNiceString()
        if(self.args[1].priority <= self.priority):
            str2 = f"({str2})"

        return f"{str1} {self.symbol} {str2}"

class AssociativeBinaryExpr(BinaryExpr):
    def getNiceString(self):
        str1 = self.args[0].getNiceString()
        if(self.args[0].priority <= self.priority):
            if(type(self.args[0]) != type(self)):
                str1 = f"({str1})"
        
        str2 = self.args[1].getNiceString()
        if(self.args[1].priority <= self.priority):
            if(type(self.args[1]) != type(self)):
                str2 = f"({str2})"

        return f"{str1} {self.symbol} {str2}"

class UnaryExpr(Expression):
    valence = 1
    args = [None]
    needsSubLinking = False
    def setArg(self, value):
        self.args[0] = value
        return self
    def getNiceString(self):
        return f"{self.symbol}{self.args[0].getNiceString()}"

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

class UnaryMinus(UnaryExpr):
    priority = 50
    symbol = "-"

class UnaryPlus(UnaryExpr):
    priority = 50
    symbol = '+'



class InvalidExpressionException(Exception):
    def __init(self, message):
        super.__init__(message)

class EmptyExpressionException(InvalidExpressionException):
    def __init__(self, index):
        super(EmptyExpressionException,self).__init__(f"Expected non-empty expression here at {index}")

class UnfinishedExpressionException(InvalidExpressionException):
    def __init__(self, index):
        super(UnfinishedExpressionException,self).__init__(f"Expected expression at {index}")

class InvalidConstantException(InvalidExpressionException):
    def __init__(self, index):
        super(InvalidConstantException,self).__init__(f"Expected valid constant at {index}")

class InvalidBracketsException(InvalidExpressionException):
    def __init__(self, index):
        super(InvalidBracketsException,self).__init__(f"Expected closing bracket ar {index}")

class UnexpectedSymbolException(InvalidExpressionException):
    def __init__(self, index):
        super(UnexpectedSymbolException,self).__init__(f"Unexpected symbol at {index}")


class DefaultExpressionProcessor(IExpressionProcessor):
    
    unaryOperations = [UnaryPlus(), UnaryMinus()]
    binaryOperations = [SumExpr(), DivideExpr(), MultiplyExpr(), SubtractExpr(), PowerExpr()]

    def __currentCharacter(self):
        return self.__expressionWithoutSpaces[self.__index]


    def __cutUnary(self):
        for operation in self.unaryOperations:
            if self.__currentCharacter() == operation.symbol:
                self.__index += 1
                return deepcopy(operation).setArg(self.__getInfixExpression())
        return None
    
    def __isFloatConstantSymbol(self):
        return (not self.__isOver()) and self. __currentCharacter() in "0123456789."
    
    def __isIdentifierSymbol(self):
        return (not self.__isOver()) and self.__currentCharacter() in "1234567890abcdefghijklmnopqrstuvwzxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

    def __cutBrackets(self):
        if self.__currentCharacter() == '(':
            self.__index += 1
            expr =  self.__getValidExpression()
            if self.__isOver():
                raise InvalidBracketsException(self.__index)
            if self.__currentCharacter() != ')':
                raise InvalidBracketsException(self.__index)
            self.__index += 1
            return expr
        return None

    def __cutFloatConstant(self):
        if not self.__isFloatConstantSymbol():
            return None
        
        strConstant = ""
        while self.__isFloatConstantSymbol():
            strConstant += self.__currentCharacter()
            self.__index += 1

        try:
            floatConstant = float(strConstant)
            return ConstantExpr(floatConstant)

        except ValueError:
            raise InvalidConstantException(self.__index)

    def __isOver(self):
        return self.__index >= self.__expLen
    

    def __isSubexprEnd(self):
        return self.__isOver() or self.__currentCharacter() == ')'
    
    def __isBinaryOperatorNext(self):
        for operation in self.binaryOperations:
            if operation.symbol == self.__currentCharacter():
                return True
        return False
    
    def __isNextBracketInfixExpr(self):      
        if not self.__isOver():
            return self.__currentCharacter() == '('
        return False


    def __getInfixExpression(self):
        if(self.__isSubexprEnd()):
            raise UnfinishedExpressionException(self.__index)
        
        bracketsCutResult = self.__cutBrackets()
        if(bracketsCutResult != None):
            if self.__isNextBracketInfixExpr():
                return deepcopy(MultiplyExpr()).setArgs(bracketsCutResult, self.__getInfixExpression())
            
            if not self.__isSubexprEnd():
                if not self.__isBinaryOperatorNext():
                    return deepcopy(MultiplyExpr()).setArgs(bracketsCutResult, self.__getInfixExpression())
            return bracketsCutResult

        unaryCutResult = self.__cutUnary()
        if(unaryCutResult != None):
            return unaryCutResult
        
        prefixConstant = self.__cutFloatConstant()
        
        identifier = ""
        while(self.__isIdentifierSymbol()):
            identifier += self.__currentCharacter()
            self.__index += 1
        
        


        varConstant = None
        if identifier != "":
            varConstant = NamedVarExpr(identifier)
        
        if(self.__isNextBracketInfixExpr()):
            if(varConstant == None):
                varConstant = self.__getInfixExpression()
            else:
                varConstant = deepcopy(MultiplyExpr()).setArgs(varConstant, self.__getInfixExpression())

        if prefixConstant == None:
            if varConstant == None:
                raise UnfinishedExpressionException(self.__index)
            else:
                return varConstant
        else:
            if varConstant == None:
                return prefixConstant
            else:
                return deepcopy(MultiplyExpr()).setArgs(prefixConstant, varConstant)
        

    def __getPairingSymbol(self):
        for operation in self.binaryOperations:
            if operation.symbol == self.__currentCharacter():
                self.__index += 1
                resOper = deepcopy(operation)
                resOper.needsSubLinking = True
                return resOper
        raise UnfinishedExpressionException(self.__index)
    
    def __subLinkList(self, subResult):
        if(self.__subListIndex >= len(subResult)):
            raise UnfinishedExpressionException(self.__index)
        currentExpression = subResult[self.__subListIndex]
        self.__subListIndex += 1
        if currentExpression.needsSubLinking:
            for i in range(currentExpression.valence):
                currentExpression.args[currentExpression.valence - 1 - i] = self.__subLinkList(subResult)
            currentExpression.needsSubLinking = False
        return currentExpression

    def __getValidExpression(self):
        if self.__isSubexprEnd():
            raise EmptyExpressionException(self.__index)

        subResult = []
        subStack = []
        while(not self.__isSubexprEnd()):
            subResult.append(self.__getInfixExpression())
            if(self.__isSubexprEnd()):
                break
            pairingSymbol = self.__getPairingSymbol()
            
            while len(subStack) != 0:
                if subStack[-1].priority < pairingSymbol.priority:
                    break
                subResult.append(subStack.pop())
               
            subStack.append(pairingSymbol)
        
        while(len(subStack) != 0):
            subResult.append(subStack.pop())

        if(len(subResult) % 2 == 0):
            raise UnfinishedExpressionException(self.__index)
        
        self.__subListIndex = 0
        return self.__subLinkList(subResult[::-1])
        

            


    def getParsedExpression(self, expressionString):
        self.__expressionWithoutSpaces = ''.join(expressionString.split(' '))
        self.__index = 0
        self.__expLen = len(self.__expressionWithoutSpaces)
        expression = self.__getValidExpression()
        if not self.__isOver():
            raise UnexpectedSymbolException(self.__index)
        return expression
    
    def isParseable(self, string):
        try:
            self.getParsedExpression(string)
            return True
        except InvalidExpressionException:
            return False


if __name__ == '__main__':
    string = input()
    processor = DefaultExpressionProcessor()
    print(processor.getParsedExpression(string).print())
