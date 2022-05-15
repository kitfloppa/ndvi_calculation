class Point():
    def __init__(self, x=None, y=None):
        self.x, self.y = x, y

    def __getitem__(self, i):
        if i == 0: return self.x
        elif i == 1: return self.y
