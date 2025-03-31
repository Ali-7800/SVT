from svt.units import Unit,MiscUnit
from typing import Union
from svt.measured_data import Measured
from svt._check import Check
import matplotlib.pyplot as plt
import numpy as np


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
        self._check_and_match_units(curve.x,self.x_unit)
        self._check_and_match_units(curve.y,self.y_unit)
        if self.dimension>2:
            self._check_and_match_units(curve.z,self.z_unit)
        self._plotCurve(curve,curve_label,x_label,y_label,z_label,**kwargs)
        
    def plotSurface(self,surface,surface_label,x_label = "x",y_label = "y",z_label = "z",**kwargs):
        pass
    
    @staticmethod
    def _check_and_match_units(curve_axis,figure_axis_unit):
        Check.condition((curve_axis.unit == figure_axis_unit)>0,ValueError,"{0} component has different unit than Figure's {1}".format(curve_axis,figure_axis_unit))
        curve_axis.match_unit_to(figure_axis_unit)

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

        if self.dimension == 2:
            def plotCurvesAsShadedRegion(self, curve_list, curves_label=None, x_label="x", y_label="y", color="b",alpha = 0.2):
                Check.list_class(curve_list,Measured.Curve,"Curve","Curve list")
                minimum_curve = curve_list[0]
                maximum_curve = curve_list[0]
                for curve in curve_list:
                    Check.condition(len(curve) == 2,ValueError,"All curves must be 2D for plotCurvesAsShadedRegion")
                    self._check_and_match_units(curve.x,self.x_unit)
                    self._check_and_match_units(curve.y,self.y_unit)
                    minimum_curve = Measured.Curve.min(minimum_curve,curve)
                    maximum_curve = Measured.Curve.max(maximum_curve,curve)
                plt.plot(minimum_curve.x.value, minimum_curve.y.value, color, label=curves_label)
                plt.plot(maximum_curve.x.value, maximum_curve.y.value, color)
                plt.fill(
                    np.append(minimum_curve.x.value, maximum_curve.x.value[::-1]), np.append(minimum_curve.y.value, maximum_curve.y.value[::-1]), color=color, alpha=alpha
                )
                plt.xlabel(x_label + " ({0})".format(self._find_axis_symbol(curve.x)))
                plt.ylabel(y_label + " ({0})".format(self._find_axis_symbol(curve.y)))
                plt.legend()
                plt.grid()
        else:
            def plotCurvesAsShadedRegion(self, curve_list, curves_label=None, x_label="x", y_label="y", **kwargs):
                raise RuntimeError("This method can only be used for 2D Figures")
        
        self.plotCurvesAsShadedRegion = plotCurvesAsShadedRegion.__get__(self, MatplotlibFigure)

    def _plotCurve(self,curve,curve_label,x_label = "x",y_label = "y",z_label = "z",**kwargs):
        if self.dimension == 2:
            plt.plot(curve.x.value,curve.y.value,label = curve_label,**kwargs)
            plt.xlabel(x_label + " ({0})".format(self._find_axis_symbol(curve.x)))
            plt.ylabel(y_label + " ({0})".format(self._find_axis_symbol(curve.y)))
            plt.legend()
            plt.grid()
        else:
            plt.plot(curve.x.value,curve.y.value,curve.z.value,label = curve_label,**kwargs)
            plt.set_xlabel(x_label + " ({0})".format(self._find_axis_symbol(curve.x)))
            plt.set_ylabel(y_label + " ({0})".format(self._find_axis_symbol(curve.y)))
            plt.set_zlabel(z_label + " ({0})".format(self._find_axis_symbol(curve.z)))
            plt.legend()
            plt.grid()
    
    

# from svt.unit_collections import SI,MiscUnits
# import numpy as np
# from svt.measured_data import Measured
# curve_list = []
# for i in range(3):
#     curve_list.append(
#         Measured.Curve(
#             x = Measured(np.linspace(0,1/(i+1)),MiscUnits.celsius()),
#             y = Measured(np.linspace(0,i),SI.Pa())
#         )
#     )
# my_figure = MatplotlibFigure(x_unit=MiscUnits.fahrenheit(),y_unit=SI.Pa("M"))
# import matplotlib
# matplotlib.use("TkAgg")
# my_figure.plotCurvesAsShadedRegion(curve_list, curves_label="test", color="b")
# for i,curve in enumerate(curve_list):
#     my_figure.plotCurve(curve,i)
# plt.show()
