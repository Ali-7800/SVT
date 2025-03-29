from svt.units import Unit
from svt.measured_data import Measured
from svt._check import Check
import matplotlib.pyplot as plt

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
    
    def _plotCurve(self,point,x_label = "x",y_label = "y",z_label = "z",**kwargs):
        pass
    
    def _plotCurve(self,curve):
        pass
    
    def _plotSurface(self,curve):
        pass

    def plotPoint(self,point):
        pass
    
    def plotCurve(self,curve,x_label = "x",y_label = "y",z_label = "z",**kwargs):
        Check.object_class(curve,Measured.Curve,"Curve")
        Check.condition(len(curve) == self.dimension,ValueError,"Can't plot a {0}D curve on a {1}D Figure".format(len(curve),self.dimension))
        Check.condition((curve.x.unit == self.x_unit)>0,ValueError,"Curve x component has different unit than Figure's x axis")
        Check.condition((curve.y.unit == self.y_unit)>0,ValueError,"Curve y component has different unit than Figure's y axis")
        curve.x.match_unit_to(self.x_unit)
        curve.y.match_unit_to(self.y_unit)
        self._plotCurve(curve)
        
    def plotSurface(self,surface):
        pass

class MatplotlibFigure(Figure):
    def __init__(self, x_unit: Unit, y_unit: Unit, z_unit=None, title="") -> None:
        super().__init__(x_unit, y_unit, z_unit, title)

    def _plotCurve(self,curve,x_label = "x",y_label = "y",z_label = "z",**kwargs):
        if self.dimension == 2:
            plt.plot(curve.x.value,curve.y.value,**kwargs)
            plt.xlabel(x_label + " ({0})".format(curve.x.unit.plot_symbol()))
            plt.ylabel(y_label + " ({0})".format(curve.y.unit.plot_symbol()))
        else:
            Check.condition((curve.z.unit == self.z_unit)>0,ValueError,"Curve z component has different unit than Figure's z axis")
            curve.z.match_unit_to(self.z_unit)
            plt.plot(curve.x.value,curve.y.value,curve.z.value,**kwargs)
            plt.set_xlabel(x_label + " ({0})".format(curve.x.unit.plot_symbol()))
            plt.set_ylabel(y_label + " ({0})".format(curve.y.unit.plot_symbol()))
            plt.set_zlabel(z_label + " ({0})".format(curve.z.unit.plot_symbol()))
    

# from svt import SI
# import numpy as np
# a = Measured(1000,Unit(symbol = Unit.Symbol(["m"]),dimension = Unit.Dimension(["length"]),prefix= Unit.Prefix("m")))
# b = Measured(2,SI.meter())
# c = Measured(np.linspace(0,1),SI.newton())
# d = Measured(np.linspace(0,2),SI.pascal())
# my_col = Measured.Collection(a=a,b=b,c=c,d=d)
# my_point = Measured.Point(x=a,y=b)
# my_curve = Measured.Curve(x=c,y=d)
# my_curve2 = Measured.Curve(x=c,y=c)
# my_figure = MatplotlibFigure(x_unit=SI.newton("m"),y_unit=SI.pascal("M"))
# import matplotlib
# matplotlib.use("TkAgg")
# my_figure.plotCurve(my_curve)
# # my_figure.plotCurve(my_curve2)
# plt.show()
