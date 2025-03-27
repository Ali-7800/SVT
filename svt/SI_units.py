from svt.units import (
    Unit,
    DerivedUnit,
)

class SI:
    """ 
        This is a class for storing SI untis
    """
    def __init__(self) -> None:
        pass 
    
    @staticmethod
    def meter():
        return Unit("m",numerator_dimensions=["length"])
    
    @staticmethod
    def second():
        return Unit("s",numerator_dimensions=["time"])
    
    @staticmethod
    def hertz():
        return Unit("Hz",denominator_dimensions=["time"])
    
    @staticmethod
    def kilogram():
        return Unit("g",prefix="k",numerator_dimensions=["mass"])
    
    @staticmethod
    def celsius():
        return Unit("°C",numerator_dimensions=["temperature"])
    
    @staticmethod
    def kelvin():
        return Unit("K",numerator_dimensions=["temperature"])
    
    @staticmethod
    def ampere():
        return Unit("A",numerator_dimensions=["current"])
    
    @staticmethod
    def mole():
        return Unit("mol",numerator_dimensions=["amount"])
    
    @staticmethod
    def candela():
        return Unit("cd",numerator_dimensions=["luminousity"])
    
    @staticmethod
    def coloumb():
        return DerivedUnit([SI.ampere(),SI.second()],derived_symbol="C")
    
    @staticmethod
    def volt():
        return DerivedUnit([SI.kilogram()]+2*[SI.meter()],3*[SI.second()]+[SI.ampere()],derived_symbol="V",default_prefix="k")
    
    @staticmethod
    def newton():
        return DerivedUnit([SI.kilogram(),SI.meter()],2*[SI.second()],derived_symbol="N",default_prefix="k")
    
    @staticmethod
    def joule():
        return DerivedUnit([SI.newton(),SI.meter()],derived_symbol="J")
    
    @staticmethod
    def watt():
        return DerivedUnit([SI.joule()],[SI.second()],derived_symbol="W")
    
    @staticmethod
    def pascal():
        return DerivedUnit([SI.newton()],2*[SI.meter()],derived_symbol="Pa")
