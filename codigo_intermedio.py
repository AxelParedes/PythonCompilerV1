
class ASTNode:
    def __init__(self, type, value=None, children=None):
        self.type = type
        self.value = value
        self.children = children if children else []

def generate_intermediate_code(tokens):
    root = ASTNode('Program')
    root.children.append(ASTNode('Expression', value=tokens))
    return root

# Función para probar la generación de código intermedio
def test_intermediate_code(input_text):
    from lexico import test_lexer
    tokens = test_lexer(input_text)
    return generate_intermediate_code(tokens)

# Prueba de la generación de código intermedio
if __name__ == "__main__":
    data = "3 + 5 * (10 - 4)"
    ast = test_intermediate_code(data)
    print(f"Código intermedio generado: {ast}")