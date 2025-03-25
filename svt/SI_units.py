from svt.units import (
    Unit,
    DerivedUnit,
)

class SIUnitSystem:
    """ 
        This is a class for storing SI untis
    """
    def __init__(self) -> None:
        self.meter = Unit("m",numerator_dimensions=["length"])
        self.second = Unit("s",numerator_dimensions=["time"])
        self.hertz = Unit("Hz",denominator_dimensions=["time"])
        self.kilogram = Unit("g",power=3,numerator_dimensions=["mass"])
        self.celsius = Unit("°C",numerator_dimensions=["temperature"])
        self.kelvin = Unit("K",numerator_dimensions=["temperature"])
        self.newton = DerivedUnit([self.kilogram,self.meter],2*[self.second],derived_symbol="N",default_power=3)
        self.pascal = DerivedUnit([self.newton],2*[self.meter],derived_symbol="Pa")
