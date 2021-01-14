from sly import Parser

from code_generator import CodeGenerator
from compiler_exception import CompilerException
from lexer import CompilerLexer


class CompilerParser(Parser):
    def __init__(self, generator):
        if isinstance(generator, CodeGenerator):
            self.generator = generator

    tokens = CompilerLexer.tokens
    precedence = (
        ('left', ADDITION, SUBTRACTION),
        ('left', MULTIPLICATION, DIVIDE),
    )
    '''
    program
    '''

    @_('DECLARE declarations BEGIN commands END')
    def program(self, p):
        self.generator.end_program()

    @_('BEGIN commands END')
    def program(self, p):
        self.generator.end_program()

    '''
    declarations
    '''

    @_('declarations COMMA PIDENTIFIER')
    def declarations(self, p):
        pass

    @_('declarations COMMA PIDENTIFIER LEFTBRACKET NUMBER COLON NUMBER RIGHTBRACKET')
    def declarations(self, p):
        self.generator.check_array_declaration(p[2], p[4], p[6], p.lineno)

    @_('PIDENTIFIER')
    def declarations(self, p):
        pass

    @_('PIDENTIFIER LEFTBRACKET NUMBER COLON NUMBER RIGHTBRACKET')
    def declarations(self, p):
        self.generator.check_array_declaration(p[0], p[2], p[4], p.lineno)

    '''
    commands
    '''

    @_('commands command',
       'command')
    def commands(self, p):
        pass

    '''
    command
    '''

    @_('identifier ASSIGN expression SEMICOLON')
    def command(self, p):
        self.generator.c_assign(p[0], p.lineno)

    @_('IF condition THEN commands ELSE begin_else_if commands ENDIF')
    def command(self, p):
        self.generator.c_if()

    @_('')
    def begin_else_if(self, p):
        self.generator.c_if_else()

    @_('IF condition THEN commands ENDIF')
    def command(self, p):
        self.generator.c_if()

    @_('WHILE begin_while condition DO commands ENDWHILE')
    def command(self, p):
        self.generator.c_exit_while()

    @_('REPEAT begin_while commands UNTIL condition SEMICOLON')
    def command(self, p):
        self.generator.c_exit_repeat()

    @_('')
    def begin_while(self, p):
        self.generator.c_while()

    @_('FOR PIDENTIFIER FROM value TO value DO begin_for_to commands ENDFOR')
    def command(self, p):
        self.generator.c_exit_for_to()

    @_('')
    def begin_for_to(self, p):
        self.generator.c_for_to(p[-6], p[-4], p[-2], p.lineno)

    @_('FOR PIDENTIFIER FROM value DOWNTO value DO begin_for_down_to commands ENDFOR')
    def command(self, p):
        self.generator.c_exit_for_down_to()

    @_('')
    def begin_for_down_to(self, p):
        self.generator.c_for_to(p[-6], p[-4], p[-2], p.lineno)

    @_('READ identifier SEMICOLON')
    def command(self, p):
        self.generator.c_read(p[1], p.lineno)

    @_('WRITE value SEMICOLON')
    def command(self, p):
        self.generator.c_write(p[1], p.lineno)

    '''
    expression
    '''

    @_('value')
    def expression(self, p):
        self.generator.e_value(p.value, 0)

    @_('value ADDITION value',
       'value SUBTRACTION value',
       'value MULTIPLICATION value',
       'value DIVIDE value',
       'value MODULO value')
    def expression(self, p):
        self.generator.e_operation(p[0], p[2], p[1], p.lineno)

    @_('value EQUAL value',
       'value NOTEQUAL value',
       'value LOWERTHAN value',
       'value GREATERTHAN value',
       'value LOWEREQUALTHAN value',
       'value GREATEREQUALTHAN value')
    def condition(self, p):
        self.generator.condition(p[0], p[2], p[1], p.lineno)

    '''
       value
    '''

    @_('NUMBER')
    def value(self, p):
        return p.NUMBER

    @_('identifier')
    def value(self, p):
        return p.identifier

    '''
       identifier
    '''

    @_('PIDENTIFIER')
    def identifier(self, p):
        self.generator.check_identifier_reference(p[0], p.lineno)
        return p.PIDENTIFIER

    @_('PIDENTIFIER LEFTBRACKET PIDENTIFIER RIGHTBRACKET')
    def identifier(self, p):
        return self.generator.check_array_reference_by_identifier(p[0], p[2], p.lineno)

    @_('PIDENTIFIER LEFTBRACKET NUMBER RIGHTBRACKET')
    def identifier(self, p):
        return self.generator.check_array_reference_by_number(p[0], p[2], p.lineno)

    def error(self, token):
        raise CompilerException("Syntax error in grammar", token.lineno)
