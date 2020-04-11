from abc import abstractclassmethod
from copy import copy, deepcopy
from expression_types import *
import sys
import expression_exceptions as exceptions


class IExpressionProcessor:
    @abstractclassmethod
    def getParsedExpression(self, expressionString):
        pass


class DefaultExpressionProcessor(IExpressionProcessor):

    unaryOperations = [UnaryPlus(), UnaryMinus()]
    binaryOperations = [SumExpr(), DivideExpr(), MultiplyExpr(),
                        SubtractExpr(), PowerExpr()]
    nameFactory = NamedVarFactory()
    float_symbols = "0123456789."
    bracket_symbols = ["()", "[]"]

    def __currentCharacter(self):
        return self.__expressionWithoutSpaces[self.__index]

    def __currentIn(self, symbols):
        return self.__currentCharacter() in symbols

    def __incrementIndex(self):
        self.__index += 1

    def __cutUnary(self):
        for operation in self.unaryOperations:
            if self.__currentCharacter() == operation.symbol:
                self.__incrementIndex()
                return deepcopy(operation).setArg(self.__getInfixExpression())
        return None

    def __isFloatConstantSymbol(self):
        return (not self.__isOver()) and self.__currentIn(self.float_symbols)

    def __isDigitSymbol(self):
        return (not self.__isOver()) and self.__currentCharacter().isdigit()

    def __isIdentifierSymbol(self):
        if self.__isOver():
            return False
        return self.__currentCharacter().isalpha() or self.__isDigitSymbol()

    def __isBracket(self, index, returnIndex):
        for symbol in self.bracket_symbols:
            if self.__currentCharacter == symbol[index]:
                return symbol[returnIndex]
        return None

    def __isFirstBracket(self):
        return self.__isBracket(0, 1)

    def __isSecondBracket(self):
        return self.__isBracket(1, 0)

    def __cutBrackets(self):
        secondBracket = self.__isFirstBracket()
        if secondBracket is not None:
            self.__incrementIndex()
            expression = self.__getValidExpression()
            if self.__isOver():
                raise exceptions.InvalidBracketsException(self.__index)
            if self.__currentCharacter() != secondBracket:
                raise exceptions.InvalidBracketsException(self.__index)
            self.__index += 1
            return expression
        return None

    def __cutFloatConstant(self):
        if not self.__isFloatConstantSymbol():
            return None
        strConstant = str()
        while self.__isFloatConstantSymbol():
            strConstant += self.__currentCharacter()
            self.__incrementIndex()
        try:
            floatConstant = float(strConstant)
            return ConstantExpr(floatConstant)
        except ValueError:
            raise exceptions.InvalidConstantException(self.__index)

    def __isOver(self):
        return self.__index >= self.__expLen

    def __isSubexprEnd(self):
        return self.__isOver() or self.__isSecondBracket() is not None

    def __isBinaryOperatorNext(self):
        for operation in self.binaryOperations:
            if operation.symbol == self.__currentCharacter():
                return True
        return False

    def __isNextBracketInfixExpr(self):
        if not self.__isOver():
            return self.__isFirstBracket() is not None
        return False

    def __getInfixExpression(self):
        if(self.__isSubexprEnd()):
            raise exceptions.UnfinishedExpressionException(self.__index)
        bracketsCutResult = self.__cutBrackets()
        if(bracketsCutResult is not None):
            if self.__isNextBracketInfixExpr():
                return deepcopy(MultiplyExpr()).setArgs(bracketsCutResult, self.__getInfixExpression())
            if not self.__isSubexprEnd():
                if not self.__isBinaryOperatorNext():
                    return deepcopy(MultiplyExpr()).setArgs(bracketsCutResult, self.__getInfixExpression())
            return bracketsCutResult
        unaryCutResult = self.__cutUnary()
        if(unaryCutResult is not None):
            return unaryCutResult
        prefixConstant = self.__cutFloatConstant()
        identifier = ""
        while(self.__isIdentifierSymbol()):
            identifier += self.__currentCharacter()
            self.__index += 1
        varConstant = None
        if identifier != "":
            varConstant = self.nameFactory.getVarByName(identifier)
        if(self.__isNextBracketInfixExpr()):
            if(varConstant is None):
                varConstant = self.__getInfixExpression()
            else:
                varConstant = deepcopy(MultiplyExpr()).setArgs(varConstant, self.__getInfixExpression())
        if prefixConstant is None:
            if varConstant is None:
                raise exceptions.UnfinishedExpressionException(self.__index)
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
        raise exceptions.UnfinishedExpressionException(self.__index)
    
    def __subLinkList(self, subResult):
        if(self.__subListIndex >= len(subResult)):
            raise exceptions.UnfinishedExpressionException(self.__index)
        currentExpression = subResult[self.__subListIndex]
        self.__subListIndex += 1
        if currentExpression.needsSubLinking:
            for i in range(currentExpression.valence):
                currentExpression.args[currentExpression.valence - 1 - i].link = self.__subLinkList(subResult)
            currentExpression.needsSubLinking = False
        return currentExpression

    def __getValidExpression(self):
        if self.__isSubexprEnd():
            raise exceptions.EmptyExpressionException(self.__index)

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
            raise exceptions.UnfinishedExpressionException(self.__index)
        
        self.__subListIndex = 0
        return self.__subLinkList(subResult[::-1])
        

            


    def getParsedExpression(self, expressionString):
        self.__expressionWithoutSpaces = ''.join(expressionString.split(' '))
        self.__index = 0
        self.__expLen = len(self.__expressionWithoutSpaces)
        expression = self.__getValidExpression()
        if not self.__isOver():
            raise exceptions.UnexpectedSymbolException(self.__index)
        return expression
    
    def isParseable(self, string):
        try:
            self.getParsedExpression(string)
            return True
        except exceptions.InvalidExpressionException:
            return False


if __name__ == '__main__':
    string = input()
    processor = DefaultExpressionProcessor()
    print(processor.getParsedExpression(string).print())
