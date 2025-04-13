# semantico.py
symbol_table = {}

def check_semantics(tokens):
    errors = []
    for token in tokens:
        if token.type == 'ID':
            if token.value not in symbol_table:
                errors.append(f"Error semántico: Variable '{token.value}' no declarada")
            else:
                print(f"Variable '{token.value}' declarada correctamente")
    return errors

# Función para probar el análisis semántico
def test_semantics(input_text):
    from lexico import test_lexer
    tokens = test_lexer(input_text)
    return check_semantics(tokens)
# 
# Prueba del análisis semántico
if __name__ == "__main__":
    data = "x + y * (10 - 4)"
    errors = test_semantics(data)
    for error in errors:
        print(error)