from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from chatbot import get_chatbot_response

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)
CORS(app)  # Activer CORS pour permettre les requêtes du frontend

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Point d'entrée API pour le chatbot
    Le frontend envoie des messages et reçoit des réponses
    """
    data = request.json
    user_message = data.get('message', '')
    user_context = data.get('context', {})
    
    if not user_message:
        return jsonify({'error': 'Message vide'}), 400
    
    # Obtenir la réponse du chatbot
    response = get_chatbot_response(user_message, user_context)
    
    return jsonify({
        'response': response,
        'status': 'success'
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Point d'entrée API pour vérifier que le serveur fonctionne
    """
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)