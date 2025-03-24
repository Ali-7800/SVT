from svt.units import (
    Unit,
    DerivedUnit,
)
##### SI and other common units
meter = Unit("m",numerator_dimensions=["length"])
second = Unit("s",numerator_dimensions=["time"])
hertz = Unit("Hz",denominator_dimensions=["time"])
kilogram = Unit("g",power=3,numerator_dimensions=["mass"])
celsius = Unit("°C",numerator_dimensions=["temperature"])
kelvin = Unit("K",numerator_dimensions=["temperature"])
newton = DerivedUnit([kilogram,meter],2*[second],derived_symbol="N",default_power=3)
pascal = DerivedUnit([newton],2*[meter],derived_symbol="Pa")