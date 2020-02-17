from setup import *

class MyClass:
    def __init__(self):
        self.pure_username = pure_username

    def printVar(self):
        from test2 import secondMethod
        secondMethod(self)


inst = MyClass()
inst.printVar()
