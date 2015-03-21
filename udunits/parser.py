#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
udunits/parser.py

Parser logic for parsing out units and operators
'''
from pyparsing import ParseException, Regex, quotedString, nums, Literal, Combine, ZeroOrMore
from pyparsing import CaselessLiteral, MatchFirst, removeQuotes, Optional, Word, White, Or
from pyparsing import OneOrMore

class Parser(object):
    def __init__(self):
        #----------------------------------------
        # number       ::= [0-9]+
        # point        ::= .
        # exp          ::= [eE]
        # integer      ::= [-]<number>
        # float_number ::= <integer>[<point>[<number]][<exp><integer>][f]
        # unit_symbol  ::= [a-zA-Z]+[0-9]?
        #----------------------------------------
        number = Word(nums)
        point = Literal('.')
        exp = CaselessLiteral('E')
        integer = Combine(Optional('-') + number)
        float_number = Combine(integer + Optional(point + Optional(number)) + Optional(exp + integer))
        degree_symbol = Literal(u'\u00b0')
        prime = Literal("'") ^ Literal(u'\u2032')
        double_prime = Literal('"') ^ Literal(u'\u2033')
        unit_symbol = Regex(r'[a-zA-Z]+[a-zA-Z_]*[\^]?[0-9]*') ^ degree_symbol ^ prime ^ double_prime
        #----------------------------------------
        # per              ::= /
        # unit_combination ::= <unit_symbol> [[/ ] <unit_symbol>]*
        # unit             ::= [<float_number>] <unit_combination>
        #----------------------------------------
        per = Literal('/')
        mult = Literal('.')
        at = Literal('@')
        operators = per ^ mult ^ at
        unit_or_float = unit_symbol ^ float_number
        operation = unit_or_float + Optional(operators) + unit_or_float
        expression = OneOrMore(operation)
        parenthetical_expression = '(' + expression + ')'
        ordered_expression = parenthetical_expression ^ expression ^ unit_or_float
        equation = ordered_expression + Optional(per) + ordered_expression

        self.sentence = equation ^ ordered_expression ^ unit_or_float


    def tokenize(self, statement):
        tokens = self.sentence.parseString(statement)
        return tokens


def check_statement(statement):
    parser = Parser()
    tokens = parser.tokenize(statement)
    print statement + ':' + repr(tokens)

def test():
    statements = [
        '60 s',
        '60 min',
        '24 h',
        '3.141592653589793238462643383279',
        '(pi/180)',
        'pi 180',
        '180 pi',
        '(pi/180) rad',
        u'°/60',
        "'/60",
        'dm^3',
        '1000 kg',
        '1.60217733e-19 J',
        '1.6605402e-27 kg',
        '1.495979e11 m',
        '1852 m',
        'nautical_mile/hour',
        '1e-10 m',
        'dam^2',
        '100 are',
        '100 fm^2',
        '1000 hPa',
        'cm/s^2',
        '3.7e10 Bq',
        '2.58e-4 C/kg',
        '0.01 sievert',
        'm.kg/s^2',
        'K @ 273.15',
    ]

    for statement in statements:
        check_statement(statement)


if __name__ == '__main__':
    test()




