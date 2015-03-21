#!/usr/bin/env python
# -*- coding: utf-8 -*-
from udunits import systems
from udunits.parser import Parser
import pkg_resources
import xml.etree.ElementTree as ET

class System:
    def __init__(self):
        self.units = {}
class Unit:
    def __init__(self, name, symbol, aliases=None, base=False, definition=None):
        self.name = name
        self.symbol = symbol
        self.aliases = aliases or []
        self.base = base
        self.definition = definition

    def is_base(self):
        return self.base

    @classmethod
    def fromtag(cls, tag):
        name = UnitName.from_unit_tag(tag)
        symbol = UnitSymbol.fromtag(tag)
        aliases = UnitAliases.fromtag(tag)
        base = tag.find('base')
        if base is None:
            base = False
        base = True
        definition = tag.find('def')
        if definition is not None:
            definition = definition.text.encode('utf-8')
            parser = Parser()
            try:
                tokens = parser.parse(definition)
            except:
                print "BAD DEFINITION:", definition
        return cls(name=name, symbol=symbol, aliases=aliases, base=base, definition=definition)

    def __repr__(self):
        if self.definition is not None:
            return '<Unit %s %s >' % (self.definition, self.symbol)
        return '<Unit %s %s >' % (self.symbol, self.name)

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
    system_xml = pkg_resources.resource_string(systems.__name__, 'udunits2-base.xml')
    root = ET.fromstring(system_xml)
    for unit_tag in root.findall('unit'):
        unit = Unit.fromtag(unit_tag)
        print unit

    prefix_xml = pkg_resources.resource_string(systems.__name__, 'udunits2-prefixes.xml')
    root = ET.fromstring(prefix_xml)
    for prefix_tag in root.findall('prefix'):
        prefix = Prefix.fromtag(prefix_tag)
        print prefix
        print '    ' + ', '.join(prefix.symbols)

    common_xml = pkg_resources.resource_string(systems.__name__, 'udunits2-common.xml')
    root = ET.fromstring(common_xml)
    for unit_tag in root.findall('unit'):
        unit = Unit.fromtag(unit_tag)
        print unit



if __name__ == '__main__':
    idea()

