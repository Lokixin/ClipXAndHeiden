from random import random
class FakeHeinden():
    def __init__(self, path):
        self.path = path

    
    def fakeOpenConnectInit(self, axis):
        if len(axis) > 0:
            return 0
        else:
            return 1


    def fakeConfigStreaming(self):
        return 0


    def fakeReadData(self):
        return random(), random(), random(), random()


    def fakeExit(self):
        return 0