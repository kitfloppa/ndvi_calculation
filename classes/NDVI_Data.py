import numpy as np

from classes.Point import Point as pn
from datetime import date as dt

class NDVI_Data():
    __items = ['point', 'nday', 'date', 'path', 'ndvi ']
    
    def __init__(self, point=None, nday=None, date=None, path=None, ndvi=None):
        if not isinstance(point, pn):
            raise TypeError("Target should be a point type!")
        else: self.point = point
        
        if not isinstance(nday, int):
            raise TypeError("Nday should be int type!")
        else: self.nday = nday

        if not isinstance(date, dt):
            raise TypeError("Date should be date type!")
        else: self.date = date
        
        if not isinstance(path, str):
            raise TypeError("Path should be string type!")
        else: self.path = path

        if not isinstance(path, np.ndarray):
            raise TypeError("NDVI matrix should be numpy.ndarray type!")
        else: self.ndvi = ndvi

    def __getitem__(self, item):
        if not isinstance(item, str):
            raise TypeError("Index should be a string type!")
        
        if item == 'point': return self.point
        elif item == 'nday': return self.nday
        elif item == 'date': return self.date
        elif item == 'path': return self.path
        elif item == 'ndvi': return self.ndvi
        else: raise IndexError("Wrong index!")

    def __setitem__(self, item, value):
        if not isinstance(item, str):
            raise TypeError("Index should be a string type!")

        if item in NDVI_Data.__items:
            self[item] = value
        else: raise IndexError("Wrong index!")


    