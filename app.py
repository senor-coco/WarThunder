from flask import Flask, request, render_template
import re
app = Flask(__name__)
def lexico(text):
    tokens = re.findall(r'\b\w+\b', text)
    line_info = []
    keywords = {'for': 'Palabra Reservada'}   
    for i, token in enumerate(tokens):
        lower_token = token.lower()  # Convertir el token a minúsculas
        tipo = keywords.get(lower_token, 'Palabra Libre') 
        line_info.append((i + 1, tipo)) 
    return tokens, line_info
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text = request.form['text']
        tokens, line_info = lexico(text)
        return render_template('index.html', tokens=tokens, text=text, line_info=line_info)
    return render_template('index.html', tokens=None, text=None, line_info=None)
if __name__ == '__main__':
    app.run(debug=True)