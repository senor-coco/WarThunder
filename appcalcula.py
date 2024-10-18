from flask import Flask, render_template, request, jsonify
import ply.lex as lex
import ply.yacc as yacc

app = Flask(__name__)

# Definición de tokens para PLY
tokens = (
    'NUMBER', 'POINT', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'LPAREN', 'RPAREN'
)

# Expresiones regulares para tokens simples
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'

# Definición del token para el punto decimal
t_POINT = r'\.'

# Definición de número (solo enteros, el punto será un token separado)
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)  # Los números son enteros
    return t

# Ignorar espacios y tabulaciones
t_ignore = ' \t'

# Manejo de errores
def t_error(t):
    raise ValueError(f"Carácter ilegal '{t.value[0]}'")
    t.lexer.skip(1)

# Construir el analizador léxico
lexer = lex.lex()

# Nodo de árbol sintáctico
class Node:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right

# Definición de la gramática para PLY
def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression'''
    p[0] = Node(p[2], left=p[1], right=p[3])

def p_expression_group(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]

# Nueva regla para manejar números con decimales (número + punto + número)
def p_expression_decimal(p):
    'expression : NUMBER POINT NUMBER'
    decimal_value = float(f"{p[1]}.{p[3]}")  # Convertir la combinación de número y punto en un valor decimal
    p[0] = Node(decimal_value)

def p_expression_number(p):
    'expression : NUMBER'
    p[0] = Node(p[1])

def p_error(p):
    raise SyntaxError("Error de sintaxis")

# Construir el parser
parser = yacc.yacc()

# Almacenamos la última expresión ingresada
last_expression = ""

# Función segura para evaluar la expresión matemática
def safe_eval(expression):
    global last_expression
    last_expression = expression  # Guardamos la última expresión ingresada
    try:
        result_tree = parser.parse(expression)
        tokens = []
        lexer.input(expression)
        for tok in lexer:
            tokens.append({'value': str(tok.value), 'type': tok.type})
        return result_tree, tokens
    except Exception as e:
        return f"Error: Expresión inválida ({str(e)})", []

# Convertir el árbol en una estructura que pueda ser enviada en JSON
def tree_to_dict(node):
    if not node:
        return None
    return {
        'value': str(node.value),
        'left': tree_to_dict(node.left),
        'right': tree_to_dict(node.right)
    }

@app.route('/')
def index():
    return render_template('index1.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    global last_expression
    data = request.json
    expression = data.get('expression')

    # Evaluamos la expresión y guardamos los tokens
    result_tree, tokens = safe_eval(expression)

    if isinstance(result_tree, str) and result_tree.startswith("Error"):
        return jsonify(status="error", result=result_tree, tokens=tokens)

    # Evaluar el valor del árbol
    def eval_tree(node):
        if isinstance(node.value, (int, float)):
            return node.value
        elif node.value == '+':
            return eval_tree(node.left) + eval_tree(node.right)
        elif node.value == '-':
            return eval_tree(node.left) - eval_tree(node.right)
        elif node.value == '*':
            return eval_tree(node.left) * eval_tree(node.right)
        elif node.value == '/':
            right_value = eval_tree(node.right)
            if right_value == 0:
                raise ZeroDivisionError("No se puede dividir entre cero")
            return eval_tree(node.left) / right_value

    try:
        result = eval_tree(result_tree)
    except ZeroDivisionError as e:
        return jsonify(status="error", result=str(e), tokens=tokens)
    
    return jsonify(status="success", result=result, tokens=tokens)


@app.route('/generate_tree', methods=['POST'])
def generate_tree():
    global last_expression
    data = request.json

    # Usamos la última expresión ingresada, no el resultado
    result_tree, tokens = safe_eval(last_expression)

    if isinstance(result_tree, str) and result_tree.startswith("Error"):
        return jsonify(status="error", result=result_tree, tokens=tokens)

    # Convertir el árbol en un diccionario para enviarlo al frontend
    tree_dict = tree_to_dict(result_tree)
    
    return jsonify(status="success", tree=tree_dict)

if __name__ == '__main__':
    app.run(debug=True)