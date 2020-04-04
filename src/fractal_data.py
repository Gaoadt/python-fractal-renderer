from expression_processor import DefaultExpressionProcessor
from expression_exceptions import InvalidExpressionException
import functools

def ignore_exceptions(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception:
            pass
    return wrapper


class InvalidFractalDataException(Exception):
    def __init__(self, message):
        super.__init__(self, message)

class FractalData:
    processor = DefaultExpressionProcessor()
    __iterations = None
    __expression = None
    __radius = None

    def isValid(self):
        return self.__iterations != None and self.__expression != None and self.__radius != None
    
    def isIterationsValid(self):
        return self.__iterations != None
    
    def isRadiusValid(self):
        return self.__radius != None
    
    def isExpressionValid(self):
        return self.__expression != None
    
    def getExpression(self):
        return self.__expression
    
    def getIterations(self):
        return self.__iterations

    def getRadius(self):
        return self.__radius

    @ignore_exceptions
    def setIterations(self, string):
        try:
            self.__iterations = int(string)
            if(self.__iterations <= 0):
                self.__iterations = None
                raise InvalidFractalDataException("Iterations number must be positive")
        except ValueError:
            self.__iterations = None
            raise InvalidFractalDataException("Iterations number must be integer")
    
    @ignore_exceptions
    def setRadius(self, string):
        try:
            self.__radius = float(string)
            if(self.__radius < 0):
                self.__radius = None
                raise InvalidFractalDataException("Radius must not be negative")
        except ValueError:
            self.__radius = None
            raise InvalidFractalDataException("Radius must be float")
    
    @ignore_exceptions
    def setFormula(self, string):
        try:
            self.__expression = self.processor.getParsedExpression(string)
        except InvalidExpressionException as expEx:
            self.__expression = None
            raise InvalidFractalDataException(expEx.message)

