from svt.units import (
    Unit,
    DerivedUnit,
)
##### SI and other common units
meter = Unit("m")
second = Unit("s")
kilogram = Unit("g",power=3)
celsius = Unit("°C")
Kelvin = Unit("K")
Newton = DerivedUnit([kilogram,meter],2*[second],derived_symbol="N")
Pascal = DerivedUnit([Newton],2*[meter],derived_symbol="Pa")
