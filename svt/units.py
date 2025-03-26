"""
This module includes classes for managing physical units.
"""

import numpy as np
from svt._check import Check

class Unit:
    """
    The Unit class defines a physical unit that is used for tracking operations involving measured physical quantaties.

    Parameters
    ----------
    symbol: str
        the unit's symbol
    prefix: str
        the unit's prefix (if any), should be an SI prefix. Use Unit.SI_prefixes() for valid prefix list.
    numerator_dimensions: list
        list of numerator dimensions, each dimension should be a str. Use Unit.valid_dimensions() for valid dimension list.
    denominator_dimensions: list
        list of denominator dimensions, each dimension should be a str. Use Unit.valid_dimensions() for valid dimension list.

    Attributes
    ----------
    symbol: str
        the unit's symbol
    numerator_dimensions: list
        list of numerator dimensions, for tracking the unit's dimension.
    denominator_dimensions: list
        list of denominator dimensions, for tracking the unit's dimension.
    SI_prefix: str
        the unit's SI prefix.
    SI_power: int
        the power associated with the unit's SI prefix
    power: int
        the unit's power, this is for tracking when the unit is converted to another prefix.
    multiplier: int
        this is what is multipled with the data when the associated unit is converted to another prefix.

    Methods
    -------
    full_symbol: 
        returns str with the unit's symbol and prefix
    dimension:
        returns str with the unit's dimension
    convert_to:
        converts unit into given prefix
    copy:
        returns a copy of the unit
    with_prefix:
        returns a copy of the unit with a different prefix
    _simplify:
        static method for simplifying the unit's dimension
    _write_symbol:
        static method for writing a symbol from two lists of strings
    SI_prefixes:
        static method that returns SI prefixes
    SI_powers:
        static method that returns SI powers
    valid_dimensions:
        static method that returns valid dimensions for the unit
    _find_SI_power_index:
        return the index in Unit.SI_powers() for a given power
    _find_SI_prefix_index:
        return the index in Unit.SI_prefixes() for a given prefixes

    """
    def __init__(
        self,
        symbol:str,
        prefix = "",
        numerator_dimensions = [],
        denominator_dimensions = [],
        ) -> None:
        self.symbol = symbol
        self.numerator_dimensions = numerator_dimensions
        self.denominator_dimensions = denominator_dimensions
        for dimension in self.numerator_dimensions:
            Check.validity(dimension,"Numerator dimensions",self.valid_dimensions())
        for dimension in self.denominator_dimensions:
            Check.validity(dimension,"Denominator dimensions",self.valid_dimensions())

        self._simplify(self.denominator_dimensions,self.numerator_dimensions)
        Check.validity(prefix,"prefix",self.SI_prefixes())
        self.SI_prefix = prefix
        self.SI_power = self.SI_powers()[self._find_SI_prefix_index(prefix)]
        self.power = self.SI_power
        self.multiplier = 1

    def full_symbol(self):
        try:
            return self.SI_prefix + self.derived_symbol
        except:
            return self.SI_prefix + self.symbol
        
    def dimension(self):
        return self._write_symbol(self.numerator_dimensions,self.denominator_dimensions)
    
    def convert_to(self,prefix:str):
        Check.validity(prefix,"SI prefix",self.SI_prefixes())
        self.SI_prefix = prefix
        self.SI_power = self.SI_powers()[self._find_SI_prefix_index(prefix)]
        self.multiplier *= 10.0**(self.power-self.SI_power)
        self.power = self.SI_power
    
    def copy(self):
        #this method returns a new unit that is a copy of the current class
        new_unit = Unit(self.symbol,self.SI_prefix,self.numerator_dimensions,self.denominator_dimensions)
        try:
            new_unit.derived_symbol = self.derived_symbol
        except AttributeError:
            pass
        return new_unit
    
    def with_prefix(self,new_prefix):
        #this method returns a new unit with same symbol as the class instance but with a new power that is the same as the prefix
        Check.validity(new_prefix,"SI prefix",self.SI_prefixes())
        new_unit = Unit(self.symbol,new_prefix,self.numerator_dimensions,self.denominator_dimensions)
        try:
            new_unit.derived_symbol = self.derived_symbol
        except AttributeError:
            pass
        return new_unit
    
    @staticmethod
    def _simplify(numerator:list,denominator:list):
        common_elements = list(set(numerator).intersection(denominator))
        for common_dimension in common_elements:
            numerator.remove(common_dimension)
            denominator.remove(common_dimension)
    
    @staticmethod
    def _write_symbol(numerator:list,denominator:list):
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
        return ["length","mass","time","temperature","current","amount","luminousity"]
    
    @staticmethod
    def _find_SI_power_index(power:int):
        Check.validity(power,"power",Unit.SI_powers())
        return np.argmin(abs((power-Unit.SI_powers())))
    
    @staticmethod
    def _find_SI_prefix_index(prefix:str):
        Check.validity(prefix,"prefix",Unit.SI_prefixes())
        return Unit.SI_prefixes().index(prefix)
    


class DerivedUnit(Unit):
    def __init__(
        self,
        numerator_unit_list=[],
        denominator_unit_list=[],
        derived_symbol=None,
        default_prefix = "",
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

        Check.validity(default_prefix,"SI prefix",Unit.SI_prefixes())
        default_power = Unit.SI_powers()[Unit.SI_prefixes().index(default_prefix)]
        Unit._simplify(numerator_symbols,denominator_symbols)
        symbol = Unit._write_symbol(numerator_symbols,denominator_symbols)
        SI_power = Unit.SI_powers()[Unit._find_SI_power_index(numerator_power-denominator_power-default_power)]
        prefix = Unit.SI_prefixes()[Unit._find_SI_power_index(numerator_power-denominator_power-default_power)]
        super().__init__(symbol, prefix= prefix,numerator_dimensions=numerator_dimensions,denominator_dimensions=denominator_dimensions)
        self.multiplier *= 10.0**(default_power-SI_power)
        self.derived_symbol = derived_symbol
