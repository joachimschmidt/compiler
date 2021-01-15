from sly import Lexer
from compiler_exception import CompilerException

class CompilerLexer(Lexer):
    tokens = {DECLARE, BEGIN, END, ASSIGN, IF, THEN, ELSE, ENDIF, WHILE, DO, ENDWHILE, REPEAT, UNTIL, FOR, FROM, TO,
              ENDFOR, DOWNTO, READ, WRITE, ADDITION, SUBTRACTION, MULTIPLICATION, DIVIDE, MODULO, EQUAL, NOTEQUAL,
              LOWERTHAN, GREATERTHAN, LOWEREQUALTHAN, GREATEREQUALTHAN,
              SEMICOLON, COLON, COMMA, LEFTBRACKET, RIGHTBRACKET, PIDENTIFIER, NUMBER}

    DECLARE = r'DECLARE'
    BEGIN = r'BEGIN'
    ASSIGN = r':='
    IF = r'IF'
    THEN = r'THEN'
    ELSE = r'ELSE'
    ENDIF = r'ENDIF'
    WHILE = r'WHILE'
    ENDWHILE = r'ENDWHILE'
    REPEAT = r'REPEAT'
    UNTIL = r'UNTIL'
    FOR = r'FOR'
    FROM = r'FROM'
    ENDFOR = r'ENDFOR'
    END = r'END'
    DOWNTO = r'DOWNTO'
    DO = r'DO'
    TO = r'TO'

    READ = r'READ'
    WRITE = r'WRITE'
    ADDITION = r'\+'
    SUBTRACTION = r'\-'
    MULTIPLICATION = r'\*'
    DIVIDE = r'\/'
    MODULO = r'\%'
    NOTEQUAL = r'!='
    EQUAL = r'='
    LOWEREQUALTHAN = r'<='
    GREATEREQUALTHAN = r'>='
    LOWERTHAN = r'<'
    GREATERTHAN = r'>'
    SEMICOLON = r';'
    COLON = r':'
    COMMA = r','
    LEFTBRACKET = r'\('
    RIGHTBRACKET = r'\)'
    PIDENTIFIER = r'[_a-z]+'

    @_(r'\d+')
    def NUMBER(self, t):
        t.value = int(t.value)
        return t

    ignore = " \t\r"
    ignore_comment = r'\[[^\]]*\]'

    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += len(t.value)

    def error(self, t):
        raise CompilerException("Syntax error")
