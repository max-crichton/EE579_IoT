from enum import Enum


class Device:
    def __init__(self, name, input=0, output=0):
        self.name = name
        if input != 0:
            self.input = input

        if output != 0:
            self.output = output
