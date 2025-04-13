import ply.lex as lex

# Palabras reservadas
reserved = {
    'if': 'IF', 'else': 'ELSE', 'end': 'END', 'do': 'DO', 'while': 'WHILE', 'switch': 'SWITCH',
    'case': 'CASE', 'int': 'INT', 'float': 'FLOAT', 'main': 'MAIN', 'cin': 'CIN', 'cout': 'COUT'
}

# Lista de tokens
tokens = [
    'NUMBER', 'REAL', 'ID', 'COMMENT', 'INVALID_REAL', 'INVALID_ID', 'AT',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MODULO', 'POWER', 'INCREMENT', 'DECREMENT',
    'LT', 'LE', 'GT', 'GE', 'NE', 'EQ',
    'AND', 'OR', 'NOT',
    'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'COMMA', 'SEMICOLON', 'ASSIGN'
] + list(reserved.values())

# Expresiones regulares para tokens simples
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_MODULO = r'%'
t_POWER = r'\^'
t_INCREMENT = r'\+\+'
t_DECREMENT = r'--'
t_LT = r'<'
t_LE = r'<='
t_GT = r'>'
t_GE = r'>='
t_NE = r'!='
t_EQ = r'=='
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
t_AT = r'@'

def t_REAL(t):
    r'[-+]?[0-9]+\.[0-9]+'
    if ".." in t.value:
        t.type = 'INVALID_REAL'
    else:
        t.value = float(t.value)
    return t

def t_NUMBER(t):
    r'[-+]?[0-9]+(?![\.0-9])'
    t.value = int(t.value)
    return t

def t_INVALID_REAL(t):
    r'[-+]?[0-9]+\.[a-zA-Z_]+'
    t.type = 'INVALID_REAL'
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9@]*'
    if '@' in t.value:
        t.type = 'INVALID_ID'
    elif t.value in reserved:
        t.type = reserved[t.value]
    else:
        t.type = 'ID'
    return t

def t_COMMENT(t):
    r'//.*|/\*[\s\S]*?\*/'
    pass  # Ignorar comentarios

t_ignore = ' \t'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    pass

def t_error(t):
    print(f"Carácter ilegal '{t.value[0]}' en línea {t.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()

def test_lexer(input_text):
    lexer.input(input_text)
    return [tok for tok in lexer]

if __name__ == "__main__":
    code = """
    int x = 5;
    float y = 3.14;
    if (x > y) {
        cout << "Mayor";
    }
    34.34.34.34
    sum@r
    int myVar = 10;
    32.algo
    """
    tokens = test_lexer(code)
    for tok in tokens:
        print(tok)