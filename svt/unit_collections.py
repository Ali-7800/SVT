from svt.units import (
    Unit,
    MiscUnit,
)

class SI(Unit.Collection):
    """ 
    This is a class for storing and defining SI units
    """
    def __init__(self) -> None:
        unit_list = []
        for method in SI.__dict__:
            if isinstance(SI.__dict__[method],staticmethod):
                my_unit = SI.__dict__[method]()
                unit_list.append(my_unit)
        
        Unit.Collection.__init__(
            self,
            *unit_list,
        )

    @staticmethod
    def m(prefix=""):
        return Unit(symbol = Unit.Symbol(["m"]),dimension = Unit.Dimension(["length"]),prefix= Unit.Prefix(prefix))
    
    @staticmethod
    def s(prefix=""):
        return Unit(symbol = Unit.Symbol(["s"]),dimension = Unit.Dimension(["time"]),prefix= Unit.Prefix(prefix))
    
    @staticmethod
    def Hz(prefix=""):
        return Unit(symbol = Unit.Symbol([],["s"]),dimension = Unit.Dimension([],["time"]),prefix= Unit.Prefix(prefix),alternate_symbol= Unit.Symbol(["Hz"]))
    
    @staticmethod
    def Kg(prefix="k"):
        return Unit(symbol = Unit.Symbol(["g"]),dimension = Unit.Dimension(["mass"]),prefix= Unit.Prefix(prefix))

    @staticmethod
    def K():
        return Unit(symbol = Unit.Symbol(["K"]),dimension = Unit.Dimension(["temperature"]),prefix= Unit.Prefix(""))
    
    @staticmethod
    def A(prefix=""):
        return Unit(symbol = Unit.Symbol(["A"]),dimension = Unit.Dimension(["current"]),prefix= Unit.Prefix(prefix))
    
    @staticmethod
    def mol():
        return Unit(symbol = Unit.Symbol(["mol"]),dimension = Unit.Dimension(["amount"]),prefix= Unit.Prefix(""))
    
    @staticmethod
    def cd():
        return Unit(symbol = Unit.Symbol(["cd"]),dimension = Unit.Dimension(["luminousity"]),prefix= Unit.Prefix(""))
    
    @staticmethod
    def C(prefix=""):
        return Unit(symbol = Unit.Symbol(["A","s"]),dimension = Unit.Dimension(["current","time"]),prefix= Unit.Prefix(prefix),alternate_symbol= Unit.Symbol(["C"]))
    
    @staticmethod
    def V(prefix=""):
        return Unit(symbol = Unit.Symbol(["g","m","m"],["s","s","s","A"]),
                    dimension = Unit.Dimension(["mass","length","length"],3*["time"]+["current"]),
                    prefix= Unit.Prefix(prefix)*Unit.Prefix("k"),
                    alternate_symbol= Unit.Symbol(["V"]),
                    alternate_prefix = Unit.Prefix(prefix))
    
    @staticmethod
    def N(prefix=""):
        return Unit(symbol = Unit.Symbol(["m","g"],2*["s"]),
                    dimension = Unit.Dimension(["length","mass"],2*["time"]),
                    prefix= Unit.Prefix(prefix)*Unit.Prefix("k"),
                    alternate_symbol = Unit.Symbol(["N"]),
                    alternate_prefix = Unit.Prefix(prefix),
                    )
    
    @staticmethod
    def J(prefix=""):
        return Unit(symbol = Unit.Symbol(["m","m","g"],2*["s"]),
                    dimension = Unit.Dimension(["length","length","mass"],2*["time"]),
                    prefix= Unit.Prefix(prefix)*Unit.Prefix("k"),
                    alternate_symbol = Unit.Symbol(["J"]),
                    alternate_prefix = Unit.Prefix(prefix),
                    )
    
    @staticmethod
    def W(prefix=""):
        return Unit(symbol = Unit.Symbol(["m","m","g"],3*["s"]),
                    dimension = Unit.Dimension(["length","length","mass"],3*["time"]),
                    prefix= Unit.Prefix(prefix)*Unit.Prefix("k"),
                    alternate_symbol = Unit.Symbol(["W"]),
                    alternate_prefix = Unit.Prefix(prefix),
                    )
    
    @staticmethod
    def Pa(prefix=""):
        return Unit(symbol = Unit.Symbol(["m","g"],2*["s","m"]),
                    dimension = Unit.Dimension(["length","mass"],2*["time","length"]),
                    prefix= Unit.Prefix(prefix)*Unit.Prefix("k"),
                    alternate_symbol = Unit.Symbol(["Pa"]),
                    alternate_prefix = Unit.Prefix(prefix)*Unit.Prefix(""),
                    )

class MiscUnits(Unit.Collection):
    """ 
    This is a class for storing and defining commmon non SI units
    """
    def __init__(self) -> None:
        unit_list = []
        for method in SI.__dict__:
            if isinstance(SI.__dict__[method],staticmethod):
                my_unit = SI.__dict__[method]()
                unit_list.append(my_unit)
        
        Unit.Collection.__init__(
            self,
            *unit_list,
        )

    @staticmethod
    def celsius():
        return MiscUnit(
                        symbol = Unit.Symbol(["°C"]),
                        SI_unit_counterpart=SI.K(),
                        convert_from_SI= lambda x:x-273.15,
                        convert_to_SI= lambda x:x+273.15,)
    @staticmethod
    def per_celsius():
        return MiscUnit(
                        symbol = Unit.Symbol([],["°C"]),
                        SI_unit_counterpart=1/SI.K(),
                        convert_from_SI= lambda x:x,
                        convert_to_SI= lambda x:x,)
    @staticmethod
    def fahrenheit():
        return MiscUnit(
                        symbol = Unit.Symbol(["°F"]),
                        SI_unit_counterpart=SI.K(),
                        convert_from_SI= lambda x:1.8*(x-273.15)+32,
                        convert_to_SI= lambda x:((x-32)/1.8)+273.15,)
