# Importar las librerías necesarias 
import ply.yacc as yacc
from flask import Flask, request, render_template
import ply.lex as lex
import re  # Importar la librería de expresiones regulares

app = Flask(__name__)

# Palabras reservadas
reserved = {
    'programa': 'PROGRAMA',
    'int': 'TIPO_DE_DATO',
    'read': 'READ',
    'printf': 'PRINTF',
    'end': 'END',
}

# Definir tokens
tokens = ['LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'SEMI', 'ID', 'PLUS', 'EQUALS', 'STRING', 'NUM', 'TIPO_DE_DATO'] + list(reserved.values())

# Reglas léxicas para operadores y otros símbolos
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_SEMI = r';'
t_PLUS = r'\+'
t_EQUALS = r'='
t_STRING = r'\".*?\"'

# Regla para números
def t_NUM(t):
    r'\d+'
    t.value = int(t.value)
    t.lineno = lexer.lineno  # Asignar la línea correcta
    return t

# Regla para identificadores y palabras reservadas
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID')  # Verifica si es una palabra reservada
    t.lineno = lexer.lineno  # Asignar la línea correcta
    return t

# Manejo de nuevas líneas
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

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
    conteo_tokens = {
        'palabras_reservadas': 0,
        'identificadores': 0,
        'cadenas': 0,
        'numeros': 0,
        'simbolos': 0
    }
    
    while True:
        tok = lexer.token()
        if not tok:
            break
        
        # Determinar tipo de token
        tipo = tok.type
        token_data = {
            'line': tok.lineno,
            'token': tok.value,
            'reserved_word': '',
            'identifier': '',
            'string': '',
            'number': '',
            'symbol': '',
            'data_type': ''
        }

        # Clasificar el tipo de token y contar
        if tipo in reserved.values():  # Si es palabra reservada
            token_data['reserved_word'] = tok.value
            token_data['data_type'] = 'Palabra reservada'
            conteo_tokens['palabras_reservadas'] += 1
        elif tipo == 'ID':  # Identificadores
            token_data['identifier'] = tok.value
            token_data['data_type'] = 'Identificador'
            conteo_tokens['identificadores'] += 1
        elif tipo == 'STRING':  # Cadenas de texto
            token_data['string'] = tok.value
            token_data['data_type'] = 'Cadena de texto'
            conteo_tokens['cadenas'] += 1
        elif tipo == 'NUM':  # Números
            token_data['number'] = tok.value
            token_data['data_type'] = 'Número'
            conteo_tokens['numeros'] += 1
        elif tipo in ['LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'SEMI', 'PLUS', 'EQUALS']:  # Símbolos
            token_data['symbol'] = tok.value
            token_data['data_type'] = 'Símbolo'
            conteo_tokens['simbolos'] += 1
        elif tipo == 'TIPO_DE_DATO':  # Tipos de datos
            token_data['data_type'] = 'Tipo de dato'
            conteo_tokens['palabras_reservadas'] += 1
        
        # Agregar token clasificado a la lista
        tokens.append(token_data)

    return tokens, conteo_tokens  # Devolver también el conteo de tokens

# Análisis sintáctico mejorado
def analizar_sintactico(text):
    lineas = text.splitlines()  # Separar el texto en líneas
    line_info = []  # Lista para almacenar la información sintáctica

    # Expresión regular para separar tokens (palabras, números, operadores y símbolos)
    token_regex = re.compile(r'(\w+|[{}();=+])')

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
            elif palabra == '=':
                tipo_estructura = '='
                estructura_correcta = 'Operador asignación'
                incorrecta = ''
            elif palabra == '+':
                tipo_estructura = '+'
                estructura_correcta = 'Operador suma'
                incorrecta = ''
            elif palabra.isdigit():  # Si es un número
                tipo_estructura = palabra
                estructura_correcta = 'Número'
                incorrecta = ''
            elif palabra.isidentifier():  # Si es un identificador válido
                tipo_estructura = palabra
                estructura_correcta = ''  # Dejar en blanco si es un identificador válido
                incorrecta = 'Identificador'
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
    # Expresión regular para validar la estructura 'programa suma() { ... }'
    patron = r'^\s*programa\s+\w+\s*\(\s*\)\s*\{\s*(int\s+[a-zA-Z_][a-zA-Z0-9_,]*;\s*)*(read\s+\w+;\s*)*(\w+\s*=\s*\w+\s*\+\s*\w+;\s*)*printf\s*\(.*\);\s*end\s*;\s*\}\s*$'

    if re.match(patron, text.strip()):
        return "La sintaxis es correcta."
    else:
        return "La sintaxis es incorrecta. Asegúrate de que el código siga el formato adecuado."

# Rutas para Flask
@app.route('/', methods=['GET', 'POST'])
def index():
    global error_message
    error_message = None
    tokens = []
    sintactico_info = []
    resultado_segundo = ""
    text = ""
    codigo_segundo_analizador = ""
    conteo_tokens = {
        'palabras_reservadas': 0,
        'identificadores': 0,
        'cadenas': 0,
        'numeros': 0,
        'simbolos': 0
    }

    if request.method == 'POST':
        if 'text' in request.form and request.form['text'].strip() != "":
            text = request.form['text']
            tokens, conteo_tokens = lexico(text)  # Obtener los tokens y el conteo
            sintactico_info = analizar_sintactico(text)

        elif 'codigo' in request.form and request.form['codigo'].strip() != "":
            codigo_segundo_analizador = request.form['codigo']
            resultado_segundo = segundo_analizador(codigo_segundo_analizador)

    return render_template('index.html', tokens=tokens, error_message=error_message, sintactico_info=sintactico_info,
                           resultado_segundo=resultado_segundo, conteo_tokens=conteo_tokens)  # Pasar conteo a la plantilla

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True)
