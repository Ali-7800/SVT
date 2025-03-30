from svt.units import Unit,MiscUnit
from svt._check import Check
import numpy as np
from typing import Union

class Measured:
    def __init__(self,value,unit:Union[Unit,MiscUnit]):
        if isinstance(unit,Unit):
            self.unit = unit
            Check.object_class_validity(value,self.valid_values(),"value")
            self.SI_value = value*self.unit.alternate_prefix.multiplier
            self.value = self.SI_value
            self.unit.alternate_prefix.multiplier = 1.0
            self.unit.alternate_prefix.power = self.unit.alternate_prefix.SI_power
            self.unit.prefix = self.unit.prefix_ratio*self.unit.alternate_prefix
            self.shape = self._shape()
            self.SI = True
        elif isinstance(unit,MiscUnit):
            self.unit = unit.SI_unit
            self.misc_unit = unit
            Check.object_class_validity(value,self.valid_values(),"value")
            self.SI_value = self.misc_unit.convert_to_SI(value)*self.unit.alternate_prefix.multiplier
            self.value = value
            self.unit.alternate_prefix.multiplier = 1.0
            self.unit.alternate_prefix.power = self.unit.alternate_prefix.SI_power
            self.unit.prefix = self.unit.prefix_ratio*self.unit.alternate_prefix
            self.SI = False
            self.shape = self._shape()
    
    def convert_to(self,prefix:str):
        if self.SI:
            new_unit = self.unit.update_prefix(prefix)
            return Measured(self.SI_value,new_unit)
        else:
            raise ValueError("Cannot convert non SI unit to different prefix")
    
    def __eq__(self, other):
        """Defines behavior for the equality operator (==)."""
        if isinstance(other, Measured):
            if (self.unit==other.unit)>0:
                m1,m2,new_unit = Unit.unify_prefixes(self.unit,other.unit)
                return m1*self.SI_value == m2*other.SI_value
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
                return m1*self.SI_value < m2*other.SI_value
            else:
                raise ValueError("Cannot compare Measured objects of different units")
        return NotImplemented

    def __gt__(self, other):
        """Defines behavior for the greater-than operator (>)."""
        if isinstance(other, Measured):
            if (self.unit==other.unit)>0:
                m1,m2,new_unit = Unit.unify_prefixes(self.unit,other.unit)
                return m1*self.SI_value > m2*other.SI_value
            else:
                raise ValueError("Cannot compare Measured objects of different units")
        return NotImplemented

    def __le__(self, other):
        """Defines behavior for the less-than-or-equal-to operator (<=)."""
        if isinstance(other, Measured):
            if (self.unit==other.unit)>0:
                m1,m2,new_unit = Unit.unify_prefixes(self.unit,other.unit)
                return m1*self.SI_value <= m2*other.SI_value
            else:
                raise ValueError("Cannot compare Measured objects of different units")
        return NotImplemented

    def __ge__(self, other):
        """Defines behavior for the greater-than-or-equal-to operator (>=)."""
        if isinstance(other, Measured):
            if (self.unit==other.unit)>0:
                m1,m2,new_unit = Unit.unify_prefixes(self.unit,other.unit)
                return m1*self.SI_value >= m2*other.SI_value
            else:
                raise ValueError("Cannot compare Measured objects of different units")
        return NotImplemented
        
    def __neg__(self):
        if self.SI:
            return Measured(-self.value,self.unit)
        else:
            return Measured(-self.value,self.misc_unit)

    def __add__(self,other):
        if isinstance(other, Measured):
            if self.SI or other.SI:
                if (other.unit == self.unit)>0:
                    m1,m2,new_unit = Unit.unify_prefixes(self.unit,other.unit)
                    return Measured(m1*self.SI_value + m2*other.SI_value,new_unit) #this will always return the SI unit
                else:
                    raise ValueError("Measured objects must have the same unit symbols and dimensions for addition")
            elif not self.SI and not other.SI:
                if (self.misc_unit == other.misc_unit):
                    return Measured(m1*self.value + m2*other.value,self.misc_unit)
                else:
                    raise ValueError("Measured objects must have the same Non SI units for addition")
        return NotImplemented
    
    def __sub__(self,other):
        if isinstance(other, Measured):
            if self.SI or other.SI:
                if (other.unit == self.unit)>0:
                    m1,m2,new_unit = Unit.unify_prefixes(self.unit,other.unit)
                    return Measured(m1*self.SI_value - m2*other.SI_value,new_unit) #this will always return the SI unit
                else:
                    raise ValueError("Measured objects must have the same unit symbols and dimensions for subtraction")
            elif not self.SI and not other.SI:
                if (self.misc_unit == other.misc_unit):
                    return Measured(self.value - other.value,self.misc_unit)
                else:
                    raise ValueError("Measured objects must have the same Non SI units for subtraction")
        return NotImplemented
    
    def __mul__(self, other):
        if isinstance(other, Measured):
            return Measured(self.SI_value * other.SI_value,self.unit*other.unit) #this will always return the SI unit
        elif isinstance(other, (int, float)):
            if self.SI:
                return Measured(self.SI_value * other,self.unit)
            else:
                return Measured(self.value * other,self.misc_unit)

        return NotImplemented

    def __rmul__(self, other):
        if isinstance(other, Measured):
            return Measured(self.SI_value * other.SI_value,self.unit*other.unit)
        elif isinstance(other, (int, float)):
            if self.SI:
                return Measured(self.SI_value * other,self.unit)
            else:
                return Measured(self.value * other,self.misc_unit)
        return NotImplemented
    
    def __truediv__(self, other):
        if isinstance(other, Measured):
            return Measured(self.SI_value / other.SI_value,self.unit/other.unit)
        elif isinstance(other, (int, float)):
            if self.SI:
                return Measured(self.SI_value / other,self.unit)
            else:
                return Measured(self.value / other,self.misc_unit)
        return NotImplemented
    
    def __rtruediv__(self,other):
        if isinstance(other, Measured):
            return Measured(other.SI_value / self.SI_value,other.unit/self.unit)
        elif isinstance(other, (int, float)):
            if self.SI:
                return Measured(other / self.SI_value,1/self.unit)
        return NotImplemented
    
    def __pow__(self,exponent):
        if isinstance(exponent,int):
            if self.SI:
                return Measured(self.SI_value**exponent,self.unit**exponent)
        return NotImplemented
    
    def __getitem__(self, key):
        if self.SI:
            return Measured(self.SI_value[key],self.unit)
        else:
            return Measured(self.value[key],self.misc_unit)

    def __setitem__(self, key, value):
        if self.SI:
            self.SI_value[key] = value
            self.value[key] = value
        else:
            self.SI_value[key] = self.misc_unit.convert_to_SI(value)
            self.value[key] = value

    def __str__(self):
        if self.SI:
            return str(self.SI_value)+self.unit.__str__()
        else:
            return str(self.value)+self.misc_unit.symbol.__str__()
    
    def _shape(self):
        if isinstance(self.SI_value,(int, float)):
            return 1
        elif isinstance(self.SI_value,np.ndarray):
            return self.SI_value.shape
    
    def transpose(self):
        if self.shape == 1:
            return self.copy()
        else:
            if self.SI:
                return Measured(self.SI_value.T,self.unit)
            else:
                return Measured(self.value.T,self.misc_unit)
    
    def scale(self,factor):
        if isinstance(factor,(int,float)):
            self.SI_value *= factor
            self.value *= factor
        elif isinstance(factor,Measured):
            self.SI_value *= factor.SI_value
            self.value *= factor
            self.unit *= factor.unit
        else:
            return NotImplemented
    
    def copy(self):
        if self.SI:
            return Measured(self.SI_value,self.unit)
        else:
            return Measured(self.value,self.misc_unit)
    
    def valid_values(self):
        return [int,float,np.ndarray]
    
    def match_unit_to(self,unit_to_match:Union[Unit.Collection,Unit,MiscUnit],name = None):
        if isinstance(unit_to_match,Unit.Collection):
            if name is None:
                if self.unit.dimension.symbol in unit_to_match:
                    if isinstance(unit_to_match[self.unit.dimension.symbol],Unit):
                        temp = self + Measured(0,unit_to_match[self.unit.dimension.symbol])
                        temp = temp.convert_to(unit_to_match[self.unit.dimension.symbol].alternate_prefix.symbol)
                        self.unit = temp.unit
                        self.SI_value = temp.SI_value
                        self.value = temp.value
                        self.shape = temp.shape
                        self.SI = True #since addition with SI always returns an SI value
                    else:
                        temp = Measured(unit_to_match[self.unit.dimension.symbol].convert_from_SI(self.SI_value),
                                        unit_to_match[self.unit.dimension.symbol]) #new Measured with MiscUnit
                        self.unit = temp.unit
                        self.SI_value = temp.SI_value
                        self.value = temp.value
                        self.shape = temp.shape
                        self.misc_unit = unit_to_match[self.unit.dimension.symbol]
                        self.SI = False
            else:
                Check.condition(name in unit_to_match,ValueError,"Given name is not in Unit.Collection")
                Check.condition((unit_to_match[name]==self.unit)>0,ValueError,"Given name does not have units that match")
                if isinstance(unit_to_match[name],Unit):
                    temp = self + Measured(0,unit_to_match[name])
                    temp = temp.convert_to(unit_to_match[name].alternate_prefix.symbol)
                    self.unit = temp.unit
                    self.SI_value = temp.SI_value
                    self.value = temp.value
                    self.shape = temp.shape
                    self.SI = True #since addition with SI always returns an SI value
                else:
                    temp = Measured(unit_to_match[name].convert_from_SI(self.SI_value),
                                    unit_to_match[name]) #new Measured with unit to match
                    self.unit = temp.unit
                    self.SI_value = temp.SI_value
                    self.value = temp.value
                    self.shape = temp.shape
                    self.misc_unit = unit_to_match[name]
                    self.SI = False
        elif isinstance(unit_to_match,Unit):
            Check.condition((unit_to_match==self.unit)>0,ValueError,"Given name does not have units that match")
            temp = self + Measured(0,unit_to_match) #this will always return the SI value
            temp = temp.convert_to(unit_to_match.alternate_prefix.symbol)
            self.unit = temp.unit
            self.SI_value = temp.SI_value
            self.value = temp.value
            self.shape = temp.shape
            self.SI = True
        elif isinstance(unit_to_match,MiscUnit):
            Check.condition((unit_to_match.SI_unit==self.unit)>0,ValueError,"Given name does not have units that match")
            temp = Measured(unit_to_match.convert_from_SI(self.SI_value),unit_to_match) #new Measured with MiscUnit
            self.unit = self.unit
            self.SI_value = self.SI_value
            self.value = temp.value
            self.shape = self.shape
            self.misc_unit = unit_to_match
            self.SI = False
        else:
            return NotImplemented
        
    def append(self,values):
        if isinstance(values,(float,int)):
            values = np.array([values])
        if self.shape == 1:
            self.SI_value = np.array([self.SI_value])
        if self.SI:
            self.SI_value = np.append(self.SI_value,values)
            self.value = self.SI_value
        else:
            self.SI_value = np.append(self.SI_value,self.misc_unit.convert_to_SI(np.array(values)))
            self.value = np.append(self.value,np.array(values))
        self.shape = self._shape()
    
    @staticmethod
    def empty(shape,unit):
        return Measured(np.empty(shape),unit)
    
    @staticmethod
    def array(elements:list,unit):
        return Measured(np.array(elements),unit)
    
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