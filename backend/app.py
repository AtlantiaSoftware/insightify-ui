# Archivo: app.py (Versión de Depuración para espiar el stream)

from flask import Flask, request, Response, stream_with_context
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)

FLOWISE_API_URL = 'https://flowise.atlantia.ai/api/v1/prediction/b1528cfd-e54d-40cb-92ee-5cb31c26c41e'

@app.route('/chat', methods=['POST'])
def chat_proxy():
    user_question = request.json.get('question')
    if not user_question:
        return Response(json.dumps({'error': 'La pregunta es requerida'}), status=400, mimetype='application/json')

    print(f"Recibida pregunta: '{user_question}'. Pidiendo a Flowise...")

    try:
        flowise_response = requests.post(
            FLOWISE_API_URL,
            json={'question': user_question},
            stream=True,
            headers={'Content-Type': 'application/json'}
        )

        # Esta función ahora imprimirá cada trozo de datos en la terminal
        def generate_and_log():
            print("\n--- INICIO DEL STREAM DE FLOWISE ---")
            for chunk in flowise_response.iter_content(chunk_size=None): # Usamos chunk_size=None para ver los eventos como llegan
                # Decodificamos el trozo para poder imprimirlo como texto
                try:
                    chunk_text = chunk.decode('utf-8')
                    print(chunk_text, end='') # Imprime el chunk en la terminal de VS Code
                except UnicodeDecodeError:
                    print(f"\n[Chunk no decodificable: {chunk}]")
                
                yield chunk # Reenviamos el trozo original al frontend
            print("\n--- FIN DEL STREAM DE FLOWISE ---\n")

        return Response(stream_with_context(generate_and_log()), content_type=flowise_response.headers['content-type'])

    except requests.exceptions.RequestException as e:
        print(f"Error al contactar Flowise: {e}")
        return Response(json.dumps({'error': 'sNo se pudo obtener respuesta de Flowise.'}), status=502, mimetype='application/json')

if __name__ == '__main__':
    app.run(port=5000, debug=True)