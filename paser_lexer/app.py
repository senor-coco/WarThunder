<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analizador de Código</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            padding: 20px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        textarea {
            width: 100%;
            height: 200px;
            margin-bottom: 10px;
            padding: 10px;
            font-family: monospace;
        }
        button {
            padding: 10px 15px;
            font-size: 16px;
            cursor: pointer;
        }
        .result {
            margin-top: 20px;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            background-color: #f9f9f9;
        }
    </style>
</head>
<body>
    <h1>Analizador de Código</h1>
    <form id="codeForm">
        <textarea id="codigo" placeholder="Escribe tu código aquí..."></textarea>
        <br>
        <button type="submit">Analizar Código</button>
    </form>
    <div id="resultado" class="result"></div>

    <script>
        document.getElementById('codeForm').addEventListener('submit', function(event) {
            event.preventDefault();
            const codigo = document.getElementById('codigo').value;

            fetch('/analizar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ codigo: codigo }),
            })
            .then(response => response.json())
            .then(data => {
                const resultadoDiv = document.getElementById('resultado');
                if (data.status === 'success') {
                    resultadoDiv.innerHTML = `<strong>Éxito:</strong> ${data.message}`;
                } else {
                    resultadoDiv.innerHTML = `<strong>Error:</strong> ${data.message}`;
                }
            })
            .catch((error) => {
                console.error('Error:', error);
                document.getElementById('resultado').innerHTML = '<strong>Error:</strong> No se pudo realizar la solicitud.';
            });
        });
    </script>
</body>
</html>
