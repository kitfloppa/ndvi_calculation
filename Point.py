import numpy as np

from math import sqrt

class Point():
    def __init__(self, x=None, y=None):
        self.x, self.y = x, y

    def __getitem__(self, i):
        if i == 0: return self.x
        elif i == 1: return self.y

    def __eq__(self, other):
        if isinstance(other, Point):
            return self.x == other.x and self.y == other.y
        else: return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        
        if result is NotImplemented:
            return result
        else: return not result

    def __lt__(self, other):
        if isinstance(other, Point):
            if self.x < other.x:
                return True
            elif self.x == other.x and self.y < other.y:
                return True
            else: return False
        else: return NotImplemented

    def __gt__(self, other):
        if isinstance(other, Point):
            if self.x > other.x:
                return True
            elif self.x == other.x and self.y > other.y:
                return True
            else: return False
        else: return NotImplemented

    def __str__(self):
        return "({0}, {1})".format(self.x, self.y)

    def distance(self, other):
        return sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)