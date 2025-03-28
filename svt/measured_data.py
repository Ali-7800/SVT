from svt.units import Unit
from svt._check import Check
import numpy as np
import matplotlib.pyplot as plt


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


    class Collection:
        def __init__(
            self,
            **kwargs) -> None:
            self.shape = None
            self.keys = []
            for key in kwargs.keys():
                Check.object_class(kwargs[key],Measured,"keyword argument/component")
                self._shape_check(kwargs[key])
                setattr(self, key, kwargs[key])
            self.keys+=kwargs.keys()
            
        def append(self,key,data):
            Check.object_class(data,Measured,"","Only Measured objects can be appended to a Collection object")
            Check.condition(key not in self.keys,KeyError,"Key already used for other Measured object in Collection, please use a different key")
            self._shape_check(data)
            setattr(self, key, data)
            self.keys.append(key)
        
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

    class Figure:
        def __init__(
            self,
            x_unit:Unit,
            y_unit:Unit,
            z_unit = None,
            title = "") -> None:
            Check.object_class(x_unit,Unit,"x unit")
            Check.object_class(y_unit,Unit,"y unit")
            self.x_unit = x_unit
            self.y_unit = y_unit
            if z_unit is None:
                self.dimension = 2
            else:
                Check.object_class(z_unit,Unit,"z unit")
                self.z_unit = z_unit
                self.dimension = 3
            # if self.dimension == 2:
            #     plt.figure()
            # else:
            #     plt.figure().add_subplot(projection='3d')
            #     pass

        def plotPoint(self,point):
            pass
        
        def plotCurve(self,curve,x_label = "x",y_label = "y",z_label = "z",**kwargs):
            Check.object_class(curve,Measured.Curve,"Curve")
            Check.condition(len(curve) == self.dimension,ValueError,"Can't plot a {0}D curve on a {1}D Figure".format(len(curve),self.dimension))
            Check.condition((curve.x.unit == self.x_unit)>0,ValueError,"Curve x component has different unit than Figure's x axis")
            Check.condition((curve.y.unit == self.y_unit)>0,ValueError,"Curve y component has different unit than Figure's y axis")
            curve.x += Measured(0,self.x_unit)
            curve.y += Measured(0,self.y_unit)
            if self.dimension == 2:
                plt.plot(curve.x.value,curve.y.value,**kwargs)
                plt.xlabel(x_label + " ({0})".format(curve.x.unit.plot_symbol()))
                plt.ylabel(y_label + " ({0})".format(curve.y.unit.plot_symbol()))
            else:
                Check.condition((curve.z.unit == self.z_unit)>0,ValueError,"Curve z component has different unit than Figure's z axis")
                curve.z += Measured(0,self.z_unit)
                plt.plot(curve.x.value,curve.y.value,curve.z.value,**kwargs)
                plt.set_xlabel(x_label + " ({0})".format(curve.x.unit.plot_symbol()))
                plt.set_ylabel(y_label + " ({0})".format(curve.y.unit.plot_symbol()))
                plt.set_zlabel(z_label + " ({0})".format(curve.z.unit.plot_symbol()))
        
        def plotSurface(self,surface):
            pass

# from svt import SI
# a = Measured(1000,Unit(symbol = Unit.Symbol(["m"]),dimension = Unit.Dimension(["length"]),prefix= Unit.Prefix("m")))
# b = Measured(2,SI.meter())
# c = Measured(np.linspace(0,1),SI.meter())
# d = Measured(np.linspace(0,2),SI.meter())
# print(a)
# d = c/a**2
# print(c,d)
# my_col = Measured.Collection(a=a,b=b,c=c,d=d)
# my_point = Measured.Point(x=a,y=b)
# my_curve = Measured.Curve(x=c,y=d)
# my_curve2 = Measured.Curve(x=c,y=c)
# my_figure = Measured.Figure(x_unit=SI.newton(),y_unit=SI.pascal())
# import matplotlib
# matplotlib.use("TkAgg")
# my_figure.plotCurve(my_curve)
# # my_figure.plotCurve(my_curve2)

# plt.show()
