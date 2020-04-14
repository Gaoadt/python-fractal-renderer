from abc import abstractclassmethod
from copy import copy, deepcopy
from expression_types import UnaryExprFactory, BinaryExprFactory,\
                             NamedVarFactory, ConstantExprFactory

import sys
import expression_exceptions as exceptions


class IExpressionProcessor:
    @abstractclassmethod
    def getParsedExpression(self, expressionString):
        pass


class DefaultExpressionProcessor(IExpressionProcessor):

    unaryFactory = UnaryExprFactory()
    binaryFactory = BinaryExprFactory()
    nameFactory = NamedVarFactory()
    constantFactory = ConstantExprFactory()

    float_symbols = "0123456789."
    bracket_symbols = ["()", "[]"]

    def __currentCharacter(self):
        return self.__expressionWithoutSpaces[self.__index]

    def __currentIn(self, symbols):
        return self.__currentCharacter() in symbols

    def __incrementIndex(self):
        self.__index += 1

    def __cutUnary(self):
        expression = self.unaryFactory.getExpression(self.__currentCharacter())
        if expression is not None:
            self.__incrementIndex()
        return expression

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
            if self.__currentCharacter() == symbol[index]:
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
            return self.constantFactory.getExpression(floatConstant)
        except ValueError:
            raise exceptions.InvalidConstantException(self.__index)

    def __isOver(self):
        return self.__index >= self.__expLen

    def __isSubexprEnd(self):
        return self.__isOver() or self.__isSecondBracket() is not None

    def __isBinaryOperatorNext(self):
        typ_ = self.binaryFactory.getExpressionType(self.__currentCharacter())
        return typ_ is not None

    def __isNextBracketInfixExpr(self):
        if not self.__isOver():
            return self.__isFirstBracket() is not None
        return False

    def __isInfixContinuationNext(self):
        if self.__isNextBracketInfixExpr():
            return True
        if self.__isSubexprEnd():
            return False
        return not self.__isBinaryOperatorNext()

    def __getInfixExpression(self):
        if(self.__isSubexprEnd()):
            raise exceptions.UnfinishedExpressionException(self.__index)

        brCutResult = self.__cutBrackets()
        if(brCutResult is not None):
            if self.__isInfixContinuationNext():
                nxt = self.__getInfixExpression()
                return self.binaryFactory.makeMultiplication(brCutResult, nxt)
            return brCutResult

        unaryCutResult = self.__cutUnary()
        if(unaryCutResult is not None):
            return unaryCutResult

        prefixConstant = self.__cutFloatConstant()
        identifier = ""
        while(self.__isIdentifierSymbol()):
            identifier += self.__currentCharacter()
            self.__incrementIndex()
        varConstant = None
        if identifier != "":
            varConstant = self.nameFactory.getVarByName(identifier)

        resultExprs = [prefixConstant, varConstant]
        if(self.__isNextBracketInfixExpr()):
            resultExprs.append(self.__getInfixExpression())

        expression = self.binaryFactory.makeMultiplication(*resultExprs)
        if expression is None:
            raise exceptions.UnfinishedExpressionException(self.__index)
        return expression

    def __getPairingSymbol(self):
        expr = self.binaryFactory.getExpression(self.__currentCharacter())
        if expr is None:
            raise exceptions.UnfinishedExpressionException(self.__index)
        self.__incrementIndex()
        expr.needsSubLinking = True
        return expr

    def __subLinkList(self, subResult):
        if(self.__subListIndex >= len(subResult)):
            raise exceptions.UnfinishedExpressionException(self.__index)
        currentExpression = subResult[self.__subListIndex]
        self.__subListIndex += 1
        if currentExpression.needsSubLinking:
            for i in range(currentExpression.valence - 1, -1, -1):
                currentExpression.args[i].link = self.__subLinkList(subResult)
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


if __name__ == '__main__':
    string = input()
    processor = DefaultExpressionProcessor()
    ex = processor.getParsedExpression(string)
    print(ex.getNiceString())
    print(ex.print())
