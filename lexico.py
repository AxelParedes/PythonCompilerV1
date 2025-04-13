import ply.lex as lex

reserved = {
    'if': 'IF', 'else': 'ELSE', 'end': 'END', 'do': 'DO', 'while': 'WHILE', 
    'switch': 'SWITCH', 'case': 'CASE', 'int': 'INT', 'float': 'FLOAT', 
    'main': 'MAIN', 'cin': 'CIN', 'cout': 'COUT', 'then': 'THEN', 'until': 'UNTIL'
}

tokens = [
    'NUMBER', 'REAL', 'ID', 'COMMENT', 'INVALID_ID', 'INVALID_REAL', 'INVALID_COMMENT',
    'ERROR', 'STRING', 'CHAR', 'BOOL', 'TRUE', 'FALSE',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MODULO', 'POWER', 
    'LT', 'LE', 'GT', 'GE', 'NE', 'EQ', 'EEQ',
    'AND', 'OR', 'NOT',
    'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'COMMA', 'SEMICOLON', 'ASSIGN',
    'INCREMENT', 'DECREMENT'
] + list(reserved.values())

# Tokens válidos
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_MODULO = r'%'
t_POWER = r'\^'
t_LT = r'<'
t_LE = r'<='
t_GT = r'>'
t_GE = r'>='
t_NE = r'!='
t_EQ = r'='
t_EEQ = r'=='
t_AND = r'&&'
t_OR = r'\|\|'
t_NOT = r'!'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_COMMA = r','
t_SEMICOLON = r';'
t_ASSIGN = r'='
t_INCREMENT = r'\+\+'
t_DECREMENT = r'--'

def t_ERROR_MIXED_REAL(t):
    r'\d+\.[a-zA-Z_]+'
    t.type = 'ERROR'
    return t

def t_REAL(t):
    r'\d+\.\d+(\.\d+)*'
    if t.value.count('.') > 1:
        t.type = 'ERROR'
        t.value = t.value
    else:
        t.value = float(t.value)
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_@]*'
    if t.value in reserved:
        t.type = reserved[t.value]
    elif '@' in t.value:
        t.type = 'ERROR'
    return t



def t_COMMENT(t):
    r'//.*|/\*[\s\S]*?\*/'
    pass

t_ignore = ' \t'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    # Solo caracteres realmente inválidos
    invalid_chars = {'@', '$', '¿', '?', '¡', '°', '¬', '~'}
    if t.value[0] in invalid_chars:
        error_token = lex.LexToken()
        error_token.type = 'ERROR'
        error_token.value = t.value[0]
        error_token.lineno = t.lineno
        error_token.lexpos = t.lexpos
        t.lexer.skip(1)
        return error_token
    t.lexer.skip(1)

lexer = lex.lex()

def test_lexer(input_text):
    lexer.input(input_text)
    return list(lexer)