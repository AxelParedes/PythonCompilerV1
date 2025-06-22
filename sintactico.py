import ply.yacc as yacc
from lexico import tokens, lexer

# Definición de nodos del AST
# Cada nodo tiene un tipo, una lista de hijos, un valor opcional, y puede tener información de línea y posición léxica
# También puede tener un operador si es relevante (por ejemplo, en expresiones) 


class ASTNode:
    def __init__(self, type, children=None, value=None, lineno=None, lexpos=None, op=None):
        self.type = type
        self.children = children if children is not None else []
        self.value = value
        self.lineno = lineno
        self.lexpos = lexpos
        self.op = op

    def __repr__(self):
        if self.op:
            return f"{self.type} ({self.op})"
        return f"{self.type}: {self.value}" if self.value else self.type

# Precedencia de operadores
precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('right', 'NOT'),
    ('nonassoc', 'LT', 'LE', 'GT', 'GE', 'EEQ', 'NE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MODULO'),
    ('left', 'LSHIFT', 'RSHIFT')
)

def p_programa(p):
    'programa : MAIN LBRACE lista_declaraciones RBRACE'
    p[0] = ASTNode('programa', children=[p[3]], lineno=p.lineno(1), lexpos=p.lexpos(1))

def p_lista_declaraciones(p):
    '''lista_declaraciones : lista_declaraciones declaracion
                          | declaracion'''
    if len(p) == 3:
        p[0] = ASTNode('lista_declaraciones', children=[p[1], p[2]], lineno=p.lineno(1), lexpos=p.lexpos(1))
    else:
        p[0] = ASTNode('lista_declaraciones', children=[p[1]], lineno=p.lineno(1), lexpos=p.lexpos(1))
        
def p_declaracion(p):
    '''declaracion : declaracion_variable
                   | sentencia
                   | error SEMICOLON'''  # Manejo de errores no fatales
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ASTNode('error', value=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))
        print(f"Error recuperado en línea {p.lineno(1)}")

def p_declaracion_variable(p):
    '''declaracion_variable : tipo lista_ids SEMICOLON'''
    p[0] = {
        'type': 'declaration',
        'var_type': p[1],
        'variables': p[2],
        'lineno': p.lineno(1)
    }    
    
def p_lista_ids(p):
    '''lista_ids : ID
                | lista_ids COMMA ID'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]
        
def p_tipo(p):
    '''tipo : INT
            | FLOAT
            | BOOL'''  # Asegúrate que BOOL esté definido como token
    p[0] = ASTNode('tipo', value=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))

def p_lista_sentencias(p):
    '''lista_sentencias : sentencia lista_sentencias
                       | sentencia'''
    if len(p) == 3:
        p[0] = ASTNode('lista_sentencias', children=[p[1], p[2]], lineno=p.lineno(1), lexpos=p.lexpos(1))
    else:
        p[0] = ASTNode('lista_sentencias', children=[p[1]], lineno=p.lineno(1), lexpos=p.lexpos(1))
        
def p_sentencia(p):
    '''sentencia : asignacion
                 | seleccion
                 | iteracion
                 | repeticion
                 | sent_in
                 | sent_out
                 | incremento
                 | decremento
                 | error'''  # Manejo de errores en sentencias
    p[0] = p[1]

def p_asignacion(p):
    'asignacion : ID EQ expresion SEMICOLON'
    p[0] = ASTNode('asignacion', children=[p[3]], value=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))
    
def p_sent_expresion(p):
    '''sent_expresion : expresion SEMICOLON
                      | SEMICOLON'''
    if len(p) == 3:
        p[0] = ASTNode('sent_expresion', children=[p[1]], lineno=p.lineno(2), lexpos=p.lexpos(2))
    else:
        p[0] = ASTNode('sent_expresion', lineno=p.lineno(1), lexpos=p.lexpos(1))

def p_seleccion(p):
    '''seleccion : IF expresion THEN LBRACE lista_sentencias RBRACE END
                 | IF expresion THEN LBRACE lista_sentencias RBRACE ELSE LBRACE lista_sentencias RBRACE END'''
    node = {
        'type': 'if-then',
        'condition': p[2],
        'then_body': p[5],
        'lineno': p.lineno(1)
    }
    if len(p) > 8:
        node['type'] = 'if-then-else'
        node['else_body'] = p[9]
    p[0] = node
    
def p_incremento(p):
    'incremento : ID INCREMENT SEMICOLON'
    p[0] = ASTNode('incremento', value=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))
    
def p_decremento(p):
    'decremento : ID DECREMENT SEMICOLON'
    p[0] = ASTNode('decremento', value=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))
            
def p_iteracion(p):
    'iteracion : WHILE expresion LBRACE lista_sentencias RBRACE END'
    p[0] = ASTNode('while', children=[p[2], p[4]], lineno=p.lineno(1), lexpos=p.lexpos(1))
    
def p_repeticion(p):
    '''repeticion : DO LBRACE lista_sentencias RBRACE WHILE expresion SEMICOLON
                 | DO LBRACE lista_sentencias RBRACE UNTIL expresion SEMICOLON'''
    p[0] = {
        'type': 'do-while' if p[5] == 'while' else 'do-until',
        'body': p[3],
        'condition': p[6],
        'lineno': p.lineno(1)
    }
    
def p_sent_in(p):
    'sent_in : CIN RSHIFT ID SEMICOLON'
    p[0] = ASTNode('sent_in', value=p[3], lineno=p.lineno(1), lexpos=p.lexpos(1))

def p_sent_out(p):
    '''sent_out : COUT LSHIFT CADENA SEMICOLON
                | COUT LSHIFT expresion SEMICOLON
                | COUT LSHIFT CADENA LSHIFT expresion SEMICOLON
                | COUT LSHIFT expresion LSHIFT CADENA SEMICOLON'''
    if len(p) == 5:
        p[0] = ASTNode('sent_out', children=[p[3]], lineno=p.lineno(1), lexpos=p.lexpos(1))
    else:
        p[0] = ASTNode('sent_out', children=[p[3], p[5]], lineno=p.lineno(1), lexpos=p.lexpos(1))

def p_expresion(p):
    '''expresion : expresion AND expresion
                 | expresion OR expresion
                 | NOT expresion
                 | expresion_relacional'''
    if len(p) == 4:
        p[0] = ASTNode('expresion_logica', children=[p[1], p[3]], op=p[2], lineno=p.lineno(2), lexpos=p.lexpos(2))
    elif len(p) == 3:
        p[0] = ASTNode('expresion_logica', children=[p[2]], op=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))
    else:
        p[0] = p[1]

def p_expresion_relacional(p):
    '''expresion_relacional : expresion_simple
                            | expresion_simple rel_op expresion_simple'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ASTNode('expresion_relacional', children=[p[1], p[3]], op=p[2], lineno=p.lineno(2), lexpos=p.lexpos(2))
  
def p_expresion_simple(p):
    '''expresion_simple : termino
                       | expresion_simple suma_op termino'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ASTNode('expresion_binaria', 
                      children=[p[1], p[3]], 
                      op=p[2],
                      lineno=p.lineno(2), 
                      lexpos=p.lexpos(2))
def p_rel_op(p):
    '''rel_op : LT
              | LE
              | GT
              | GE
              | NE
              | EEQ'''
    p[0] = p[1]

def p_expresion_simple(p):
    '''expresion_simple : termino
                        | expresion_simple suma_op termino'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ASTNode('expresion_suma', children=[p[1], p[3]], op=p[2], lineno=p.lineno(2), lexpos=p.lexpos(2))

def p_suma_op(p):
    '''suma_op : PLUS
               | MINUS'''
    p[0] = p[1]

def p_termino(p):
    '''termino : factor
               | termino mult_op factor'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ASTNode('expresion_mult', children=[p[1], p[3]], op=p[2], lineno=p.lineno(2), lexpos=p.lexpos(2))

def p_mult_op(p):
    '''mult_op : TIMES
               | DIVIDE
               | MODULO'''
    p[0] = p[1]

def p_factor(p):
    '''factor : componente
              | PLUS factor
              | MINUS factor'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ASTNode('expresion_unaria', children=[p[2]], op=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))

def p_componente(p):
    '''componente : LPAREN expresion RPAREN
                  | NUMBER
                  | REAL
                  | ID
                  | TRUE
                  | FALSE
                  | STRING'''  # Asegúrate que STRING esté definido
    if len(p) == 4:
        p[0] = p[2]
    else:
        p[0] = ASTNode('componente', value=p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))
def p_error(p):
    if p:
        error_msg = f"Error de sintaxis en línea {p.lineno}, columna {find_column(lexer, p.lexpos)}:\n"
        error_msg += f"Token inesperado: '{p.value}'\n"
        
        # Obtener el contexto de la línea
        input_lines = lexer.lexdata.split('\n')
        if 0 <= p.lineno-1 < len(input_lines):
            error_msg += f"Contexto: {input_lines[p.lineno-1]}\n"
            error_msg += " "*(find_column(lexer, p.lexpos)-1) + "^\n"
        
        if not hasattr(parser, 'errors'):
            parser.errors = []
        parser.errors.append(error_msg)
        
        # Recuperación: saltar hasta el siguiente punto y coma
        parser.errok()
        return parser.token()
    else:
        error_msg = "Error de sintaxis: Fin de archivo inesperado"
        if hasattr(parser, 'errors'):
            parser.errors.append(error_msg)

def parse_code(input_text):
    parser.errors = []
    lexer.input(input_text)
    try:
        ast = parser.parse(input_text, lexer=lexer, debug=False)
        return {
            'ast': ast,
            'errors': parser.errors,
            'success': len(parser.errors) == 0
        }
    except Exception as e:
        error_msg = f"Error fatal durante el análisis: {str(e)}"
        parser.errors.append(error_msg)
        return {
            'ast': None,
            'errors': parser.errors,
            'success': False
        }
        
def generate_ast_view(node, level=0):
    """Genera la vista jerárquica del AST"""
    indent = "    " * level
    result = ""
    
    if isinstance(node, dict):
        if node['type'] == 'programa':
            result += f"{indent}Raíz: programa\n"
            for child in node['body']:
                result += generate_ast_view(child, level+1)
                
        elif node['type'] == 'declaration':
            result += f"{indent}- {node['var_type']}\n"
            for var in node['variables']:
                result += f"{indent}    - {var}\n"
                
        elif node['type'] == 'if-then':
            result += f"{indent}- if-then\n"
            result += generate_ast_view(node['condition'], level+1)
            result += generate_ast_view(node['body'], level+1)
            
        elif node['type'] == 'asignacion':
            result += f"{indent}- =\n"
            result += f"{indent}    - {node['left']}\n"
            result += generate_ast_view(node['right'], level+2)
            
        elif node['type'] == 'while':
            result += f"{indent}- while\n"
            result += generate_ast_view(node['condition'], level+1)
            result += generate_ast_view(node['body'], level+1)
        elif node['type'] == 'sent_out':
            result += f"{indent}- sent_out\n"
            for child in node['children']:
                result += generate_ast_view(child, level+1)
        elif node['type'] == 'sent_in':
            result += f"{indent}- sent_in\n"
            result += f"{indent}    - {node['value']}\n"
        elif node['type'] == 'sent_expresion':
            result += f"{indent}- sent_expresion\n"
            if node['children']:
                for child in node['children']:
                    result += generate_ast_view(child, level+1)
        elif node['type'] == 'error':
            result += f"{indent}- error: {node['value']}\n"
        else:
            result += f"{indent}- {node['type']}\n"
            if 'children' in node:
                for child in node['children']:
                    result += generate_ast_view(child, level+1)
    elif isinstance(node, ASTNode):
        result += f"{indent}- {node.type}"
        if node.value is not None:
            result += f": {node.value}"
        if node.op is not None:
            result += f" ({node.op})"
        result += f" (linea {node.lineno}, pos {node.lexpos})\n"
        for child in node.children:
            result += generate_ast_view(child, level+1)

    elif isinstance(node, list):
        for item in node:
            result += generate_ast_view(item, level)
            
    else:  # nodos hoja
        result += f"{indent}- {node}\n"
        
    return result
        
def find_column(lexer, lexpos):
    last_cr = lexer.lexdata.rfind('\n', 0, lexpos)
    if last_cr < 0:
        last_cr = 0
    return (lexpos - last_cr)

# Construir el parser
parser = yacc.yacc(debug=False, write_tables=False)
parser.lexer = lexer 