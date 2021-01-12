from sly import Parser

from lexer import CompilerLexer
from variable import *


class CompilerPreParser(Parser):
    tokens = CompilerLexer.tokens
    variables = {}

    def declare_variable(self, name):
        if name in self.variables.keys():
            raise Exception("{} already defined".format(name))
        new_variable = Identifier(name, None)
        self.variables[name] = new_variable

    def declare_iterator(self, name):
        if name in self.variables.keys() and not isinstance(self.variables[name], Iterator):
            raise Exception("{} cannot be used as an iterator. Iterator is local for each loop".format(name))
        if name not in self.variables.keys():
            new_variable = Iterator(name, None)
            self.variables[name] = new_variable

    def count_variable(self, variable):
        if variable not in self.variables.keys():
            raise Exception("{} not declared".format(variable))
        elif not isinstance(self.variables[variable], Iterator):
            self.variables[variable].occurrences += 1

    def count_number(self, number, in_write=False):
        if number not in self.variables.keys():
            new_variable = Number(number, number, None)
            new_variable.occurrences = 1
            self.variables[number] = new_variable
        else:
            self.variables[number].occurrences += 1
        if in_write:
            self.variables[number].in_write = True

    def declare_array(self, name, start, end):
        variable = Array(name, start, end, 0)
        self.variables[name] = variable

    '''
    program
    '''

    @_('DECLARE declarations BEGIN commands END')
    def program(self, p):
        return self.variables

    @_('BEGIN commands END')
    def program(self, p):
        return self.variables

    '''
    declarations
    '''

    @_('declarations COMMA PIDENTIFIER')
    def declarations(self, p):
        self.declare_variable(p[2])

    @_('declarations COMMA PIDENTIFIER LEFTBRACKET NUMBER COLON NUMBER RIGHTBRACKET')
    def declarations(self, p):
        self.declare_array(p[2], p[4], p[6])

    @_('PIDENTIFIER')
    def declarations(self, p):
        self.declare_variable(p[0])

    @_('PIDENTIFIER LEFTBRACKET NUMBER COLON NUMBER RIGHTBRACKET')
    def declarations(self, p):
        self.declare_array(p[0], p[2], p[4])

    '''
    commands
    '''

    @_('commands command')
    def commands(self, p):
        pass

    @_('command')
    def commands(self, p):
        pass

    '''
    command
    '''

    @_('identifier ASSIGN expression SEMICOLON')
    def command(self, p):
        pass

    @_('IF condition THEN commands ELSE begin_else_if commands ENDIF')
    def command(self, p):
        pass

    @_('')
    def begin_else_if(self, p):
        pass

    @_('IF condition THEN commands ENDIF')
    def command(self, p):
        pass

    @_('WHILE begin_while condition DO commands ENDWHILE')
    def command(self, p):
        pass

    @_('REPEAT begin_while commands UNTIL condition SEMICOLON')
    def command(self, p):
        pass

    @_('')
    def begin_while(self, p):
        pass

    @_('FOR PIDENTIFIER FROM value TO value DO begin_for_to commands ENDFOR')
    def command(self, p):
        pass

    @_('')
    def begin_for_to(self, p):
        self.declare_iterator(p[-6])

    @_('FOR PIDENTIFIER FROM value DOWNTO value DO begin_for_downto commands ENDFOR')
    def command(self, p):
        pass

    @_('')
    def begin_for_downto(self, p):
        self.declare_iterator(p[-6])

    @_('READ identifier SEMICOLON')
    def command(self, p):
        pass

    @_('WRITE value SEMICOLON')
    def command(self, p):
        if isinstance(p[1], Number):
            self.variables[p[1].name].in_write = True

    '''
    expression
    '''

    @_('value')
    def expression(self, p):
        pass

    @_('value ADDITION value',
       'value SUBTRACTION value',
       'value MULTIPLICATION value',
       'value DIVIDE value',
       'value MODULO value')
    def expression(self, p):
        pass

    @_('value EQUAL value',
       'value NOTEQUAL value',
       'value LOWERTHAN value',
       'value GREATERTHAN value',
       'value LOWEREQUALTHAN value',
       'value GREATEREQUALTHAN value')
    def condition(self, p):
        pass

    '''
       value
    '''

    @_('NUMBER')
    def value(self, p):
        self.count_number(p[0])
        return self.variables[p[0]]

    @_('identifier')
    def value(self, p):
        return p[0]

    '''
       identifier
    '''

    @_('PIDENTIFIER')
    def identifier(self, p):
        self.count_variable(p[0])
        return self.variables[p[0]]

    @_('PIDENTIFIER LEFTBRACKET PIDENTIFIER RIGHTBRACKET')
    def identifier(self, p):
        self.count_variable(p[0])
        self.count_variable(p[2])

    @_('PIDENTIFIER LEFTBRACKET NUMBER RIGHTBRACKET')
    def identifier(self, p):
        self.count_variable(p[0])

    def error(self, token):
        raise Exception("Syntax error in grammar in preparsing {}")
