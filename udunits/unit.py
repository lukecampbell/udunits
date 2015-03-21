#!/usr/bin/env python
# -*- coding: utf-8 -*-
from udunits import systems
from udunits.parser import Parser
import pkg_resources
import xml.etree.ElementTree as ET

class System:
    def __init__(self, name=None):
        self.name = name
        self.symbol_table = {}

    def add(self, unit):
        self.symbol_table[unit.symbol.symbol] = unit

    def __getitem__(self, item):
        if item in self.symbol_table:
            return self.symbol_table[item]
        raise KeyError(item)

class Measure:
    def __init__(self, unit, value):
        self.unit = unit
        self.value = value

    def __repr__(self):
        return '%s %s' % (self.value, self.unit.symbol.symbol)

    def __mul__(self, other):
        if isinstance(other, Measure):
            v = other.value
        v = other
        return Measure(self.unit, self.value * v)

    def __rmul__(self, other):
        return Measure(self.unit, self.value * other)

    def __div__(self, other):
        if isinstance(other, Measure):
            v = other.value
        v = other
        return Measure(self.unit, self.value / v)

class BaseUnit:
    def __init__(self, name, symbol, aliases=None):
        self.name = name
        self.symbol = symbol
        self.aliases = aliases or []

    def is_base(self):
        return self.base

    @classmethod
    def fromtag(cls, tag):
        name = UnitName.from_unit_tag(tag)
        symbol = UnitSymbol.fromtag(tag)
        aliases = UnitAliases.fromtag(tag)
        base = tag.find('base')
        if base is None:
            return None # Not a base unit
        base = True
        return cls(name=name, symbol=symbol, aliases=aliases)

    def __repr__(self):
        return "<BaseUnit '%s'>" % self.symbol.symbol

    def measure(self):
        return Measure(self.base_unit, 1)

class DerivedUnit:
    def __init__(self, base_unit, constant, symbol=None, aliases=None):
        if not isinstance(constant, (float, int)):
            raise ValueError("Invalid constant, must be a valid number")
        self.constant = constant
        self.base_unit = base_unit
        self.symbol = symbol
        self.aliases = aliases or []

    def measure(self):
        return Measure(self.base_unit, self.constant)

    def __repr__(self):
        return "<Unit '%s'>" % self.measure()

    def is_convertible(self, unit):
        if isinstance(unit, BaseUnit):
            return unit.symbol.symbol == self.base_unit.symbol.symbol
        elif isinstance(unit, DerivedUnit):
            return self.is_convertible(unit.base_unit)
        raise TypeError("Unkonwn Type")

    def convert(self, unit):
        if not is_convertible(unit):
            raise ValueError("Inconvertible Units")

    def __mul__(self, other):
        if isinstance(other, (BaseUnit, DerivedUnit)):
            if not self.is_convertible(other):
                raise ValueError("Inconvertible Units")
            other = other.measure()
        measure = self.measure()
        result = measure * other
        return DerivedUnit(self.base_unit, result.value)

    def __rmul__(self, other):
        if not isinstance(other, (int, float)):
            raise TypeError("unsupported operand type(s) for /: '%s' and 'DerivedUnit'") % type(other)
        measure = self.measure()
        result = measure * other
        return DerivedUnit(self.base_unit, result.value)

    def __div__(self, other):
        if isinstance(other, (BaseUnit, DerivedUnit)):
            if not self.is_convertible(other):
                raise ValueError("Inconvertible Units")
            other = other.measure()
        measure = self.measure()
        result = measure / other
        return DerivedUnit(self.base_unit, result.value)
        

class UnitName:
    def __init__(self, singular, plural=None):
        self.singular = singular
        self.plural = plural or singular + 's'

    @classmethod
    def from_unit_tag(cls, tag):
        name = tag.find('name')
        if name is None:
            return None
        return cls.fromtag(name)

    @classmethod
    def fromtag(cls, tag):
        singular = tag.find('singular')
        if singular is None:
            return None
        singular = singular.text.encode('utf-8')
        plural = tag.find('plural')
        if plural is not None:
            plural = plural.text.encode('utf-8')
        return cls(singular, plural)

    def __repr__(self):
        return '<UnitName singular=%s plural=%s>' % (self.singular, self.plural)

class UnitSymbol:
    def __init__(self, symbol):
        self.symbol = symbol

    @classmethod
    def fromtag(cls, tag):
        symbol_tag = tag.find('symbol')
        if symbol_tag is None:
            return None
        return cls(symbol_tag.text.encode('utf-8'))

    def __repr__(self):
        return "<UnitSymbol '%s'>" % self.symbol

class UnitAliases:
    def __init__(self, aliases):
        self.aliases = aliases or []

    @classmethod
    def fromtag(cls, tag):
        aliases = tag.find('aliases')
        if aliases is None:
            return None
        alias_list = []
        for alias in aliases.findall('name'):
            name = UnitName.fromtag(alias)
            alias_list.append(name)
        return cls(aliases=alias_list)

    def __iter__(self):
        for alias in self.aliases:
            yield alias

class Prefix:
    def __init__(self, name, value, symbols):
        self.name = name
        self.value = value
        if not symbols:
            raise ValueError("At least one symbol must be defined")
        self.symbols = symbols

    @classmethod
    def fromtag(cls, tag):
        name = tag.find('name')
        if name is None:
            return None
        name = name.text.encode('utf-8')

        value = tag.find('value')
        if value is None:
            return None
        value = float(value.text)

        symbols = []
        for symbol in tag.findall('symbol'):
            symbol = symbol.text.encode('utf-8')
            symbols.append(symbol)
        if not symbols:
            return None

        return cls(name, value, symbols)

    def __repr__(self):
        return "<Prefix '%s'=%s >" % (self.symbols[0], self.value)


def idea():
    system = System()
    system_xml = pkg_resources.resource_string(systems.__name__, 'udunits2-base.xml')
    root = ET.fromstring(system_xml)
    for unit_tag in root.findall('unit'):
        unit = BaseUnit.fromtag(unit_tag)
        if unit is not None:
            system.add(unit)


    prefix_xml = pkg_resources.resource_string(systems.__name__, 'udunits2-prefixes.xml')
    root = ET.fromstring(prefix_xml)
    for prefix_tag in root.findall('prefix'):
        prefix = Prefix.fromtag(prefix_tag)

    meters = system['m']
    dam = DerivedUnit(meters, 10)
    print dam * 20

    

if __name__ == '__main__':
    idea()

