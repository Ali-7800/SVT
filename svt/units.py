import numpy as np
from svt._check import Check

class Unit:
    def __init__(
        self,
        symbol:str,
        power = 0,
        numerator_dimensions = [],
        denominator_dimensions = [],
        ) -> None:
        self.power = power
        self.symbol = symbol
        self.numerator_dimensions = numerator_dimensions
        self.denominator_dimensions = denominator_dimensions
        for dimension in self.numerator_dimensions:
            Check.validity(dimension,"Numerator dimensions",self.valid_dimensions())
        for dimension in self.denominator_dimensions:
            Check.validity(dimension,"Denominator dimensions",self.valid_dimensions())

        self.simplify(self.denominator_dimensions,self.numerator_dimensions)
        self.SI_power = self.SI_powers()[np.argmin(abs(self.power-self.SI_powers()))]
        self.SI_prefix = self.SI_prefixes()[np.argmin(abs(self.power-self.SI_powers()))]
        self.multiplier = 10.0**(self.power-self.SI_power)

    def return_full_symbol(self):
        try:
            return self.SI_prefix + self.derived_symbol
        except AttributeError:
            return self.SI_prefix + self.symbol
        
    def return_dimension(self):
        return self.write_symbol(self.numerator_dimensions,self.denominator_dimensions)
    
    def convert_to(self,prefix:str):
        Check.validity(prefix,"SI prefix",self.SI_prefixes())
        self.SI_prefix = prefix
        self.SI_power = self.SI_powers()[self.SI_prefixes().index(prefix)]
        self.multiplier = 10.0**(self.power-self.SI_power)
    
    def copy(self):
        #this method returns a new unit that is a copy of the current class
        new_unit = Unit(self.symbol,self.power,self.numerator_dimensions,self.denominator_dimensions)
        try:
            new_unit.derived_symbol = self.derived_symbol
        except AttributeError:
            pass
        return new_unit
    
    def with_power(self,new_power):
        #this method returns a new unit with same symbol as the class instance but with a new power
        new_unit = Unit(self.symbol,new_power,self.numerator_dimensions,self.denominator_dimensions)
        try:
            new_unit.derived_symbol = self.derived_symbol
        except AttributeError:
            pass
        return new_unit
    
    def with_prefix(self,new_prefix):
        #this method returns a new unit with same symbol as the class instance but with a new power that is the same as the prefix
        Check.validity(new_prefix,"SI prefix",self.SI_prefixes())
        new_power = self.SI_powers()[self.SI_prefixes().index(new_prefix)]
        new_unit = Unit(self.symbol,new_power,self.numerator_dimensions,self.denominator_dimensions)
        try:
            new_unit.derived_symbol = self.derived_symbol
        except AttributeError:
            pass
        return new_unit
    
    @staticmethod
    def simplify(numerator:list,denominator:list):
        common_elements = list(set(numerator).intersection(denominator))
        for common_dimension in common_elements:
            numerator.remove(common_dimension)
            denominator.remove(common_dimension)
    
    @staticmethod
    def write_symbol(numerator:list,denominator:list):
        numerator_str = ""
        denominator_str = ""
        for i in numerator:
            numerator_str += "*{0}".format(i)
        for i in denominator:
            denominator_str += "*{0}".format(i)
        
        if denominator_str == "":
            symbol = "({0})".format(numerator_str[1:])
        elif numerator_str == "":
            symbol = "[1/({0})]".format(denominator_str[1:])
        else:
            symbol = "({0})/({1})".format(numerator_str[1:],denominator_str[1:])
        return symbol
    
    @staticmethod
    def SI_prefixes():
        return ["q","r","y","z","a","f","p","n","µ","m","c","d","","da","h","k","M","G","T","P","E","Z","Y","R","Q"]
    
    @staticmethod
    def SI_powers():
        return np.array([-30,-27,-24,-21,-18,-15,-12,-9,-6,-3,-2,-1,0,1,2,3,6,9,12,15,18,21,24,27,30])
    
    @staticmethod
    def valid_dimensions():
        return ["length","mass","time","temperature"]
    


class DerivedUnit(Unit):
    def __init__(
        self,
        numerator_unit_list=[],
        denominator_unit_list=[],
        derived_symbol=None,
        default_power = 0,
        ) -> None:
        numerator_power = 0
        numerator_symbols = []
        numerator_dimensions = []

        denominator_power = 0
        denominator_symbols = []
        denominator_dimensions = []

        Check.condition(len(numerator_unit_list)>0 or len(denominator_unit_list)>0,ValueError,"There must be at least one unit in the one of the unit lists")

        for unit in numerator_unit_list:
            #check if all list objects are units
            Check.object_class(unit,Unit,"unit",error_msg="At least one of the objects in the numerator unit list is not a unit, please use the Unit class to derive units")
            numerator_power += unit.power
            numerator_symbols.append(unit.symbol)
            numerator_dimensions+=unit.numerator_dimensions
            denominator_dimensions+=unit.denominator_dimensions
        
        for unit in denominator_unit_list:
            #check if all list objects are units
            Check.object_class(unit,Unit,"unit",error_msg="At least one of the objects in the denominator unit list is not a unit, please use the Unit class to derive units")
            denominator_power += unit.power
            denominator_symbols.append(unit.symbol)
            numerator_dimensions+=unit.denominator_dimensions
            denominator_dimensions+=unit.numerator_dimensions
        
        Unit.simplify(numerator_symbols,denominator_symbols)
        symbol = Unit.write_symbol(numerator_symbols,denominator_symbols)
        super().__init__(symbol, power = numerator_power-denominator_power-default_power,numerator_dimensions=numerator_dimensions,denominator_dimensions=denominator_dimensions)
        self.derived_symbol = derived_symbol

    
class UnitSystem:
    def __init__(
        self,
        unit_list:list,) -> None:
        self.unit_list = unit_list
        Check.length(unit_list,"unit_list",1)
        #check if all list objects are units
        Check.list_class(unit,Unit,"unit","unit_list")
        #check to make sure they have the same symbol
        self.symbol = unit_list[0].symbol
        for unit in self.unit_list:
            Check.condition(unit.symbol == self.symbol,ValueError,"At least one of the objects in the unit list does not have the same symbol as the others, please make sure they all have the same symbol")

    def convert_units_to_same_prefix(self):
        minimum_SI_power = Unit.SI_powers()
        for unit in self.unit_list:
            if minimum_SI_power>unit.SI_power:
                minimum_SI_power = unit.SI_power
        minimum_SI_prefix = Unit.SI_prefixes()[np.argmin(abs(minimum_SI_power-Unit.SI_powers()))]
        for unit in self.unit_list:
            unit.convert_to(minimum_SI_prefix)