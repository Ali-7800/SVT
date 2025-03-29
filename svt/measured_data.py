from svt.units import Unit
from svt._check import Check
import numpy as np
import matplotlib.pyplot as plt
from typing import Union

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
    
    def __eq__(self, other):
        """Defines behavior for the equality operator (==)."""
        if isinstance(other, Measured):
            if (self.unit==other.unit)>0:
                m1,m2,new_unit = Unit.unify_prefixes(self.unit,other.unit)
                return m1*self.value == m2*other.value
            else:
                raise ValueError("Cannot compare Measured objects of different units")
        return NotImplemented

    def __ne__(self, other):
        """Defines behavior for the inequality operator (!=)."""
        return not self.__eq__(other)

    def __lt__(self, other):
        """Defines behavior for the less-than operator (<)."""
        if isinstance(other, Measured):
            if (self.unit==other.unit)>0:
                m1,m2,new_unit = Unit.unify_prefixes(self.unit,other.unit)
                return m1*self.value < m2*other.value
            else:
                raise ValueError("Cannot compare Measured objects of different units")
        return NotImplemented

    def __gt__(self, other):
        """Defines behavior for the greater-than operator (>)."""
        if isinstance(other, Measured):
            if (self.unit==other.unit)>0:
                m1,m2,new_unit = Unit.unify_prefixes(self.unit,other.unit)
                return m1*self.value > m2*other.value
            else:
                raise ValueError("Cannot compare Measured objects of different units")
        return NotImplemented

    def __le__(self, other):
        """Defines behavior for the less-than-or-equal-to operator (<=)."""
        if isinstance(other, Measured):
            if (self.unit==other.unit)>0:
                m1,m2,new_unit = Unit.unify_prefixes(self.unit,other.unit)
                return m1*self.value <= m2*other.value
            else:
                raise ValueError("Cannot compare Measured objects of different units")
        return NotImplemented

    def __ge__(self, other):
        """Defines behavior for the greater-than-or-equal-to operator (>=)."""
        if isinstance(other, Measured):
            if (self.unit==other.unit)>0:
                m1,m2,new_unit = Unit.unify_prefixes(self.unit,other.unit)
                return m1*self.value >= m2*other.value
            else:
                raise ValueError("Cannot compare Measured objects of different units")
        return NotImplemented
        
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
    
    def __getitem__(self, key):
        return Measured(self.value[key],self.unit)
    
    def __setitem__(self, key, value):
        self.value[key] = value

    def __str__(self):
        return str(self.value)+self.unit.__str__()
    
    def _shape(self):
        if isinstance(self.value,(int, float)):
            return 1
        elif isinstance(self.value,np.ndarray):
            return self.value.shape
    
    def transpose(self):
        if self.shape == 1:
            return self.copy()
        else:
            return Measured(self.value.T,self.unit)
    
    def scale(self,factor):
        if isinstance(factor,(int,float)):
            self.value *= factor
        elif isinstance(factor,Measured):
            self.value *= factor.value
            self.unit *= factor.unit
        else:
            return NotImplemented
    
    def copy(self):
        return Measured(self.value,self.unit)
    
    def valid_values(self):
        return [int,float,np.ndarray]
    
    def match_unit_to(self,unit_to_match:Union[Unit.Collection,Unit],name = None):
        if isinstance(unit_to_match,Unit.Collection):
            if name is None:
                if self.unit.dimension.symbol in unit_to_match:
                    temp = self + Measured(0,unit_to_match[self.unit.dimension.symbol])
                    temp = temp.convert_to(unit_to_match[self.unit.dimension.symbol].alternate_prefix.symbol)
                    self.unit = temp.unit
                    self.value = temp.value
                    self.shape = temp.shape
            else:
                Check.condition(name in unit_to_match,ValueError,"Given name is not in Unit.Collection")
                Check.condition((unit_to_match[name]==self.unit)>0,ValueError,"Given name does not have units that match")
                temp = self + Measured(0,unit_to_match[name])
                temp = temp.convert_to(unit_to_match[name].alternate_prefix.symbol)
                self.unit = temp.unit
                self.value = temp.value
                self.shape = temp.shape
        elif isinstance(unit_to_match,Unit):
            Check.condition((unit_to_match==self.unit)>0,ValueError,"Given name does not have units that match")
            temp = self + Measured(0,unit_to_match)
            temp = temp.convert_to(unit_to_match.alternate_prefix.symbol)
            self.unit = temp.unit
            self.value = temp.value
            self.shape = temp.shape
        else:
            return NotImplemented
        
    def append(self,values):
        if self.shape == 1:
            self.value = np.array([self.value])
            self.value = np.append(self.value,values)
        else:
            self.value = np.append(self.value,values)
    
    class Collection:
        def __init__(
            self,
            **kwargs) -> None:
            self.shape = None
            self.keys = []
            self.append(**kwargs)
            
        def append(self,**kwargs):
            for key in kwargs.keys():
                Check.object_class(kwargs[key],Measured,"keyword argument/component")
                self._shape_check(kwargs[key])
                setattr(self, key, kwargs[key])
            self.keys+=kwargs.keys()
        
        def __len__(self):
            return len(self.keys)
        
        def _shape_check(self,data):
            #any Measured object can be appended to a Collection
            pass

    class Point(Collection):
        def __init__(
            self,
            x,
            y,
            z  = None) -> None:
            if z is None:
                Measured.Collection.__init__(
                    self,
                    x = x,
                    y = y
                    )
            else:
                Measured.Collection.__init__(
                    self,
                    x = x,
                    y = y,
                    z = z,
                    )
        
        def _shape_check(self,data):
            Check.condition(data.shape==1,ValueError,"All Point components must be of shape 1")

    class Curve(Collection):
        def __init__(
            self,
            x,
            y,
            z  = None) -> None:
            if z is None:
                Measured.Collection.__init__(
                    self,
                    x = x,
                    y = y
                    )
            else:
                Measured.Collection.__init__(
                    self,
                    x = x,
                    y = y,
                    z = z,
                    )
        
        def _shape_check(self,data):
            if self.shape == None:
                Check.condition(data.shape!=1,ValueError,"Must have more than one point for Curve")
                Check.condition(len(data.shape)==1,ValueError,"Must be a 1D arrat for a Curve component")
                self.shape == data.shape
            else:
                Check.condition(self.shape==data.shape,ValueError,"All Curve components must have the same shape")

    class Surface(Collection):
        def __init__(
            self,
            x,
            y,
            z  = None) -> None:
            if z is None:
                Measured.Collection.__init__(
                    self,
                    x = x,
                    y = y
                    )
            else:
                Measured.Collection.__init__(
                    self,
                    x = x,
                    y = y,
                    z = z,
                    )
        
        def _shape_check(self,data):
            if self.shape == None:
                Check.condition(data.shape!=1,ValueError,"Must have more than one point for Surface")
                self.shape == data.shape
            else:
                Check.condition(self.shape==data.shape,ValueError,"All Surface components must have the same shape")