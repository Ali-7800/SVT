import numpy as np
from svt.units import Unit
from svt._check import Check
from typing import Union
import matplotlib.pyplot as plt

class Measured:
    def __init__(self) -> None:
        pass
    class Quantity:
        def __init__(
            self,
            value:Union[float,int],
            unit:Unit,
            ) -> None:
            Check.object_class(unit,Unit,"unit")
            self.unit = unit
            self.value = value*self.unit.alternate_prefix.multiplier
            self.unit.alternate_prefix.multiplier = 1.0
            self.unit.alternate_prefix.power = self.unit.alternate_prefix.SI_power
            self.prefix_ratio = self.unit.prefix/self.unit.alternate_prefix
        
        def convert_to(self,prefix:str):
            new_unit = self.unit.update_prefix(prefix)
            return Measured.Quantity(self.value,new_unit)
        
        def __neg__(self):
            return Measured.Quantity(-self.value,self.unit)

        def __add__(self,other):
            if isinstance(other, Measured.Quantity):
                if (other.unit == self.unit)>0:
                    m1,m2,new_unit = Unit.unify_prefixes(self.unit,other.unit)
                    return Measured.Quantity(m1*self.value + m2*other.value,new_unit)
                else:
                    raise ValueError("(Measured.Quantity)s must have the same unit symbols and dimensions for addition")
            return NotImplemented
        
        def __sub__(self,other):
            if isinstance(other, Measured.Quantity):
                if (other.unit == self.unit)>0:
                    m1,m2,new_unit = Unit.unify_prefixes(self.unit,other.unit)
                    return Measured.Quantity(m1*self.value - m2*other.value,new_unit)
                else:
                    raise ValueError("(Measured.Quantity)s must have the same units for subtraction")
            return NotImplemented
        
        def __mul__(self, other):
            if isinstance(other, Measured.Quantity):
                return Measured.Quantity(self.value * other.value,self.unit*other.unit)
            elif isinstance(other, (int, float)):
                return Measured.Quantity(self.value * other,self.unit)
            return NotImplemented

        def __rmul__(self, other):
            if isinstance(other, Measured.Quantity):
                return Measured.Quantity(self.value * other.value,self.unit*other.unit)
            elif isinstance(other, (int, float)):
                return Measured.Quantity(self.value * other,self.unit)
            return NotImplemented
        
        def __truediv__(self, other):
            if isinstance(other, Measured.Quantity):
                return Measured.Quantity(self.value / other.value,self.unit/other.unit)
            elif isinstance(other,Measured.Array):
                return Measured.Array(self.value/other.values,self.unit/other.unit)
            elif isinstance(other, (int, float)):
                return Measured.Quantity(self.value / other,self.unit)
            return NotImplemented
        
        def __rtruediv__(self,other):
            if isinstance(other, Measured.Quantity):
                return Measured.Quantity(other.value / self.value,other.unit/self.unit)
            elif isinstance(other,Measured.Array):
                return Measured.Array(other.values/self.value,other.unit/self.unit)
            elif isinstance(other, (int, float)):
                return Measured.Quantity(other / self.value,1/self.unit)
            return NotImplemented
        
        def __pow__(self,exponent):
            if isinstance(exponent,int):
                return Measured.Quantity(self.value**exponent,self.unit**exponent)
            return NotImplemented


        def __str__(self):
            return str(self.value)+self.unit.__str__()
        
    class Array:
        def __init__(
            self,
            values: np.ndarray,
            unit:Unit,
            ) -> None:
            Check.object_class(values,np.ndarray,"value")
            Check.object_class(unit,Unit,"unit")
            self.unit = unit
            self.values = values*self.unit.alternate_prefix.multiplier
            self.unit.alternate_prefix.multiplier = 1.0
            self.unit.alternate_prefix.power = self.unit.alternate_prefix.SI_power
            self.prefix_ratio = self.unit.prefix/self.unit.alternate_prefix
        
        def convert_to(self,prefix:str):
            new_unit = self.unit.update_prefix(prefix)
            return Measured.Array(self.values,new_unit)
        
        def __neg__(self):
            return Measured.Array(-self.value,self.unit)
        
        def __add__(self,other):
            if isinstance(other, Measured.Array):
                if (other.unit == self.unit)>0:
                    m1,m2,new_unit = Unit.unify_prefixes(self.unit,other.unit)
                    return Measured.Array(m1*self.values + m2*other.values,new_unit)
                else:
                    raise ValueError("(Measured.Array)s must have the same units for addition")
            elif isinstance(other, Measured.Quantity):
                if (other.unit == self.unit)>0:
                    m1,m2,new_unit = Unit.unify_prefixes(self.unit,other.unit)
                    return Measured.Array(m1*self.values + m2*other.value,new_unit)
                else:
                    raise ValueError("Measured objects must have the same units for addition")
            return NotImplemented
        
        def __sub__(self,other):
            if isinstance(other, Measured.Array):
                if (other.unit == self.unit)>0:
                    m1,m2,new_unit = Unit.unify_prefixes(self.unit,other.unit)
                    return Measured.Array(m1*self.values - m2*other.values,new_unit)
                else:
                    raise ValueError("(Measured.Array)s must have the same units for subtraction")
            elif isinstance(other, Measured.Quantity):
                if (other.unit == self.unit)>0:
                    m1,m2,new_unit = Unit.unify_prefixes(self.unit,other.unit)
                    return Measured.Array(m1*self.values - m2*other.value,new_unit)
                else:
                    raise ValueError("Measured objects must have the same units for addition")
            return NotImplemented
        
        def __mul__(self, other):
            if isinstance(other, Measured.Array):
                return Measured.Array(self.values * other.values,self.unit*other.unit)
            elif isinstance(other, Measured.Quantity):
                return Measured.Array(self.values * other.value,self.unit*other.unit)
            elif isinstance(other, (int, float)):
                return Measured.Array(self.values * other,self.unit)
            return NotImplemented

        def __rmul__(self, other):
            if isinstance(other, Measured.Array):
                return Measured.Array(self.values * other.values,self.unit*other.unit)
            elif isinstance(other, Measured.Quantity):
                return Measured.Array(self.values * other.value,self.unit*other.unit)
            elif isinstance(other, (int, float)):
                return Measured.Array(self.values * other,self.unit)
            return NotImplemented
        
        def __truediv__(self, other):
            if isinstance(other, Measured.Array):
                return Measured.Array(self.values / other.values,self.unit/other.unit)
            elif isinstance(other, Measured.Quantity):
                return Measured.Array(self.values / other.value,self.unit/other.unit)
            elif isinstance(other, (int, float)):
                return Measured.Array(self.values / other,self.unit)
            return NotImplemented
        
        def __rtruediv__(self,other):
            if isinstance(other, Measured.Quantity):
                return Measured.Array(other.value / self.values,other.unit/self.unit)
            elif isinstance(other,Measured.Array):
                return Measured.Array(other.values/self.values,other.unit/self.unit)
            elif isinstance(other, (int, float)):
                return Measured.Array(other / self.values,1/self.unit)
            return NotImplemented
        
        def __pow__(self,exponent):
            if isinstance(exponent,int):
                return Measured.Array(self.values**exponent,self.unit**exponent)
            return NotImplemented
        
        def __str__(self):
            return str(self.values)+self.unit.__str__()
        
        def copy(self):
            return Measured.Array(self.values,self.unit)

    class DataCollection:
        def __init__(
            self,
            **kwargs) -> None:
            self.keys = []
            for key in kwargs.keys():
                Check.object_class(kwargs[key],Measured.Array,"","Every keyword argument in Measured.DataCollection must be an instance of Measured.Array")
                setattr(self, key, kwargs[key])
            self.keys+=kwargs.keys()
            
        def append(self,key,data):
            Check.object_class(data,Measured.Array,"","Only (Measured.Array)s can be appended to a Measured.DataCollection")
            Check.condition(key not in self.keys,KeyError,"Key already used for other Measured.Data, please use a different key")
            setattr(self, key, data)
            self.keys.append(key)
        
        def plot2D(self,x_key:str,y_key:str,**kwargs):
            Check.validity(x_key,"key1",self.keys)
            Check.validity(y_key,"key2",self.keys)
            x = getattr(self,x_key)
            y = getattr(self,y_key)
            plt.plot(x.values,y.values,**kwargs)
            plt.xlabel(x_key + " ({0})".format(x.unit.plot_symbol()))
            plt.ylabel(y_key + " ({0})".format(y.unit.plot_symbol()))
    
    
# from svt import SI
# a = Measured.Quantity(3,SI.meter().convert_prefix_to("m"))
# b = Measured.Quantity(4,SI.newton())
# c = Measured.Array(np.linspace(1,2),SI.celsius())
# d = Measured.Array(np.linspace(1,2),SI.newton())/a**2
# print(type(d))
# dc = Measured.DataCollection(x=c,y=d)
# import matplotlib
# matplotlib.use('TkAgg')
# dc.plot2D("x","y")
# plt.show()