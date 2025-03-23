import numpy as np

class Unit:
    def __init__(
        self,
        symbol:str,
        power = 0,
        ) -> None:
        self.power = power
        self.symbol = symbol
        self.SI_powers = np.array([
            -30,
            -27,
            -24,
            -21,
            -18,
            -15,
            -12,
            -9,
            -6,
            -3,
            -2,
            -1,
            0,
            1,
            2,
            3,
            6,
            9,
            12,
            15,
            18,
            21,
            24,
            27,
            30
        ])
        self.SI_prefixes = [
            "q",
            "r",
            "y",
            "z",
            "a",
            "f",
            "p",
            "n",
            "µ",
            "m",
            "c",
            "d",
            "",
            "da",
            "h",
            "k",
            "M",
            "G",
            "T",
            "P",
            "E",
            "Z",
            "Y",
            "R",
            "Q",
        ]
        self.SI_power = self.SI_powers[np.argmin(abs(self.power-self.SI_powers))]
        self.SI_prefix = self.SI_prefixes[np.argmin(abs(self.power-self.SI_powers))]
        self.multiplier = 10.0**(self.power-self.SI_power)

    def return_symbol(self):
        if self.derived_symbol is None:
            return self.SI_prefix + self.symbol
        else:
            return self.SI_prefix + self.derived_symbol
    
    def convert_to(self,prefix:str):
        try:
            assert prefix in self.SI_prefixes
        except AssertionError:
            raise ValueError("{0} is not an SI prefix".format(prefix))
        self.SI_prefix = prefix
        self.SI_power = self.SI_powers[self.SI_prefixes.index(prefix)]
        self.multiplier = 10.0**(self.power-self.SI_power)


class DerivedUnit(Unit):
    def __init__(
        self,
        numerator_unit_list=[],
        denominator_unit_list=[],
        derived_symbol=None,
        ) -> None:
        numerator_power = 0
        numerator_symbol = ""

        denominator_power = 0
        denominator_symbol = ""

        try:
            assert len(numerator_unit_list)>0 or len(denominator_unit_list)>0
        except AssertionError:
            raise ValueError("There must be at least one unit in the one of the unit lists")

        for unit in numerator_unit_list:
            #check if all list objects are units
            try:
                assert isinstance(unit,Unit)
            except AssertionError:
                raise ValueError("At least one of the objects in the numerator unit list is not a unit, please use the Unit class to derive units")
            numerator_power += unit.power
            numerator_symbol += "*{0}".format(unit.symbol)
        
        for unit in denominator_unit_list:
            #check if all list objects are units
            try:
                assert isinstance(unit,Unit)
            except AssertionError:
                raise ValueError("At least one of the objects in the denominator unit list is not a unit, please use the Unit class to derive units")
            denominator_power += unit.power
            denominator_symbol += "*{0}".format(unit.symbol)

        if denominator_symbol == "":
            symbol = "({0})".format(numerator_symbol[1:])
        elif numerator_symbol == "":
            symbol = "[1/({0})]".format(denominator_symbol[1:])
        else:
            symbol = "({0})/({1})".format(numerator_symbol[1:],denominator_symbol[1:])

        super().__init__(symbol, power = numerator_power-denominator_power)
        self.derived_symbol = derived_symbol

class UnitSystem:
    def __init__(
        self,
        unit_list:list,) -> None:
        self.unit_list = unit_list
        try:
            assert len(unit_list)>0
        except AssertionError:
            raise ValueError("There must be at least one unit in the unit list")
        #check if all list objects are units
        for unit in self.unit_list:
            try:
                assert isinstance(unit,Unit)
            except AssertionError:
                raise ValueError("At least one of the objects in the unit list is not a unit, please use the Unit class to derive units")
        #check to make sure they have the same symbol
        self.symbol = unit_list[0].symbol
        for unit in self.unit_list:
            try:
                assert unit.symbol == self.symbol
            except AssertionError:
                raise ValueError("At least one of the objects in the unit list does not have the same symbol as the others, please make sure they all have the same symbol")

    def convert_units_to_same_prefix(self):
        minimum_SI_power = self.unit_list[0].SI_powers[-1]
        for unit in self.unit_list:
            if minimum_SI_power>unit.SI_power:
                minimum_SI_power = unit.SI_power
        minimum_SI_prefix = self.unit_list[0].SI_prefixes[np.argmin(abs(minimum_SI_power-self.unit_list[0].SI_powers))]
        for unit in self.unit_list:
            unit.convert_to(minimum_SI_prefix)