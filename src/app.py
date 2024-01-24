import os
from flask_cors import CORS
from waitress import serve
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import chatbot

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Load the .env file to be able to use the secrets
load_dotenv()


@app.route('/api/chat', methods=['POST'])
def chat_api():
    json_request = request.get_json()

    if 'query' not in json_request:
        return jsonify({
            "error": {
                "query": "Please provide a question via Query parameter"
            }
        }, 422)

    if 'identifier' not in json_request:
        return jsonify({
            "error": {
                "identifier": "Please provide an identifier via Identifier parameter"
            }
        }, 422)

    question = json_request['query']
    identifier = json_request['identifier']

    return jsonify({
        "data": {
            "question": question,
            "identifier": identifier,
            "answer": chatbot.make_ai_request(question, identifier)
        }
    })


if __name__ == '__main__':
    if os.getenv("DEBUG"):
        app.run(host='0.0.0.0', port=8080, use_reloader=True, debug=True)
    else:
        serve(app, host="0.0.0.0", port=8080)
