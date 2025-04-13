import ply.yacc as yacc
from lexico import tokens, lexer

# Definición de la gramática
def p_expression_plus(p):
    'expression : expression PLUS term'
    p[0] = p[1] + p[3]

def p_expression_minus(p):
    'expression : expression MINUS term'
    p[0] = p[1] - p[3]

def p_expression_term(p):
    'expression : term'
    p[0] = p[1]

def p_term_times(p):
    'term : term TIMES factor'
    p[0] = p[1] * p[3]

def p_term_div(p):
    'term : term DIVIDE factor'
    if p[3] == 0:
        raise ValueError("División por cero")
    p[0] = p[1] / p[3]

def p_term_factor(p):
    'term : factor'
    p[0] = p[1]

def p_factor_num(p):
    'factor : NUMBER'
    p[0] = p[1]

def p_factor_expr(p):
    'factor : LPAREN expression RPAREN'
    p[0] = p[2]

def p_factor_id(p):
    'factor : ID'
    # Aquí podrías buscar el valor de la variable en la tabla de símbolos
    p[0] = 0  # Valor por defecto para identificadores no declarados

# Manejo de errores sintácticos
def p_error(p):
    print(f"Error de sintaxis en '{p.value}'")

# Construir el parser
parser = yacc.yacc()

# Función para probar el parser
def test_parser(input_text):
    return parser.parse(input_text)

# Prueba del parser
if __name__ == "__main__":
    data = "3 + 5 * (10 - 4)"
    result = test_parser(data)
    print(f"Resultado: {result}")