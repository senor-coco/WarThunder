from flask import Flask, request, render_template
import ply.lex as lex  # Usar lex de PLY para el análisis léxico

app = Flask(__name__)  # Cambiado a __name__

# Definir palabras reservadas
reserved = {
   'for': 'Reservada',  # Etiquetar como 'Reservada'
   'while': 'Reservada',
   'if' : 'Reservada',
   'else' : 'Reservada',
   'class' : 'Reservada',
}

# Lista de tokens
tokens = [
    'Libre',  # Token genérico para palabras
] + list(set(reserved.values()))  # Añadir las palabras reservadas a la lista de tokens

# Expresión regular para palabras reservadas
def t_RESERVED(t):
    r'\b(for|while|if|else|class)\b'  # Reconocer palabras reservadas
    t.type = reserved.get(t.value)  # Cambiar el tipo a 'Reservada'
    return t

# Expresión regular para palabras generales
def t_Libre(t):
    r'\b\w+\b'
    return t

# Regla para contar líneas
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Manejo de errores
error_message = None  # Variable para guardar mensajes de error

def t_error(t):
    global error_message
    error_message = f"Carácter ilegal: {t.value[0]}"
    t.lexer.skip(1)

# Construir el lexer
lexer = lex.lex()

def lexico(text):
    lexer.input(text)
    tokens = []
    line_info = []
    while True:
        tok = lexer.token()
        if not tok:
            break
        tokens.append(tok.value)  # Añadir el valor del token a la lista de tokens
        line_info.append((tok.lineno, tok.type))  # Guardar el número de línea y tipo
    return tokens, line_info

@app.route('/', methods=['GET', 'POST'])
def index():
    global error_message
    error_message = None  # Restablecer mensajes de error
    if request.method == 'POST':
        text = request.form['text']
        tokens, line_info = lexico(text)
        return render_template('index.html', tokens=tokens, text=text, line_info=line_info, error_message=error_message)
    return render_template('index.html', tokens=None, text=None, line_info=None, error_message=None)

# Para ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True)