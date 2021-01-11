from sly import Lexer


class CompilerLexer(Lexer):
    tokens = {DECLARE, BEGIN, END, ASSIGN, IF, THEN, ELSE, ENDIF, WHILE, DO, ENDWHILE, REPEAT, UNTIL, FOR, FROM, TO,
              ENDFOR, DOWNTO, READ, WRITE, ADDITION, SUBTRACTION, MULTIPLICATION, DIVIDE, MODULO, EQUAL, NOTEQUAL,
              LOWERTHAN, GREATERTHAN, LOWEREQUALTHAN, GREATEREQUALTHAN,
              SEMICOLON, COLON, COMMA, LEFTBRACKET, RIGHTBRACKET, PIDENTIFIER, NUMBER}

    DECLARE = r'DECLARE'
    BEGIN = r'BEGIN'
    END = r'END'
    ASSIGN = r':='
    IF = r'IF'
    THEN = r'THEN'
    ELSE = r'ELSE'
    ENDIF = r'ENDIF'
    WHILE = r'WHILE'
    DO = r'DO'
    ENDWHILE = r'ENDWHILE'
    REPEAT = r'REPEAT'
    UNTIL = r'UNTIL'
    FOR = r'FOR'
    FROM = r'FROM'
    TO = r'TO'
    ENDFOR = r'ENDFOR'
    DOWNTO = r'DOWNTO'
    READ = r'READ'
    WRITE = r'WRITE'
    ADDITION = r'\+'
    SUBTRACTION = r'\-'
    MULTIPLICATION = r'\*'
    DIVIDE = r'\/'
    MODULO = r'\%'
    EQUAL = r'='
    NOTEQUAL = r'!='
    LOWERTHAN = r'<'
    GREATERTHAN = r'>'
    LOWEREQUALTHAN = r'<='
    GREATEREQUALTHAN = r'>='
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
        raise Exception("Syntax error")
