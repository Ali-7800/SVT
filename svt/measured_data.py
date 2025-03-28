from svt.units import Unit
from svt._check import Check
import matplotlib.pyplot as plt
import numpy as np

class Measured:
    def __init__(self,value,unit:Unit):
        Check.object_class(unit,Unit,"unit")
        self.unit = unit
        Check.object_class_validity(value,self.valid_values(),"value")
        self.value = value*self.unit.alternate_prefix.multiplier
        self.unit.alternate_prefix.multiplier = 1.0
        self.unit.alternate_prefix.power = self.unit.alternate_prefix.SI_power
        self.unit.prefix = self.unit.prefix_ratio*self.unit.alternate_prefix
        self.shape = self._shape()
    
    def convert_to(self,prefix:str):
            new_unit = self.unit.update_prefix(prefix)
            return Measured(self.value,new_unit)
        
    def __neg__(self):
        return Measured(-self.value,self.unit)

    def __add__(self,other):
        if isinstance(other, Measured):
            if (other.unit == self.unit)>0:
                m1,m2,new_unit = Unit.unify_prefixes(self.unit,other.unit)
                return Measured(m1*self.value + m2*other.value,new_unit)
            else:
                raise ValueError("Measured objects must have the same unit symbols and dimensions for addition")
        return NotImplemented
    
    def __sub__(self,other):
        if isinstance(other, Measured):
            if (other.unit == self.unit)>0:
                m1,m2,new_unit = Unit.unify_prefixes(self.unit,other.unit)
                return Measured(m1*self.value - m2*other.value,new_unit)
            else:
                raise ValueError("Measured objects must have the same units for subtraction")
        return NotImplemented
    
    def __mul__(self, other):
        if isinstance(other, Measured):
            return Measured(self.value * other.value,self.unit*other.unit)
        elif isinstance(other, (int, float)):
            return Measured(self.value * other,self.unit)
        return NotImplemented

    def __rmul__(self, other):
        if isinstance(other, Measured):
            return Measured(self.value * other.value,self.unit*other.unit)
        elif isinstance(other, (int, float)):
            return Measured(self.value * other,self.unit)
        return NotImplemented
    
    def __truediv__(self, other):
        if isinstance(other, Measured):
            return Measured(self.value / other.value,self.unit/other.unit)
        elif isinstance(other, (int, float)):
            return Measured(self.value / other,self.unit)
        return NotImplemented
    
    def __rtruediv__(self,other):
        if isinstance(other, Measured):
            return Measured(other.value / self.value,other.unit/self.unit)
        elif isinstance(other, (int, float)):
            return Measured(other / self.value,1/self.unit)
        return NotImplemented
    
    def __pow__(self,exponent):
        if isinstance(exponent,int):
            return Measured(self.value**exponent,self.unit**exponent)
        return NotImplemented

    def __str__(self):
        return str(self.value)+self.unit.__str__()
    
    def _shape(self):
        if isinstance(self.value,(int, float)):
            return 1
        elif isinstance(self.value,np.ndarray):
            return self.value.shape
    
    def copy(self):
        return Measured(self.value,self.unit)
    
    def valid_values(self):
        return [int,float,np.ndarray]

    class Collection:
        def __init__(
            self,
            **kwargs) -> None:
            self.keys = []
            for key in kwargs.keys():
                Check.object_class(kwargs[key],Measured,"","Every keyword argument in Measured.Collection must be an instance of Measured")
                setattr(self, key, kwargs[key])
            self.keys+=kwargs.keys()
            
        def append(self,key,data):
            Check.object_class(data,Measured,"","Only Measured objects can be appended to a Measured.Collection")
            Check.condition(key not in self.keys,KeyError,"Key already used for other Measured object in collection, please use a different key")
            setattr(self, key, data)
            self.keys.append(key)
        
        def plot2D(self,x_key:str,y_key:str,**kwargs):
            Check.validity(x_key,"key1",self.keys)
            Check.validity(y_key,"key2",self.keys)
            x = getattr(self,x_key)
            y = getattr(self,y_key)
            Check.condition(x.shape==y.shape,ValueError,"Measured objects must have same shape to be plotted")
            plt.plot(x.value,y.value,**kwargs)
            plt.xlabel(x_key + " ({0})".format(x.unit.plot_symbol()))
            plt.ylabel(y_key + " ({0})".format(y.unit.plot_symbol()))