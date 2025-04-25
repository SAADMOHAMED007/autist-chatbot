import React, { useState, useRef, useEffect } from 'react';
import './ChatBot.css';

// Constantes pour les types de messages
const MESSAGE_TYPES = {
  USER: 'user',
  BOT: 'bot'
};

/**
 * Composant ChatBot - Interface utilisateur pour le chatbot d'aide aux parents d'enfants autistes
 * 
 * Ce composant peut être facilement intégré dans n'importe quelle page de l'application
 */
const ChatBot = () => {
  // État des messages
  const [messages, setMessages] = useState([
    {
      type: MESSAGE_TYPES.BOT,
      content: "Bonjour ! Je suis là pour vous aider avec vos questions sur l'autisme et vous donner des conseils pour interagir avec votre enfant. Comment puis-je vous aider aujourd'hui ?"
    }
  ]);
  
  // État pour le message en cours de saisie
  const [inputMessage, setInputMessage] = useState('');
  
  // État pour l'animation de chargement pendant l'attente de réponse
  const [isLoading, setIsLoading] = useState(false);
  
  // Référence pour faire défiler automatiquement vers le dernier message
  const messagesEndRef = useRef(null);
  
  // État pour la visibilité du chatbot (replié/déplié)
  const [isOpen, setIsOpen] = useState(false);

  // Défilement automatique vers le dernier message
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Effet pour défiler vers le bas à chaque nouveau message
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Fonction pour envoyer le message au backend
  const sendMessage = async () => {
    // Ne rien faire si le message est vide
    if (!inputMessage.trim()) return;
    
    // Ajouter le message de l'utilisateur
    const userMessage = { type: MESSAGE_TYPES.USER, content: inputMessage };
    setMessages(prevMessages => [...prevMessages, userMessage]);
    
    // Réinitialiser le champ de saisie
    setInputMessage('');
    
    // Afficher l'animation de chargement
    setIsLoading(true);
    
    try {
      // Appel à l'API backend
      const response = await fetch('http://192.168.1.23:5000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputMessage,
          context: {
            user_id: 'user_123' // Remplacer par l'ID réel de l'utilisateur si disponible
          }
        }),
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        // Ajouter la réponse du bot
        setMessages(prevMessages => [
          ...prevMessages,
          { type: MESSAGE_TYPES.BOT, content: data.response }
        ]);
      } else {
        // En cas d'erreur, afficher un message générique
        setMessages(prevMessages => [
          ...prevMessages,
          { type: MESSAGE_TYPES.BOT, content: "Je suis désolé, j'ai rencontré un problème. Pourriez-vous reformuler votre question ?" }
        ]);
      }
    } catch (error) {
      console.error('Erreur lors de la communication avec le chatbot:', error);
      // Message d'erreur en cas de problème de connexion
      setMessages(prevMessages => [
        ...prevMessages,
        { type: MESSAGE_TYPES.BOT, content: "Désolé, je ne peux pas vous répondre pour le moment. Veuillez vérifier votre connexion internet." }
      ]);
    } finally {
      // Masquer l'animation de chargement
      setIsLoading(false);
    }
  };

  // Gestionnaire pour la touche Entrée
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      sendMessage();
    }
  };

  // Basculer l'affichage du chatbot
  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  return (
    <div className={`chatbot-container ${isOpen ? 'open' : 'closed'}`}>
      {/* Bouton pour ouvrir/fermer le chatbot */}
      <button 
        className="chatbot-toggle"
        onClick={toggleChat}
      >
        {isOpen ? 'Fermer' : 'Aide'}
      </button>
      
      {isOpen && (
        <div className="chatbot-window">
          {/* En-tête du chatbot */}
          <div className="chatbot-header">
            <h3>Assistant pour parents d'enfants autistes</h3>
          </div>
          
          {/* Zone de messages */}
          <div className="chatbot-messages">
            {messages.map((message, index) => (
              <div 
                key={index} 
                className={`message ${message.type === MESSAGE_TYPES.USER ? 'user-message' : 'bot-message'}`}
              >
                <div className="message-content">
                  {message.content}
                </div>
              </div>
            ))}
            
            {/* Animation de "chargement" pendant que le bot "réfléchit" */}
            {isLoading && (
              <div className="message bot-message">
                <div className="loading-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}
            
            {/* Élément invisible pour le défilement automatique */}
            <div ref={messagesEndRef} />
          </div>
          
          {/* Zone de saisie */}
          <div className="chatbot-input">
            <input
              type="text"
              placeholder="Tapez votre question ici..."
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isLoading}
            />
            <button 
              onClick={sendMessage}
              disabled={isLoading || !inputMessage.trim()}
            >
              Envoyer
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatBot;