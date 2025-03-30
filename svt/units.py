"""
This module includes classes for managing physical units.
"""

import numpy as np
from svt._check import Check

class Unit:
    """ 
    This is a class for defining SI units
    """
    def __init__(
        self,
        symbol,
        dimension,
        prefix,
        alternate_symbol=None,
        alternate_prefix=None) -> None:

        Check.object_class(symbol,Unit.Symbol,"Symbol")
        self.symbol = symbol
        self.alternate_symbol = symbol
        Check.object_class(dimension,Unit.Dimension,"Dimension")
        self.dimension = dimension
        Check.object_class(prefix,Unit.Prefix,"Prefix")
        self.prefix = prefix
        self.alternate_prefix = prefix
        
        if alternate_symbol is not None:
            Check.object_class(alternate_symbol,Unit.Symbol,"Alternate Symbol")
            self.alternate_symbol = alternate_symbol
        if alternate_prefix is not None:
            Check.object_class(alternate_prefix,Unit.Prefix,"Alternate Prefix")
            self.alternate_prefix = alternate_prefix
        
        self.prefix_ratio = self.prefix/self.alternate_prefix
    
    def __eq__(self, other):
        if isinstance(other,Unit):
            if ((self.symbol == other.symbol) and (self.dimension == other.dimension) and (self.prefix == other.prefix)):
                return 1
            elif (self.symbol == other.symbol) and (self.dimension == other.dimension):
                return 0.5
            else:
                return 0
        else:
            NotImplemented

    def __str__(self):
        return self.alternate_prefix.__str__()+ self.alternate_symbol.__str__()
    
    def full_symbol(self):
        return self.prefix.__str__()+ self.symbol.__str__()

    def plot_symbol(self):
        return "${0}$".format(self.alternate_prefix.__str__()+self.alternate_symbol._symbol_with_powers())
    
    def _has_alternate_symbol(self):
        return not (self.alternate_symbol == self.symbol)
    
    def _update_prefix(self,new_prefix):
        if isinstance(new_prefix,Unit.Prefix):
            multiplier = 10.0**(self.prefix/new_prefix).power
            return multiplier,Unit(self.symbol,self.dimension,new_prefix,self.alternate_symbol,new_prefix/self.prefix_ratio)
        NotImplemented
    
    def update_prefix(self,new_prefix:str):
        prefix = self.alternate_prefix.convert_to(new_prefix)
        return Unit(self.symbol,self.dimension,prefix*self.prefix_ratio,self.alternate_symbol,prefix)
    
    def __mul__(self, other):
        if isinstance(other, Unit):
            return Unit(self.symbol*other.symbol,
                        self.dimension*other.dimension,
                        self.prefix*other.prefix,
                        self.alternate_symbol*other.alternate_symbol,
                        self.alternate_prefix*other.alternate_prefix)
        return NotImplemented
    
    def __rmul__(self,other):
        if isinstance(other, Unit):
            return Unit(other.symbol*self.symbol,
                        other.dimension*self.dimension,
                        other.prefix*self.prefix,
                        self.alternate_symbol*other.alternate_symbol,
                        self.alternate_prefix*other.alternate_prefix)
        return NotImplemented
    
    def __truediv__(self, other):
        if isinstance(other, Unit):
            return Unit(self.symbol/other.symbol,
                        self.dimension/other.dimension,
                        self.prefix/other.prefix,
                        self.alternate_symbol/other.alternate_symbol,
                        self.alternate_prefix/other.alternate_prefix)
        return NotImplemented

    def __rtruediv__(self, other):
        if isinstance(other, Unit):
            return Unit(other.symbol/self.symbol,
                        other.dimension/self.dimension,
                        other.prefix/self.prefix,
                        other.alternate_symbol/self.alternate_symbol,
                        other.alternate_prefix/self.alternate_prefix)
        elif isinstance(other, (int,float)):
            if (other == 1) or (other == 1.0):
                return Unit(1/self.symbol,
                        1/self.dimension,
                        1/self.prefix,
                        1/self.alternate_symbol,
                        1/self.alternate_prefix)
        return NotImplemented
    
    def __pow__(self, exponent):
        if isinstance(exponent,int):
            return Unit(self.symbol**exponent,
            self.dimension**exponent,
            self.prefix**exponent,
            self.alternate_symbol**exponent,
            self.alternate_prefix**exponent)
        return NotImplemented  
    
    def convert_prefix_to(self,prefix:str):
        return Unit(self.symbol,self.dimension,self.alternate_prefix.convert_to(prefix)*self.prefix_ratio,self.alternate_symbol,self.alternate_prefix.convert_to(prefix))

    @staticmethod
    def _simplify(numerator:list,denominator:list):
        common_elements = list(set(numerator).intersection(denominator))
        for common_dimension in common_elements:
            numerator.remove(common_dimension)
            denominator.remove(common_dimension)
    
    @staticmethod
    def _write_product_symbol(product_list:list):
        product = ""
        for i in product_list:
            product += "*{0}".format(i)
        if len(product_list) == 0:
            return product
        if len(product_list) == 1:
            return product[1:]
        else:
            return "({0})".format(product[1:])
    
    @staticmethod
    def _write_product_with_powers_symbol(product_list:list):
        powers_list = [(x,product_list.count(x)) for x in set(product_list)]
        product = ""
        for symbol,power in powers_list:
            if power == 1:
                product += "*{0}".format(symbol,power)
            else:
                product += "*{0}^{1}".format(symbol,power)
        if len(powers_list) == 0:
            return product
        if len(powers_list) == 1:
            return product[1:]
        else:
            return "({0})".format(product[1:])
    
    @staticmethod
    def _write_quotient_with_powers(numerator_list:list,denominator_list:list):
        numerator_str = Unit._write_product_with_powers_symbol(numerator_list)
        denominator_str = Unit._write_product_with_powers_symbol(denominator_list)
        if len(denominator_list) == 0:
            str = "{0}".format(numerator_str)
        elif len(numerator_list) == 0:
            str = "1/{0}".format(denominator_str)
        else:
            str = "{0}/{1}".format(numerator_str,denominator_str)
        return str
    
    @staticmethod
    def _write_quotient(numerator_list:list,denominator_list:list):
        numerator_str = Unit._write_product_symbol(numerator_list)
        denominator_str = Unit._write_product_symbol(denominator_list)
        if len(denominator_list) == 0:
            str = "{0}".format(numerator_str)
        elif len(numerator_list) == 0:
            str = "1/{0}".format(denominator_str)
        else:
            str = "{0}/{1}".format(numerator_str,denominator_str)
        return str
    
    @staticmethod
    def unify_prefixes(unit_1,unit_2):
        Check.object_class(unit_1,Unit,"first unit")
        Check.object_class(unit_2,Unit,"second unit")
        max_prefix = max(unit_1.prefix,unit_2.prefix)
        m1,d1 = unit_1._update_prefix(max_prefix)
        m2,d2 = unit_2._update_prefix(max_prefix)
        if d1._has_alternate_symbol():
            new_unit = d1
            if d2._has_alternate_symbol():
                if Unit.Symbol._simpler_than(d2.alternate_symbol,d1.alternate_symbol):
                    new_unit = d2
        else:
            new_unit = d2
        return m1,m2,new_unit

    class Symbol:
        def __init__(
            self,
            numerator=[],
            denominator=[],
            ) -> None:
            Check.object_class(numerator,list,"Numerator symbols")
            Check.object_class(denominator,list,"Denominator symbols")
            for i in numerator:
                Check.object_class(i,str,"Numerator symbols")
            for i in denominator:
                Check.object_class(i,str,"Denominator symbols")
            Unit._simplify(numerator,denominator)
            self.numerator = numerator
            self.denominator = denominator
            self.symbol = Unit._write_quotient(numerator,denominator)
            self.symbol_with_powers = Unit._write_quotient_with_powers(numerator,denominator)
       
        def __eq__(self, other) -> bool:
            if isinstance(other,Unit.Symbol):
                return (sorted(self.numerator) == sorted(other.numerator)) and (sorted(self.denominator) == sorted(other.denominator))
            else:
                False
        
        def __len__(self):
            return len(self.numerator)+len(self.denominator)
        
        def __str__(self) -> str:
            return "{0}".format(self.symbol)
        
        def _symbol_with_powers(self):
            return "{0}".format(self.symbol_with_powers)
        
        def __mul__(self, other):
            if isinstance(other, Unit.Symbol):
                return Unit.Symbol(self.numerator+other.numerator,self.denominator+other.denominator)
            return NotImplemented
        
        def __rmul__(self,other):
            if isinstance(other, Unit.Symbol):
                return Unit.Symbol(self.numerator+other.numerator,self.denominator+other.denominator)
            return NotImplemented
        
        def __truediv__(self, other):
            if isinstance(other, Unit.Symbol):
                return Unit.Symbol(self.numerator+other.denominator,self.denominator+other.numerator)
            return NotImplemented

        def __rtruediv__(self, other):
            if isinstance(other, Unit.Symbol):
                return Unit.Symbol(self.denominator+other.numerator,self.numerator+other.denominator)
            elif isinstance(other, (int,float)):
                if (other == 1) or (other == 1.0):
                    return Unit.Symbol(self.denominator,self.numerator)
            return NotImplemented
        
        def __pow__(self, exponent):
            if isinstance(exponent,int):
                return Unit.Symbol(exponent*self.numerator,exponent*self.denominator)
            return NotImplemented 
        
        @staticmethod
        def _simpler_than(symbol1,symbol2):
            if len(symbol1)<len(symbol2):
                return True
            else:
                return False
            
    class Dimension(Symbol):
        def __init__(
                    self,
                    numerator=[],
                    denominator=[],) -> None:
            Check.object_class(numerator,list,"Numerator dimension list")
            Check.object_class(denominator,list,"Denominator dimension list")
            for dimension in numerator:
                Check.validity(dimension,"Numerator dimensions",self.valid_dimensions())
            for dimension in denominator:
                Check.validity(dimension,"Denominator dimensions",self.valid_dimensions())
            Unit.Symbol.__init__(self,numerator,denominator)
        
        def __mul__(self, other):
            if isinstance(other, Unit.Dimension):
                return Unit.Dimension(self.numerator+other.numerator,self.denominator+other.denominator)
            return NotImplemented
        
        def __rmul__(self,other):
            if isinstance(other, Unit.Dimension):
                return Unit.Dimension(self.numerator+other.numerator,self.denominator+other.denominator)
            return NotImplemented
        
        def __truediv__(self, other):
            if isinstance(other, Unit.Dimension):
                return Unit.Dimension(self.numerator+other.denominator,self.denominator+other.numerator)
            return NotImplemented

        def __rtruediv__(self, other):
            if isinstance(other, Unit.Dimension):
                return Unit.Dimension(self.denominator+other.numerator,self.numerator+other.denominator)
            elif isinstance(other, (int,float)):
                if (other == 1) or (other == 1.0):
                    return Unit.Dimension(self.denominator,self.numerator)
            return NotImplemented
        
        def __pow__(self, exponent):
            if isinstance(exponent,int):
                return Unit.Dimension(exponent*self.numerator,exponent*self.denominator)
            return NotImplemented  
        
        @staticmethod
        def valid_dimensions():
            return ["length","mass","time","temperature","current","amount","luminousity"]
    
    class Prefix:
        def __init__(
            self,
            symbol:str,
            power=None,) -> None:
            Check.validity(symbol,"SI prefix",self.SI_prefixes())
            self.symbol = symbol
            self.SI_power = self.SI_powers()[self._find_SI_prefix_index(symbol)]
            if power is None:
                self.power = self.SI_power
            else:
                self.power = power
            self.multiplier = 10.0**(self.power-self.SI_power)

        def __str__(self):
            if self.multiplier == 1.0:
                return self.symbol
            else:
                return str(self.multiplier)+self.symbol

        def __eq__(self, other):
            """Defines behavior for the equality operator (==)."""
            if isinstance(other, Unit.Prefix):
                return self.power == other.power
            return False

        def __ne__(self, other):
            """Defines behavior for the inequality operator (!=)."""
            return not self.__eq__(other)

        def __lt__(self, other):
            """Defines behavior for the less-than operator (<)."""
            if isinstance(other, Unit.Prefix):
                return self.power < other.power
            return NotImplemented

        def __gt__(self, other):
            """Defines behavior for the greater-than operator (>)."""
            if isinstance(other, Unit.Prefix):
                return self.power > other.power
            return NotImplemented

        def __le__(self, other):
            """Defines behavior for the less-than-or-equal-to operator (<=)."""
            if isinstance(other, Unit.Prefix):
                return self.power <= other.power
            return NotImplemented

        def __ge__(self, other):
            """Defines behavior for the greater-than-or-equal-to operator (>=)."""
            if isinstance(other, Unit.Prefix):
                return self.power >= other.power
            return NotImplemented

        def __mul__(self, other):
            if isinstance(other, Unit.Prefix):
                new_power = self.power+other.power
                new_symbol = self.SI_prefixes()[self._find_closest_SI_power_index(new_power)]
                return Unit.Prefix(new_symbol,new_power)
            return NotImplemented
        
        def __rmul__(self,other):
            if isinstance(other, Unit.Prefix):
                new_power = self.power+other.power
                new_symbol = self.SI_prefixes()[self._find_closest_SI_power_index(new_power)]
                return Unit.Prefix(new_symbol,new_power)
            return NotImplemented
        
        def __truediv__(self, other):
            if isinstance(other, Unit.Prefix):
                new_power = self.power-other.power
                new_symbol = self.SI_prefixes()[self._find_closest_SI_power_index(new_power)]
                return Unit.Prefix(new_symbol,new_power)
            return NotImplemented

        def __rtruediv__(self, other):
            if isinstance(other, Unit.Prefix):
                new_power = other.power-self.power
                new_symbol = self.SI_prefixes()[self._find_closest_SI_power_index(new_power)]
                return Unit.Prefix(new_symbol,new_power)
            elif isinstance(other, (int,float)):
                if (other == 1) or (other == 1.0):
                    new_power = -self.power
                    new_symbol = self.SI_prefixes()[self._find_closest_SI_power_index(new_power)]
                return Unit.Prefix(new_symbol,new_power)
            return NotImplemented
        
        def __pow__(self, exponent):
            if isinstance(exponent,int):
                new_power = exponent*self.power
                new_symbol = self.SI_prefixes()[self._find_closest_SI_power_index(new_power)]
                return Unit.Prefix(new_symbol,new_power)
            return NotImplemented 
        
        def convert_to(self,prefix:str):
            Check.validity(prefix,"SI prefix",self.SI_prefixes())
            return Unit.Prefix(prefix,self.power)
        
        @staticmethod
        def SI_prefixes():
            return ["q","r","y","z","a","f","p","n","µ","m","c","d","","da","h","k","M","G","T","P","E","Z","Y","R","Q"]

        @staticmethod
        def SI_powers():
            return np.array([-30,-27,-24,-21,-18,-15,-12,-9,-6,-3,-2,-1,0,1,2,3,6,9,12,15,18,21,24,27,30])

        @staticmethod
        def _find_closest_SI_power_index(power:int):
            return np.argmin(abs((power-Unit.Prefix.SI_powers())))

        @staticmethod
        def _find_SI_prefix_index(prefix:str):
            Check.validity(prefix,"prefix",Unit.Prefix.SI_prefixes())
            return Unit.Prefix.SI_prefixes().index(prefix)

    class Collection:
        def __init__(
            self,
            *args,
            **kwargs) -> None:
            self.shape = None
            self.dict = {}
            self.symbol_dict = {}
            self.append(*args,**kwargs)
            
        def append(self,*args,**kwargs):
            for key in kwargs.keys():
                Check.object_class(kwargs[key],(Unit,MiscUnit),"keyword argument")
                self.dict[key] = kwargs[key]
                self.symbol_dict[key] = kwargs[key].__str__()
            for argument in args:
                Check.object_class(argument,(Unit,MiscUnit),"argument")
                if isinstance(argument,Unit):
                    self.dict[argument.dimension.symbol] = argument
                    self.symbol_dict[argument.dimension.symbol] = argument.__str__()
                else:
                    self.dict[argument.SI_unit.dimension.symbol] = argument
                    self.symbol_dict[argument.SI_unit.dimension.symbol] = argument.symbol.__str__()
        
        def __getitem__(self, key):
            Check.validity(key,"given key",self.dict.keys())
            return self.dict[key]
    
        def __setitem__(self, key, value):
            Check.validity(key,"given key",self.dict.keys())
            Check.object_class(value,(Unit,MiscUnit),"value","To change a key in a Unit.Collection, the value given must be a Unit or a MiscUnit")
            self.dict[key] = value
        
        def __contains__(self, item):
            return (item in self.dict.keys())
        
        def __str__(self) -> str:
            return self.symbol_dict.__str__()


class MiscUnit:
    def __init__(self,
                 symbol:Unit.Symbol,
                 SI_unit_counterpart:Unit,
                 convert_to_SI:callable,
                 convert_from_SI:callable,
                 ) -> None:
        Check.object_class(symbol,Unit.Symbol,"Symbol")
        self.symbol = symbol
        Check.object_class(SI_unit_counterpart,Unit,"SI Unit Counterpart")
        self.SI_unit = SI_unit_counterpart
        #need function checks
        self.convert_to_SI = convert_to_SI
        self.convert_from_SI = convert_from_SI

    def __eq__(self, other):
        if isinstance(other,MiscUnit):
            if (self.SI_unit==other.SI_unit)==1 and self.symbol==other.symbol:
                return True
            else:
                return False
        else:
            NotImplemented