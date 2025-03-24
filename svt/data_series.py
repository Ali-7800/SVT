import numpy as np
from svt.units import Unit

class Axis:
    def __init__(
        self,
        values:np.ndarray,
        unit:Unit,
        ) -> None:
        self.values = values
        self.unit = unit

    def convert(self,prefix:str):
        Unit.validity_check(prefix,"SI prefix",Unit.SI_prefixes())
        self.unit.convert_to(prefix)
        self.values *= self.unit.multiplier
        self.unit.multiplier = 1 #reset multiplier for future conversions

class DataSeries:
    def __init__(
        self,
        **kwargs:Axis) -> None:
        try:
            assert len(kwargs.keys())>1
        except AssertionError:
            raise ValueError("Must at least have two axes in axes")
        
        for key in kwargs.keys():
            try:
                assert isinstance(kwargs[key],Axis)
            except AssertionError:
                raise ValueError("Every keyword argument in DataSeries must be an Axis")
            setattr(self, key, kwargs[key])
    
    
        
# meter = Unit("m",numerator_dimensions=["length"])
# test = DataSeries(
#     x = Axis(np.linspace(0,1,2),meter.copy()),
#     y =  Axis(np.linspace(0,1,2),meter.copy()),
# )

# print(test.x.values,test.x.unit.return_full_symbol(),test.y.values,test.y.unit.return_full_symbol())
# test.x.convert(prefix="m")
# print(test.x.values,test.x.unit.return_full_symbol(),test.y.values,test.y.unit.return_full_symbol())
# test.x.convert(prefix="")
# print(test.x.values,test.x.unit.return_full_symbol(),test.y.values,test.y.unit.return_full_symbol())
# # test.convert(axis="x",prefix="m")
# # print(test.x)
# # test.convert(axis="x",prefix="")
# # print(test.x)
