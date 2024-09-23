import ply.yacc as yacc  # Importar yacc para el análisis sintáctico
from flask import Flask, request, render_template
import ply.lex as lex  # Usar lex de PLY para el análisis léxico

app = Flask(__name__)  # Crear una instancia de la aplicación Flask

# Definir palabras reservadas
reserved = {
    'for': 'Reservada',
    'while': 'Reservada',
    'if': 'Reservada',
    'else': 'Reservada',
    'hola mundo': 'Reservada',
}

# Lista de tokens, combinando paréntesis, punto y coma, números, identificadores y palabras reservadas
tokens = ['LPAREN', 'RPAREN', 'SEMI', 'NUM', 'ID'] + list(reserved.values())

# Reglas para los tokens individuales
t_LPAREN = r'\('  # Token para el paréntesis izquierdo
t_RPAREN = r'\)'  # Token para el paréntesis derecho
t_SEMI = r';'     # Token para el punto y coma

# Regla para reconocer números enteros
def t_NUM(t):
    r'\d+'  # Expresión regular para números enteros
    t.value = int(t.value)  # Convertir el valor del token a entero
    return t

# Regla para reconocer identificadores (nombres de variables, funciones, etc.)
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'  # Identificadores deben comenzar con letra o guion bajo
    t.type = reserved.get(t.value, 'ID')  # Verificar si es una palabra reservada
    return t

# Manejar nuevas líneas y ajustar el número de línea del lexer
def t_newline(t):
    r'\n+'  # Expresión regular para nueva línea
    t.lexer.lineno += len(t.value)  # Incrementar el contador de líneas

error_message = None  # Variable global para almacenar mensajes de error

# Manejar errores de caracteres ilegales
def t_error(t):
    global error_message
    error_message = f"Carácter ilegal: {t.value[0]}"  # Almacenar mensaje de error
    t.lexer.skip(1)  # Saltar el carácter ilegal

# Construir el lexer basado en las reglas anteriores
lexer = lex.lex()

# Función para realizar el análisis léxico
def lexico(text):
    lexer.input(text)  # Proporcionar el texto al lexer
    tokens = []  # Lista para almacenar los tokens generados

    # Obtener tokens del lexer
    while True:
        tok = lexer.token()
        if not tok:
            break
        tokens.append({'line': tok.lineno, 'token': tok.value, 'type': tok.type})  # Agregar información del token

    return tokens

# Reglas de la gramática para yacc
def p_expresion(p):
    '''expresion : ID LPAREN expresion RPAREN
                 | NUM
                 | Reservada
    '''
    p[0] = p[1]  # Simplemente devolvemos el valor como está

def p_error(p):
    global error_message
    error_message = "Error de sintaxis"  # Almacenar mensaje de error de sintaxis

# Construir el parser basado en las reglas anteriores
parser = yacc.yacc()

# Función para realizar el análisis sintáctico
def analizar_sintactico(text):
    lineas = text.splitlines()  # Separar el texto en líneas
    line_info = []  # Lista para almacenar la información sintáctica
    estructuras_validas = ["for", "if", "while", "else", "hola mundo"]  # Estructuras válidas

    # Analizar cada línea
    for i, linea in enumerate(lineas, start=1):
        palabras = linea.strip().split()  # Separar la línea en palabras
        for palabra in palabras:
            es_correcta = palabra in estructuras_validas  # Verificar si la palabra es una estructura válida
            line_info.append({
                'line': i,
                'structure': palabra,
                'correct': 'x' if es_correcta else '',  # Marcar con 'x' si es correcta
                'incorrect_structure': palabra if not es_correcta else ''  # Capturar la estructura incorrecta
            })

    return line_info

# Función para reiniciar el número de línea del lexer
def reiniciar_numero_linea():
    global lexer
    lexer = lex.lex()  # Reiniciar el lexer

# Ruta principal de la aplicación
@app.route('/', methods=['GET', 'POST'])
def index():
    global error_message
    error_message = None  # Reiniciar el mensaje de error

    if request.method == 'POST':
        if 'text' in request.form and 'reset' not in request.form:
            text = request.form['text']  # Obtener el texto ingresado
            tokens = lexico(text)  # Realizar análisis léxico
            sintactico_info = analizar_sintactico(text)  # Realizar análisis sintáctico
            return render_template('index.html', tokens=tokens, text=text, sintactico_info=sintactico_info, error_message=error_message)
        
        elif 'reset' in request.form:  # Si se presiona el botón de reinicio
            reiniciar_numero_linea()  # Reiniciar el lexer
            return render_template('index.html', tokens=None, text=None, sintactico_info=None, error_message=None)

    return render_template('index.html', tokens=None, text=None, sintactico_info=None, error_message=None)

# Ejecutar la aplicación en modo de depuración
if __name__ == '__main__': 
    app.run(debug=True)