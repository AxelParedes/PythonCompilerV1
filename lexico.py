import ply.lex as lex

reserved = {
<<<<<<< Updated upstream
    'if': 'IF', 'else': 'ELSE', 'end': 'END', 'do': 'DO', 'while': 'WHILE',
    'switch': 'SWITCH', 'case': 'CASE', 'int': 'INT', 'float': 'FLOAT',
    'main': 'MAIN', 'cin': 'CIN', 'cout': 'COUT', 'then': 'THEN', 'until': 'UNTIL'
}

tokens = [
    'NUMBER', 'REAL', 'ID', 'ERROR',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MODULO', 'POWER',
=======
    'if': 'IF', 'else': 'ELSE', 'end': 'END', 'do': 'DO', 'while': 'WHILE', 
    'switch': 'SWITCH', 'case': 'CASE', 'int': 'INT', 'float': 'FLOAT', 
    'main': 'MAIN', 'cin': 'CIN', 'cout': 'COUT', 'then': 'THEN', 'until': 'UNTIL',
    'true': 'TRUE', 'false': 'FALSE', 'bool': 'BOOL', 'string': 'STRING', 'then': 'THEN',
    'until': 'UNTIL', 'for': 'FOR', 'return': 'RETURN', 'break': 'BREAK',
}

tokens = [
    'NUMBER', 'REAL', 'ID', 'COMMENT', 'CADENA',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MODULO', 'POWER', 
>>>>>>> Stashed changes
    'LT', 'LE', 'GT', 'GE', 'NE', 'EQ', 'EEQ',
    'AND', 'OR', 'NOT',
    'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'COMMA', 'SEMICOLON',
    'INCREMENT', 'DECREMENT', 'LSHIFT', 'RSHIFT', 'STRING', 'BOOL', 'TRUE', 'FALSE', 'ASSIGN'
] + list(reserved.values())

<<<<<<< Updated upstream
# Operadores y símbolos
=======
# Tokens simples
>>>>>>> Stashed changes
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
t_INCREMENT = r'\+\+'
t_DECREMENT = r'--'
t_LSHIFT = r'<<'
t_RSHIFT = r'>>'
t_STRING = r'\".*?\"'
t_ASSIGN = r'='  

<<<<<<< Updated upstream
# Tokens numéricos
def t_REAL(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_ERROR_REAL(t):
    r'\d+\.(?=\D|$)'
    # Ej: 32. → ERROR
    t.type = 'ERROR'
=======
def t_CADENA(t):
    r'\"([^\\\n]|(\\.))*?\"'
    t.value = t.value[1:-1]  # Remover las comillas
    return t

def t_BOOL(t):
    r'\b(true|false)\b'
    t.value = True if t.value == 'true' else False
    t.type = 'TRUE' if t.value else 'FALSE'
    return t

def t_REAL(t):
    r'\d+\.\d+'
    t.value = float(t.value)
>>>>>>> Stashed changes
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Identificadores y reservadas
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
<<<<<<< Updated upstream
    if t.value in reserved:
        t.type = reserved[t.value]
    return t

# Captura @ como error separado
def t_ERROR_AT(t):
    r'@'
    t.type = 'ERROR'
    return t

# Comentarios (ignorados)
=======
    t.type = reserved.get(t.value, 'ID')
    return t

>>>>>>> Stashed changes
def t_COMMENT(t):
    r'//.*|/\*[\s\S]*?\*/'
    pass

# Ignorar espacios y tabs
t_ignore = ' \t'

# Contador de líneas
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Caracteres inválidos
def t_error(t):
<<<<<<< Updated upstream
    t.type = 'ERROR'
    t.value = t.value[0]
=======
    print(f"Carácter ilegal '{t.value[0]}' en la línea {t.lineno}")
>>>>>>> Stashed changes
    t.lexer.skip(1)
    return t

# Construcción del lexer
lexer = lex.lex()

# Función de prueba
def test_lexer(input_text):
    lexer.input(input_text)
    tokens = []
<<<<<<< Updated upstream
    while True:
        tok = lexer.token()
        if not tok:
            break
        tokens.append(tok)
    return tokens

# Ejemplo de prueba
if __name__ == "__main__":
    entrada = '''main sum@r 3.14+main)if{32.algo
34.34.34.34
'''
    salida = test_lexer(entrada)
    print("TOKENS DETECTADOS:")
    for tok in salida:
        print(f"{tok.type:<10} {tok.value:<10} linea {tok.lineno} pos {tok.lexpos}")
=======
    for tok in lexer:
        tokens.append(tok)
    return tokens
>>>>>>> Stashed changes
