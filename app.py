
from flask import Flask, jsonify, request, json
from flask_cors import CORS
from google import genai
import os 
from dotenv import load_dotenv # Importa a função para carregar .env 

# Carrega variáveis de ambiente do arquivo .env 
load_dotenv()


app = Flask(__name__)


# Isso permitirá que qualquer origem (qualquer domínio/porta) faça requisições ao seu back-end.
CORS(app)

API_KEY = os.getenv("GOOGLE_API_KEY")

client = genai.Client(api_key=API_KEY)


def criar_historia(input):
    prompt = f"""
        Crie uma historia infantil que tenha como base {input}. A história deve ser lúdica e atrativa para crianças. Não deve conter nada violento, sexual ou sensível. Deve ter no máximo 4 parágrafos.
        Envie a resposta formatada como JSON com os campos: "title" (título da história) e "html" (história formatada em HTML, com <h1> no título e <p> nos parágrafos), sem cabeçalho ou outras marcações.
        Exemplo de resposta:
        [
          {{
            "title": "O Leão que Aprendeu a Compartilhar",
            "html": "<h1>O Leão que Aprendeu a Compartilhar</h1><p>Era uma vez...</p>"
          }}
        ]

        Caso o usuário pessa algo com conteúdo adulto, violento ou preconceituoso retorne a seguinte mensagem
        Exemplo de resposta:
        [
          {{
            "title": "Tema inválido!",
            "html": "<h1>O tema que você pediu viola minhas diretrizes, tente novamnete com outro tema...</p>"
          }}
        ]
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config={"response_mime_type": "application/json"},
    )

    # A resposta já está em .text, que é uma string JSON
    json_data = json.loads(response.text)

    # Esperamos uma lista com pelo menos um objeto que tenha a chave 'html'
    if isinstance(json_data, list) and len(json_data) > 0 and 'html' in json_data[0]:
        html = json_data[0]['html']
        return html.strip()  # Remove espaços ou \n desnecessários
    else:
        raise ValueError("Formato inesperado na resposta da API.")



# ROTA PRINCIPAL DE TESTE
@app.route('/')
def index():
    return 'API ON', 200

@app.route('/historia', methods=['POST'])
def make_historia():
    try:
        # Recupera o corpo da requisição POST que deve conter o input (tema da história)
        data = request.get_json()
        
        if not data or 'tema' not in data:
            return jsonify({'error': 'O campo "tema" é obrigatório.'}), 400
        
        tema = data['tema']
        
        # Gera a história com base no tema recebido
        historia = criar_historia(tema)
        
        # Retorna a história gerada em formato JSON
        return jsonify({'historia': historia}), 200

    except Exception as e:
        print(f"Um erro interno ocorreu na API: {e}")
        return jsonify({'error': str(e)}), 500  # Retorna código 500 para erros internos


if __name__ == '__main__':
    app.run(debug=True)