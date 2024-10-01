# Importar las librerías necesarias
import ply.yacc as yacc
from flask import Flask, request, render_template
import ply.lex as lex
import re  # Importar la librería de expresiones regulares

app = Flask(__name__)

# Palabras reservadas
reserved = {
    'for': 'FOR',
    'while': 'WHILE',
    'if': 'IF',
    'else': 'ELSE',
    'int': 'TIPO_DE_DATO',
    'main': 'PALABRA_RESERVADA_MAIN',
}

# Definir tokens
tokens = ['LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'SEMI', 'NUM', 'ID', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'NEWLINE'] + list(reserved.values())

# Reglas léxicas para operadores y otros símbolos
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_SEMI = r';'  # Punto y coma
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'

# Función para manejar los saltos de línea
def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Regla para identificadores y palabras reservadas
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID')  # Verifica si es una palabra reservada
    return t

# Regla para números
def t_NUM(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Manejo de espacios y tabulaciones
t_ignore = ' \t'

# Manejo de errores léxicos
def t_error(t):
    global error_message
    error_message = f"Carácter ilegal: {t.value[0]}"
    t.lexer.skip(1)

# Inicializar el lexer
lexer = lex.lex()

# Función para el análisis léxico
def lexico(text):
    lexer.input(text)
    tokens = []
    while True:
        tok = lexer.token()
        if not tok:
            break
        tipo = tok.type
        # Descripciones más claras para los tipos de token
        if tipo == 'LPAREN':
            tipo = 'Paréntesis de apertura'
        elif tipo == 'RPAREN':
            tipo = 'Paréntesis de cierre'
        elif tipo == 'LBRACE':
            tipo = 'Llave de apertura'
        elif tipo == 'RBRACE':
            tipo = 'Llave de cierre'
        elif tipo == 'SEMI':
            tipo = 'Punto y coma'
        elif tipo == 'TIPO_DE_DATO':
            tipo = 'Tipo de dato'
        elif tipo == 'PALABRA_RESERVADA_MAIN':
            tipo = 'Palabra reservada main'
        elif tipo in ['FOR', 'WHILE', 'IF', 'ELSE']:
            tipo = 'Palabra reservada'
        elif tipo == 'PLUS':
            tipo = 'Operador suma'
        elif tipo == 'MINUS':
            tipo = 'Operador resta'
        elif tipo == 'TIMES':
            tipo = 'Operador multiplicación'
        elif tipo == 'DIVIDE':
            tipo = 'Operador división'

        # Agregar el token a la lista
        tokens.append({'line': tok.lineno, 'token': tok.value, 'type': tipo})
    return tokens

# Análisis sintáctico mejorado
def analizar_sintactico(text):
    lineas = text.splitlines()  # Separar el texto en líneas
    line_info = []  # Lista para almacenar la información sintáctica

    # Expresión regular para separar tokens (palabras, números, operadores y símbolos)
    token_regex = re.compile(r'(\w+|[{}();])')

    # Analizar cada línea
    for i, linea in enumerate(lineas, start=1):
        palabras = token_regex.findall(linea.strip())  # Usar regex para dividir correctamente la línea en tokens

        for palabra in palabras:
            if palabra in reserved:  # Si es una palabra reservada
                tipo_estructura = palabra
                estructura_correcta = 'Palabra reservada'
                incorrecta = ''
            elif palabra == '(':
                tipo_estructura = '('
                estructura_correcta = 'Paréntesis de apertura'
                incorrecta = ''
            elif palabra == ')':
                tipo_estructura = ')'
                estructura_correcta = 'Paréntesis de cierre'
                incorrecta = ''
            elif palabra == '{':
                tipo_estructura = '{'
                estructura_correcta = 'Llave de apertura'
                incorrecta = ''
            elif palabra == ';':
                tipo_estructura = ';'
                estructura_correcta = 'Punto y coma'
                incorrecta = ''
            elif palabra == '}':
                tipo_estructura = '}'
                estructura_correcta = 'Llave de cierre'
                incorrecta = ''
            elif palabra.isdigit():  # Si es un número
                tipo_estructura = palabra
                estructura_correcta = 'NUM'
                incorrecta = ''
            elif palabra.isidentifier():  # Si es un identificador válido
                tipo_estructura = palabra
                estructura_correcta = ''  # Dejar en blanco si es un identificador válido
                incorrecta = 'ID'
            else:
                tipo_estructura = palabra
                estructura_correcta = ''
                incorrecta = palabra  # Marcar como incorrecta si no es reconocida

            # Agregar la estructura encontrada a line_info
            line_info.append({
                'line': i,
                'structure': tipo_estructura,
                'correct': estructura_correcta,
                'incorrect_structure': incorrecta
            })

    return line_info

# Reiniciar el número de línea
def reiniciar_numero_linea():
    global lexer
    lexer = lex.lex()

# Segundo analizador sintáctico
def segundo_analizador(text):
    # Expresión regular para validar la estructura básica de 'int main() { ... }'
    patron = r'^\s*int\s+main\s*\(\s*\)\s*\{\s*(int\s+[a-zA-Z_][a-zA-Z0-9_]*;\s*)*\s*\}\s*$'
    
    if re.match(patron, text.strip()):
        return "La sintaxis es correcta."
    else:
        return "La sintaxis es incorrecta. El formato esperado es: 'int main() { int x; }'"

# Rutas para Flask
@app.route('/', methods=['GET', 'POST'])
def index():
    global error_message
    error_message = None
    tokens = []
    sintactico_info = []
    resultado_segundo = ""
    text = ""  # Inicializar text como cadena vacía
    codigo_segundo_analizador = ""  # Para almacenar el código del segundo analizador

    if request.method == 'POST':
        if 'text' in request.form:
            text = request.form['text']
            tokens = lexico(text)
            sintactico_info = analizar_sintactico(text)
            return render_template('index.html', tokens=tokens, text=text, sintactico_info=sintactico_info, error_message=error_message)

        elif 'reset' in request.form:  # Botón de reset para el primer analizador
            # Borrar todo el contenido de ambos analizadores
            reiniciar_numero_linea()
            return render_template('index.html', tokens=None, text=None, sintactico_info=None, error_message=None, codigo_segundo_analizador="", resultado_segundo="")

        # Procesar el segundo analizador si se envió código
        if 'codigo' in request.form:
            codigo_segundo_analizador = request.form['codigo']
            resultado_segundo = segundo_analizador(codigo_segundo_analizador)

            # Análisis léxico y sintáctico del texto original
            tokens = lexico(text)  # Re-analizar el texto original para obtener tokens
            sintactico_info = analizar_sintactico(text)  # Re-analizar el texto original para obtener análisis sintáctico
            
            # Retornar todos los resultados al mismo tiempo
            return render_template('index.html', text=text, tokens=tokens, sintactico_info=sintactico_info,
                                   codigo_segundo_analizador=codigo_segundo_analizador, resultado_segundo=resultado_segundo)

    return render_template('index.html', text=text, tokens=tokens, sintactico_info=sintactico_info,
                           codigo_segundo_analizador=codigo_segundo_analizador, resultado_segundo=resultado_segundo)

if __name__ == '__main__':
    app.run(debug=True)
