from math import sqrt

class Point():
    def __init__(self, x=None, y=None):
        self.x, self.y = x, y

    def __getitem__(self, i):
        if i == 0: return self.x
        elif i == 1: return self.y
        else: assert 'The arguments are only 0 or 1'

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
            if self.x<other.x:
                return True
            elif self.x==other.x and self.y<other.y:
                return True
            
            return False
        return NotImplemented