from svt.units import (
    Unit
)

class SI:
    """ 
    This is a class for storing and defining SI units
    """
    def __init__(self) -> None:
        pass

    @staticmethod
    def meter():
        return Unit(symbol = Unit.Symbol(["m"]),dimension = Unit.Dimension(["length"]),prefix= Unit.Prefix(""))
    
    @staticmethod
    def second():
        return Unit(symbol = Unit.Symbol(["s"]),dimension = Unit.Dimension(["time"]),prefix= Unit.Prefix(""))
    
    @staticmethod
    def hertz():
        return Unit(symbol = Unit.Symbol([],["s"]),dimension = Unit.Dimension([],["time"]),prefix= Unit.Prefix(""),alternate_symbol= Unit.Symbol(["Hz"]))
    
    @staticmethod
    def kilogram():
        return Unit(symbol = Unit.Symbol(["g"]),dimension = Unit.Dimension(["mass"]),prefix= Unit.Prefix("k"))
    
    @staticmethod
    def celsius():
        return Unit(symbol = Unit.Symbol(["°C"]),dimension = Unit.Dimension(["temperature"]),prefix= Unit.Prefix(""))
    
    @staticmethod
    def kelvin():
        return Unit(symbol = Unit.Symbol(["K"]),dimension = Unit.Dimension(["temperature"]),prefix= Unit.Prefix(""))
    
    @staticmethod
    def ampere():
        return Unit(symbol = Unit.Symbol(["A"]),dimension = Unit.Dimension(["current"]),prefix= Unit.Prefix(""))
    
    @staticmethod
    def mole():
        return Unit(symbol = Unit.Symbol(["mol"]),dimension = Unit.Dimension(["amount"]),prefix= Unit.Prefix(""))
    
    @staticmethod
    def candela():
        return Unit(symbol = Unit.Symbol(["cd"]),dimension = Unit.Dimension(["luminousity"]),prefix= Unit.Prefix(""))
    
    @staticmethod
    def coloumb():
        return Unit(symbol = Unit.Symbol(["A","s"]),dimension = Unit.Dimension(["current","time"]),prefix= Unit.Prefix(""),alternate_symbol= Unit.Symbol(["C"]))
    
    @staticmethod
    def volt():
        return Unit(symbol = Unit.Symbol(["Kg","m","m"],["s","s","s","A"]),
                    dimension = Unit.Dimension(["mass","length","length"],3*["time"]+["current"]),
                    prefix= Unit.Prefix("k"),
                    alternate_symbol= Unit.Symbol(["V"]),
                    alternate_prefix = Unit.Prefix(""))
    
    @staticmethod
    def newton():
        return Unit(symbol = Unit.Symbol(["m","g"],2*["s"]),
                    dimension = Unit.Dimension(["length","mass"],2*["time"]),
                    prefix= Unit.Prefix("k"),
                    alternate_symbol = Unit.Symbol(["N"]),
                    alternate_prefix = Unit.Prefix(""),
                    )
    
    @staticmethod
    def joule():
        return Unit(symbol = Unit.Symbol(["m","m","g"],2*["s"]),
                    dimension = Unit.Dimension(["length","length","mass"],2*["time"]),
                    prefix= Unit.Prefix("k"),
                    alternate_symbol = Unit.Symbol(["J"]),
                    alternate_prefix = Unit.Prefix(""),
                    )
    
    @staticmethod
    def watt():
        return Unit(symbol = Unit.Symbol(["m","m","g"],3*["s"]),
                    dimension = Unit.Dimension(["length","length","mass"],3*["time"]),
                    prefix= Unit.Prefix("k"),
                    alternate_symbol = Unit.Symbol(["W"]),
                    alternate_prefix = Unit.Prefix(""),
                    )
    
    @staticmethod
    def pascal():
        return Unit(symbol = Unit.Symbol(["m","g"],2*["s","m"]),
                    dimension = Unit.Dimension(["length","mass"],2*["time","length"]),
                    prefix= Unit.Prefix("k"),
                    alternate_symbol = Unit.Symbol(["Pa"]),
                    alternate_prefix = Unit.Prefix(""),
                    )
