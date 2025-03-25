import numpy as np
from svt.units import Unit,DerivedUnit
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
    
    def scale(self,factor:float):
        self.values *= factor

    def convert_to(self,prefix:str):
        Check.validity(prefix,"SI prefix",Unit.SI_prefixes())
        self.values /= self.unit.multiplier
        self.unit.convert_to(prefix)
        self.values *= self.unit.multiplier
    
    def copy(self):
        return MeasuredData(self.values,self.unit)

class MeasuredDataCollection:
    def __init__(
        self,
        **kwargs:MeasuredData) -> None:
        self.keys = []
        for key in kwargs.keys():
            Check.object_class(kwargs[key],MeasuredData,"","Every keyword argument in MeasuredDataCollection must be an instance of MeasuredData")
            setattr(self, key, kwargs[key])
        self.keys+=kwargs.keys()
        
    def append(self,**kwargs):
        for key in kwargs.keys():
            Check.object_class(kwargs[key],MeasuredData,"","Only MeasuredData can be appended to a MeasuredDataCollection")
            Check.condition(key not in self.keys,KeyError,"Key already used for other MeasuredData, please use a different key")
            setattr(self, key, kwargs[key])
        self.keys+=kwargs.keys()
    
    @staticmethod
    def add(MeasuredData1,MeasuredData2):
        Check.condition(MeasuredData1.unit.dimension()==MeasuredData2.unit.dimension(),ValueError,"To add MeasuredData, they must have the same unit dimensions")
        if MeasuredData1.unit!=MeasuredData2.unit:
            min_SI_power = min(MeasuredData1.unit.SI_power,MeasuredData1.unit.SI_power)
            minimum_prefix = Unit.SI_prefixes()[Unit._find_SI_power_index(min_SI_power)]
            d1 = MeasuredData1.copy()
            d1.convert_to(minimum_prefix)
            d2 = MeasuredData2.copy()
            d2.convert_to(minimum_prefix)
            return MeasuredData(values = d1.values+d2.values,unit=d1.unit)

    @staticmethod
    def subtract(MeasuredData1,MeasuredData2):
        Check.condition(MeasuredData1.unit.dimension()==MeasuredData2.unit.dimension(),ValueError,"To subtract MeasuredData, they must have the same unit dimensions")
        if MeasuredData1.unit!=MeasuredData2.unit:
            min_SI_power = min(MeasuredData1.unit.SI_power,MeasuredData1.unit.SI_power)
            minimum_prefix = Unit.SI_prefixes()[Unit._find_SI_power_index(min_SI_power)]
            d1 = MeasuredData1.copy()
            d1.convert_to(minimum_prefix)
            d2 = MeasuredData2.copy()
            d2.convert_to(minimum_prefix)
            return MeasuredData(values = d1.values-d2.values,unit=d1.unit)
    
    @staticmethod
    def multiply(MeasuredData1,MeasuredData2):
        new_unit = DerivedUnit([MeasuredData1.unit,MeasuredData2.unit])
        return MeasuredData(values=MeasuredData1.values*MeasuredData2.values,unit=new_unit)
    
    @staticmethod
    def divide(MeasuredData1,MeasuredData2):
        new_unit = DerivedUnit([MeasuredData1.unit],[MeasuredData2.unit])
        return MeasuredData(values=MeasuredData1.values/MeasuredData2.values,unit=new_unit)
