from flask import Flask, request, render_template
import ply.lex as lex  # Usar lex de PLY para el análisis léxico

app = Flask(__name__)

# Definir palabras reservadas
reserved = {
    'for': 'Reservada',
    'while': 'Reservada',
    'if': 'Reservada',
    'else': 'Reservada',
    'class': 'Reservada',
}

# Lista de tokens
tokens = ['LPAREN', 'RPAREN', 'SEMI', 'NUM', 'ID'] + list(reserved.values())

# Reglas para los tokens
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_SEMI = r';'

def t_NUM(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID')
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

error_message = None

def t_error(t):
    global error_message
    error_message = f"Carácter ilegal: {t.value[0]}"
    t.lexer.skip(1)

# Construir el lexer
lexer = lex.lex()

# Función para el análisis léxico
def lexico(text):
    lexer.input(text)
    tokens = []
    line_info = []

    while True:
        tok = lexer.token()
        if not tok:
            break
        tokens.append({'line': tok.lineno, 'token': tok.value, 'type': tok.type})
        line_info.append((tok.lineno, tok.type))

    same_line = len(set(line for line, _ in line_info)) == 1
    return tokens, line_info, same_line

# Función para análisis sintáctico (actualizada para analizar todas las palabras de cada línea)
def analizar_sintactico(text):
    estructuras_validas = ["for", "if", "while", "return", "def"]
    lineas = text.splitlines()
    line_info = []

    for i, linea in enumerate(lineas, start=1):
        palabras = linea.strip().split()
        for palabra in palabras:  # Analizamos cada palabra
            es_correcta = palabra in estructuras_validas
            line_info.append({
                'line': i,
                'structure': palabra,
                'correct': es_correcta
            })

    return line_info

def reiniciar_numero_linea():
    global lexer
    lexer = lex.lex()

@app.route('/', methods=['GET', 'POST'])
def index():
    global error_message
    error_message = None

    if request.method == 'POST':
        if 'text' in request.form and 'reset' not in request.form:
            text = request.form['text']
            tokens, line_info, same_line = lexico(text)
            sintactico_info = analizar_sintactico(text)
            return render_template('index.html', tokens=tokens, text=text, line_info=line_info, same_line=same_line, sintactico_info=sintactico_info, error_message=error_message)
        
        elif 'reset' in request.form:
            reiniciar_numero_linea()
            return render_template('index.html', tokens=None, text=None, line_info=None, same_line=None, sintactico_info=None, error_message=None)

    return render_template('index.html', tokens=None, text=None, line_info=None, same_line=None, sintactico_info=None, error_message=None)

if __name__ == '__main__': 
    app.run(debug=True)
