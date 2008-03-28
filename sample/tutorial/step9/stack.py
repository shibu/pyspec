# -*- coding: utf_8 -*-

class EmptyException(RuntimeError):
    pass


class Stack(object):
    def __init__(self):
        self.values = []

    def __len__(self):
        return len(self.values)

    def push(self, value):
        self.values.append(value)

    def pop(self):
        if self.values:
            value = self.values[-1]
            del self.values[-1]
            return value
        raise EmptyException()
