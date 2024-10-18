import ply.yacc as yacc
import ply.lex as lex
from flask import Flask, request, jsonify

# --------------------------- Analizador Léxico ---------------------------

# Lista de tokens reservados
reserved = {
    'if': 'IF',
    'else': 'ELSE',
    'for': 'FOR',
    'while': 'WHILE',
    'int': 'INT',
    'float': 'FLOAT',
    'string': 'STRING',
    'System': 'SYSTEM',
    'out': 'OUT',
    'println': 'PRINTLN'
}

tokens = [
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'LPAREN',
    'RPAREN',
    'NUMBER',
    'EQUALS',
    'COMMA',
    'SEMICOLON',
    'COLON',
    'DOT',
    'LEFT_BRACKET',
    'RIGHT_BRACKET',
    'LEFT_BRACE',
    'RIGHT_BRACE',
    'ID',
    'INCREMENT',
    'LESS_THAN',
    'GREATER_THAN',
    'LESS_THAN_EQUAL',
    'GREATER_THAN_EQUAL',
    'EQUAL_EQUAL',
    'NOT_EQUAL'
] + list(reserved.values())

# Reglas de expresiones regulares para los tokens
t_PLUS = r'\+'
t_MINUS = r'\-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_EQUALS = r'='
t_COMMA = r','
t_SEMICOLON = r';'
t_COLON = r':'
t_DOT = r'\.'
t_LEFT_BRACKET = r'\['
t_RIGHT_BRACKET = r'\]'
t_LEFT_BRACE = r'\{'
t_RIGHT_BRACE = r'\}'
t_INCREMENT = r'\+\+'
t_LESS_THAN = r'<'
t_GREATER_THAN = r'>'
t_LESS_THAN_EQUAL = r'<='
t_GREATER_THAN_EQUAL = r'>='
t_EQUAL_EQUAL = r'=='
t_NOT_EQUAL = r'!='
t_ignore = r'\t'

# Contador de líneas
line_counter = 1

def reset_lexer():
    global line_counter
    line_counter = 1

def t_NUMBER(t):
    r'\d+(\.\d+)?'
    t.value = float(t.value)
    return t

def t_STRING(t):
    r'\"([^\\\n]|(\\.))*?\"'
    return t

# Regla para el salto de línea
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    global line_counter
    line_counter += 1

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID')
    t.lineno = t.lexer.lineno
    return t

# Construcción del lexer
lexer = lex.lex()

# --------------------------- Analizador Sintáctico ---------------------------

def p_program(p):
    '''
    program : statements
    '''
    p[0] = "Programa válido."

def p_statements(p):
    '''
    statements : statement
               | statements statement
    '''
    p[0] = "Lista de declaraciones válida."

def p_statement(p):
    '''
    statement : expression SEMICOLON
              | for_loop
              | println_statement
    '''
    p[0] = "Declaración válida."

def p_for_loop(p):
    '''
    for_loop : FOR LPAREN assignment SEMICOLON condition SEMICOLON expression RPAREN LEFT_BRACE statements RIGHT_BRACE
    '''
    p[0] = "Bucle For válido."

def p_println_statement(p):
    '''
    println_statement : SYSTEM DOT OUT DOT PRINTLN LPAREN expression RPAREN SEMICOLON
    '''
    p[0] = "Declaración de impresión válida."

def p_assignment(p):
    '''
    assignment : ID EQUALS expression
    '''
    p[0] = "Asignación válida."

def p_condition(p):
    '''
    condition : expression
    '''
    p[0] = "Condición válida."

def p_expression(p):
    '''
    expression : expression PLUS expression
               | expression MINUS expression
               | expression TIMES expression
               | expression DIVIDE expression
               | LPAREN expression RPAREN
               | ID
               | NUMBER
               | STRING
               | expression LESS_THAN expression
               | expression GREATER_THAN expression
               | expression LESS_THAN_EQUAL expression
               | expression GREATER_THAN_EQUAL expression
               | expression EQUAL_EQUAL expression
               | expression NOT_EQUAL expression
    '''
    p[0] = "Expresión válida."

def p_increment(p):
    '''
    increment : ID INCREMENT
    '''
    p[0] = "Incremento válido."

def p_error(p):
    if p is not None:
        mensaje_error = f"Error de sintaxis en el token '{p.value}', tipo '{p.type}'"
        raise SyntaxError(mensaje_error)
    else:
        raise SyntaxError("Error de sintaxis: No se pudo construir el árbol de análisis.")

# Construcción del parser
parser = yacc.yacc(errorlog=yacc.NullLogger())

# Función para analizar el código
def parse_code(code, debug=None):
    try:
        parser.parse(code, debug=debug)
        return {"status": "success", "message": "Análisis sintáctico completado."}
    except SyntaxError as e:
        return {"status": "error", "message": str(e)}

# --------------------------- Aplicación Flask ---------------------------

app = Flask(__name__)

@app.route('/analizar', methods=['POST'])
def analizar_codigo():
    data = request.json
    codigo = data.get('codigo', '')
    if codigo:
        resultado = parse_code(codigo)
        return jsonify(resultado)
    else:
        return jsonify({"status": "error", "message": "No se proporcionó código para analizar."})

if __name__ == '__main__':
    app.run(debug=True)
