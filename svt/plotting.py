from svt.units import Unit,MiscUnit
from typing import Union
from svt.measured_data import Measured
from svt._check import Check
import matplotlib.pyplot as plt

class Figure:
    def __init__(
        self,
        x_unit:Union[Unit,MiscUnit],
        y_unit:Union[Unit,MiscUnit],
        z_unit = None,
        title = "") -> None:
        Check.object_class(x_unit,(Unit,MiscUnit),"x unit")
        Check.object_class(y_unit,(Unit,MiscUnit),"y unit")
        self.x_unit = x_unit
        self.y_unit = y_unit
        if z_unit is None:
            self.dimension = 2
        else:
            Check.object_class(z_unit,(Unit,MiscUnit),"z unit")
            self.z_unit = z_unit
            self.dimension = 3
    
    def _plotPoint(self,point,point_label,x_label = "x",y_label = "y",z_label = "z",**kwargs):
        pass
    
    def _plotCurve(self,curve,curve_label,x_label = "x",y_label = "y",z_label = "z",**kwargs):
        pass
    
    def _plotSurface(self,surface,surface_label,x_label = "x",y_label = "y",z_label = "z",**kwargs):
        pass

    def plotPoint(self,point,point_label,x_label = "x",y_label = "y",z_label = "z",**kwargs):
        pass
    
    def plotCurve(self,curve,curve_label=None,x_label = "x",y_label = "y",z_label = "z",**kwargs):
        Check.object_class(curve,Measured.Curve,"Curve")
        Check.condition(len(curve) == self.dimension,ValueError,"Can't plot a {0}D curve on a {1}D Figure".format(len(curve),self.dimension))
        Check.condition((curve.x.unit == self.x_unit)>0,ValueError,"Curve x component has different unit than Figure's x axis")
        Check.condition((curve.y.unit == self.y_unit)>0,ValueError,"Curve y component has different unit than Figure's y axis")
        curve.x.match_unit_to(self.x_unit)
        curve.y.match_unit_to(self.y_unit)
        self._plotCurve(curve,curve_label,x_label,y_label,z_label,**kwargs)
        
    def plotSurface(self,surface,surface_label,x_label = "x",y_label = "y",z_label = "z",**kwargs):
        pass

    @staticmethod
    def _find_axis_symbol(curve_axis):
        if curve_axis.SI:
            axis_symbol = curve_axis.unit.plot_symbol()
        else:
            axis_symbol = curve_axis.misc_unit.plot_symbol()
        return axis_symbol


class MatplotlibFigure(Figure):
    def __init__(self, x_unit: Union[Unit,MiscUnit], y_unit: Union[Unit,MiscUnit], z_unit=None, title="") -> None:
        super().__init__(x_unit, y_unit, z_unit, title)

    def _plotCurve(self,curve,curve_label,x_label = "x",y_label = "y",z_label = "z",**kwargs):
        if self.dimension == 2:
            plt.plot(curve.x.value,curve.y.value,label = curve_label)
            plt.xlabel(x_label + " ({0})".format(self._find_axis_symbol(curve.x)))
            plt.ylabel(y_label + " ({0})".format(self._find_axis_symbol(curve.y)))
            plt.legend()
            plt.grid()
        else:
            Check.condition((curve.z.unit == self.z_unit)>0,ValueError,"Curve z component has different unit than Figure's z axis")
            curve.z.match_unit_to(self.z_unit)
            plt.plot(curve.x.value,curve.y.value,curve.z.value,label = curve_label)
            plt.set_xlabel(x_label + " ({0})".format(self._find_axis_symbol(curve.x)))
            plt.set_ylabel(y_label + " ({0})".format(self._find_axis_symbol(curve.y)))
            plt.set_zlabel(z_label + " ({0})".format(self._find_axis_symbol(curve.z)))
            plt.legend()
            plt.grid()
    

# from svt.unit_collections import SI,MiscUnits
# import numpy as np
# from svt.measured_data import Measured
# a = Measured(1000,Unit(symbol = Unit.Symbol(["m"]),dimension = Unit.Dimension(["length"]),prefix= Unit.Prefix("m")))
# b = Measured(2,SI.m())
# c = Measured(np.linspace(0,300),MiscUnits.celsius())
# d = Measured(np.linspace(0,2),SI.Pa())
# my_col = Measured.Collection(a=a,b=b,c=c,d=d)
# my_point = Measured.Point(x=a,y=b)
# my_curve = Measured.Curve(x=c,y=d)
# my_curve2 = Measured.Curve(x=c,y=c)
# my_figure = MatplotlibFigure(x_unit=SI.K(),y_unit=SI.Pa("M"))
# import matplotlib
# matplotlib.use("TkAgg")
# my_figure.plotCurve(my_curve,label="My curve")
# # my_figure.plotCurve(my_curve2)
# plt.show()
