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