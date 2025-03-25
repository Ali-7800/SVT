import numpy as np
from svt.units import Unit
from svt._check import Check
from typing import Union

class MeasuredData:
    def __init__(
        self,
        values: Union[np.ndarray,list],
        unit:Unit,
        ) -> None:
        self.values = np.array(values)
        self.unit = unit

    def convert(self,prefix:str):
        Check.validity(prefix,"SI prefix",Unit.SI_prefixes())
        self.values /= self.unit.multiplier
        self.unit.convert_to(prefix)
        self.values *= self.unit.multiplier

class DataCollection:
    def __init__(
        self,
        **kwargs:MeasuredData) -> None:
        Check.length(kwargs.keys(),"Measured data arrays",2)
        for key in kwargs.keys():
            Check.object_class(kwargs[key],MeasuredData,"","Every keyword argument in DataCollection must be an instance of MeasuredData")
            setattr(self, key, kwargs[key])