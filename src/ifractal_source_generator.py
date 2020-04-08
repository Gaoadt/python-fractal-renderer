from abc import abstractclassmethod

class IFractalSourceGenerator:
    def __init__(self):
        self.source = []
        self.margin = 0

    def addMargin(self):
        self.margin += 4
    
    def removeMargin(self):
        self.margin -= 4

    def addToSource(self, string):
        self.source.append(" " * self.margin + string)
            
    def printSource(self):
        print(self.getOneSourceString())
    
    def getOneSourceString(self):
        return "\n".join(self.source)