import numpy as np
from svt.units import Unit,DerivedUnit
from svt._check import Check
from typing import Union
import matplotlib.pyplot as plt

class Measured:
    def __init__(self) -> None:
        pass
    class Variable:
        def __init__(
            self,
            value:Union[float,int],
            unit:Unit,
            ) -> None:
            self.value = value
            Check.object_class(unit,Unit,"unit")
            self.unit = unit
        
        def convert_to(self,prefix:str):
            Check.validity(prefix,"SI prefix",Unit.SI_prefixes())
            self.value /= self.unit.multiplier
            self.unit.convert_to(prefix)
            self.value *= self.unit.multiplier
        
        def __add__(self,other):
            if isinstance(other, Measured.Variable):
                if other.unit == self.unit:
                    return Measured.Variable(self.value + other.value,self.unit)
                # elif other.unit.dimension() == other.unit.dimension():
                #     min_SI_power = min(self.unit.SI_power,other.unit.SI_power)
                #     minimum_prefix = Unit.SI_prefixes()[Unit._find_SI_power_index(min_SI_power)]
                #     d1 = self.copy()
                #     d1.convert_to(minimum_prefix)
                #     d2 = other.copy()
                #     d2.convert_to(minimum_prefix)
                #     return MeasuredArray(d1.values - d2.values,d1.unit)
                else:
                    raise ValueError("(Measured.Variable)s must have the same units for addition")
            return NotImplemented
        
        def __sub__(self,other):
            if isinstance(other, Measured.Variable):
                if other.unit == self.unit:
                    return Measured.Variable(self.value - other.value,self.unit)
                else:
                    raise ValueError("(Measured.Variable)s must have the same units for subtraction")
            return NotImplemented
        
        def __mul__(self, other):
            if isinstance(other, Measured.Variable):
                return Measured.Variable(self.value * other.value,self.unit*other.unit)
            elif isinstance(other, (int, float)):
                return Measured.Variable(self.value * other,self.unit)
            return NotImplemented

        def __rmul__(self, other):
            if isinstance(other, Measured.Variable):
                return Measured.Variable(self.value * other.value,self.unit*other.unit)
            elif isinstance(other, (int, float)):
                return Measured.Variable(self.value * other,self.unit)
            return NotImplemented
        
        def __truediv__(self, other):
            if isinstance(other, Measured.Variable):
                return Measured.Variable(self.value / other.value,self.unit/other.unit)
            elif isinstance(other,Measured.Array):
                return Measured.Array(self.value/other.values,self.unit/other.unit)
            elif isinstance(other, (int, float)):
                return Measured.Variable(self.value / other,self.unit)
            else:
                return NotImplemented
        
        def __rtruediv__(self,other):
            if isinstance(other, Measured.Variable):
                return Measured.Variable(other.value / self.value,other.unit/self.unit)
            elif isinstance(other,Measured.Array):
                return Measured.Array(other.values/self.value,other.unit/self.unit)
            elif isinstance(other, (int, float)):
                return Measured.Variable(other / self.value,1/self.unit)
            else:
                return NotImplemented
        
        def __str__(self):
            return str(self.value)+self.unit.full_symbol()
        
    class Array:
        def __init__(
            self,
            values: np.ndarray,
            unit:Unit,
            ) -> None:
            Check.object_class(values,np.ndarray,"value")
            self.values = values
            Check.object_class(unit,Unit,"unit")
            self.unit = unit
        
        def __add__(self,other):
            if isinstance(other, Measured.Array):
                if other.unit == self.unit:
                    return Measured.Array(self.values + other.values,self.unit)
                else:
                    raise ValueError("(Measured.Array)s must have the same units for addition")
            elif isinstance(other, Measured.Variable):
                if other.unit == self.unit:
                    return Measured.Array(self.values + other.value,self.unit)
                else:
                    raise ValueError("Measured objects must have the same units for addition")
            return NotImplemented
        
        def __sub__(self,other):
            if isinstance(other, Measured.Array):
                if other.unit == self.unit:
                    return Measured.Array(self.values - other.values,self.unit)
                else:
                    raise ValueError("(Measured.Array)s must have the same units for subtraction")
            elif isinstance(other, Measured.Variable):
                if other.unit == self.unit:
                    return Measured.Array(self.values - other.value,self.unit)
                else:
                    raise ValueError("Measured objects must have the same units for addition")
            return NotImplemented
        
        def __mul__(self, other):
            if isinstance(other, Measured.Array):
                return Measured.Array(self.values * other.values,self.unit*other.unit)
            elif isinstance(other, Measured.Variable):
                return Measured.Array(self.values * other.value,self.unit*other.unit)
            elif isinstance(other, (int, float)):
                return Measured.Variable(self.values * other,self.unit)
            return NotImplemented

        def __rmul__(self, other):
            if isinstance(other, Measured.Array):
                return Measured.Array(self.values * other.values,self.unit*other.unit)
            elif isinstance(other, Measured.Variable):
                return Measured.Array(self.values * other.value,self.unit*other.unit)
            elif isinstance(other, (int, float)):
                return Measured.Variable(self.values * other,self.unit)
            return NotImplemented
        
        def __truediv__(self, other):
            if isinstance(other, Measured.Array):
                return Measured.Array(self.values / other.values,self.unit/other.unit)
            elif isinstance(other, Measured.Variable):
                return Measured.Variable(self.values / other.value,self.unit/other.unit)
            elif isinstance(other, (int, float)):
                return Measured.Variable(self.values / other,self.unit)
            return NotImplemented
        
        def __rtruediv__(self,other):
            if isinstance(other, Measured.Variable):
                return Measured.Variable(other.value / self.values,other.unit/self.unit)
            elif isinstance(other,Measured.Array):
                return Measured.Array(other.values/self.values,other.unit/self.unit)
            elif isinstance(other, (int, float)):
                return Measured.Variable(other / self.values,1/self.unit)
            else:
                return NotImplemented
        
        def __str__(self):
            return str(self.values)+self.unit.full_symbol()

        def convert_to(self,prefix:str):
            Check.validity(prefix,"SI prefix",Unit.SI_prefixes())
            self.values /= self.unit.multiplier
            self.unit.convert_to(prefix)
            self.values *= self.unit.multiplier
        
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
            plt.xlabel(x_key + " ({0})".format(x.unit.full_symbol()))
            plt.ylabel(y_key + " ({0})".format(y.unit.full_symbol()))
