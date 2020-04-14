from expression_types import NamedVarExpr, ExpressionLink


class Fractal:

    def __init__(self, expression, radius, iterations):
        self.postOrder = []
        self.expression = ExpressionLink()
        self.identifiers = None
        self.operIndex = 0
        self.expression.link = expression
        self.radius = radius
        self.iterations = iterations
        self.buildIdentifierDictionary()

    def putIdentifier(self, expression):
        self.identifiers[expression.identifierName] = len(self.identifiers)

    def dfsIdentifierFinder(self, nodeLink):
        expression = nodeLink.link
        expression.operIndex = self.operIndex
        self.operIndex += 1

        if isinstance(expression, NamedVarExpr):
            if expression.identifierName not in self.identifiers.keys():
                self.putIdentifier(expression)
        for x in expression.args:
            self.dfsIdentifierFinder(x)

        self.postOrder.append(nodeLink)

    def buildIdentifierDictionary(self):
        self.identifiers = dict()
        self.dfsIdentifierFinder(self.expression)
