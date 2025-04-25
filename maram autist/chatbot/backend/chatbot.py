import nltk
import os
import json
import random
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
import torch

# Télécharger les ressources NLTK nécessaires (à exécuter une seule fois)
# Décommentez les lignes suivantes lors de la première exécution
# nltk.download('punkt')
# nltk.download('wordnet')

class AutismChatbot:
    def __init__(self):
        """
        Initialisation du chatbot spécialisé pour les parents d'enfants autistes
        """
        # Chargement de la base de connaissances
        self.knowledge_base = self._load_knowledge_base()
        
        # Initialiser les modèles si disponibles, sinon utiliser un système basé sur des règles
        self.use_transformer = False
        try:
            # Essayer de charger un modèle pré-entraîné pour des réponses plus contextuelles
            # On utilise un modèle léger par défaut, mais il peut être remplacé par des modèles plus avancés
            self.tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
            self.model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-small")
            self.use_transformer = True
        except:
            print("Utilisation du système basé sur des règles (modèle transformers non disponible)")
            
        # Historique des conversations pour le contexte
        self.conversation_history = {}
    
    def _load_knowledge_base(self):
        """
        Charge la base de connaissances sur l'autisme et les stratégies d'interaction
        """
        # Dans une version production, cette base serait chargée depuis un fichier ou une BDD
        return {
            "interaction": [
                {
                    "patterns": ["comment communiquer", "comment parler", "langage", "communication"],
                    "responses": [
                        "Pour communiquer avec un enfant autiste, utilisez un langage clair et concis. Évitez les expressions idiomatiques et les métaphores.",
                        "Les supports visuels comme les images ou pictogrammes peuvent faciliter la communication avec votre enfant.",
                        "Soyez patient et laissez suffisamment de temps à votre enfant pour traiter l'information et répondre.",
                        "Établissez un contact visuel si l'enfant est à l'aise avec cela, mais ne l'imposez pas s'il trouve cela difficile."
                    ]
                },
                {
                    "patterns": ["crise", "meltdown", "colère", "agitation", "calmer"],
                    "responses": [
                        "Pendant une crise sensorielle, créez un espace calme avec moins de stimuli (lumière tamisée, pas de bruit).",
                        "Parlez doucement et calmement, sans élever la voix même si l'enfant est agité.",
                        "Proposez des objets sensoriels apaisants comme une balle anti-stress ou une couverture lestée.",
                        "Évitez de toucher l'enfant sans sa permission pendant une crise, cela pourrait aggraver la situation."
                    ]
                },
                {
                    "patterns": ["routine", "changement", "transition", "habitude"],
                    "responses": [
                        "Maintenez une routine prévisible - les enfants autistes se sentent souvent plus en sécurité avec une structure claire.",
                        "Préparez votre enfant aux changements à l'avance avec des supports visuels ou des histoires sociales.",
                        "Utilisez des minuteries visuelles pour faciliter les transitions entre activités.",
                        "Créez un calendrier visuel pour que votre enfant puisse voir ce qui se passera dans la journée ou la semaine."
                    ]
                },
                {
                    "patterns": ["stimming", "comportement répétitif", "balancement", "autostimulation"],
                    "responses": [
                        "Le stimming (mouvements répétitifs) aide votre enfant à gérer ses émotions et sensations. N'essayez pas de l'arrêter s'il n'est pas dangereux.",
                        "Proposez des alternatives acceptables si le comportement de stimming est problématique (ex: remplacer le tapotement bruyant par un coussin sensoriel).",
                        "Les comportements répétitifs sont souvent une façon pour l'enfant de s'autoréguler et de gérer l'anxiété.",
                        "Essayez de comprendre ce qui déclenche ces comportements pour mieux aider votre enfant."
                    ]
                },
                {
                    "patterns": ["école", "apprentissage", "éducation", "classe"],
                    "responses": [
                        "Collaborez étroitement avec les enseignants pour assurer la cohérence entre l'école et la maison.",
                        "Demandez des aménagements spécifiques comme un endroit calme où votre enfant peut se retirer s'il est surstimulé.",
                        "Les supports visuels et les emplois du temps peuvent aider votre enfant à suivre les routines scolaires.",
                        "Certains enfants autistes apprennent mieux avec des approches pratiques et visuelles plutôt que verbales."
                    ]
                },
                {
                    "patterns": ["développement social", "amis", "jouer", "socialisation"],
                    "responses": [
                        "Encouragez les interactions sociales structurées avec des règles claires et des attentes explicites.",
                        "Les groupes de compétences sociales peuvent aider votre enfant à apprendre les codes sociaux dans un environnement sécurisant.",
                        "Commencez par des jeux parallèles (jouer à côté) avant de passer aux jeux coopératifs.",
                        "Valorisez les forces et intérêts de votre enfant pour faciliter les connexions avec d'autres enfants partageant ces intérêts."
                    ]
                },
                {
                    "patterns": ["sensoriel", "sensibilité", "hypersensibilité", "hyposensibilité", "bruit", "toucher"],
                    "responses": [
                        "Identifiez les sensibilités sensorielles spécifiques de votre enfant et adaptez son environnement en conséquence.",
                        "Proposez des écouteurs anti-bruit dans les environnements bruyants si votre enfant est sensible aux sons.",
                        "Respectez les préférences tactiles - certains enfants préfèrent les vêtements doux sans étiquettes, d'autres ont besoin de pressions profondes.",
                        "Créez un 'coin sensoriel' à la maison où votre enfant peut se retirer et réguler ses sensations."
                    ]
                },
                {
                    "patterns": ["autonomie", "indépendance", "compétences de vie", "habillage", "toilette"],
                    "responses": [
                        "Décomposez les tâches quotidiennes en petites étapes avec des instructions visuelles claires.",
                        "Utilisez des séquences d'images pour enseigner des routines comme se brosser les dents ou s'habiller.",
                        "Félicitez les progrès, même minimes, pour encourager l'autonomie.",
                        "Soyez patient et cohérent dans vos attentes concernant l'indépendance."
                    ]
                },
                {
                    "patterns": ["thérapie", "intervention", "aide professionnelle", "spécialiste"],
                    "responses": [
                        "Les interventions précoces comme l'ABA, TEACCH, ou la thérapie d'intégration sensorielle peuvent être bénéfiques.",
                        "L'orthophonie peut aider au développement du langage et des compétences sociales.",
                        "L'ergothérapie peut améliorer la motricité et les défis sensoriels.",
                        "Choisissez des professionnels qui respectent la neurodiversité et travaillent en partenariat avec les familles."
                    ]
                },
                {
                    "patterns": ["frères et sœurs", "fratrie", "famille", "parents"],
                    "responses": [
                        "Expliquez l'autisme aux frères et sœurs de manière adaptée à leur âge.",
                        "Accordez du temps individuel à chaque enfant pour qu'aucun ne se sente négligé.",
                        "Des groupes de soutien pour la fratrie peuvent être très bénéfiques.",
                        "Prenez soin de vous aussi - le bien-être des parents est essentiel pour soutenir tous les membres de la famille."
                    ]
                },
                {
                    "patterns": ["alimentation", "manger", "nourriture", "repas", "difficulté alimentaire"],
                    "responses": [
                        "Respectez les sensibilités sensorielles liées à la nourriture (texture, odeur, goût).",
                        "Introduisez de nouveaux aliments progressivement, aux côtés d'aliments familiers et appréciés.",
                        "Évitez de forcer votre enfant à manger - cela peut créer des associations négatives avec les repas.",
                        "Consultez un ergothérapeute spécialisé ou un diététicien si les difficultés alimentaires sont importantes."
                    ]
                },
                {
                    "patterns": ["sommeil", "dormir", "coucher", "nuit", "insomnie"],
                    "responses": [
                        "Établissez une routine de coucher cohérente et prévisible.",
                        "Créez un environnement de sommeil adapté aux besoins sensoriels (obscurité, silence ou bruit blanc, température).",
                        "Limitez les écrans au moins une heure avant le coucher.",
                        "Une couverture lestée peut aider certains enfants à s'apaiser pour dormir."
                    ]
                }
            ],
            "general": [
                {
                    "patterns": ["bonjour", "salut", "hello", "hey"],
                    "responses": [
                        "Bonjour ! Je suis le chatbot spécialisé sur l'autisme. Comment puis-je vous aider aujourd'hui ?",
                        "Salut ! Je suis là pour répondre à vos questions sur l'interaction avec votre enfant autiste.",
                        "Bonjour ! Avez-vous des questions sur comment mieux communiquer avec votre enfant ?"
                    ]
                },
                {
                    "patterns": ["merci", "thanks", "super", "utile"],
                    "responses": [
                        "Je suis heureux d'avoir pu vous aider. N'hésitez pas si vous avez d'autres questions !",
                        "C'est avec plaisir. Souhaitez-vous des informations sur un autre aspect ?",
                        "De rien ! Votre dévouement envers votre enfant est admirable."
                    ]
                },
                {
                    "patterns": ["qui es tu", "es-tu", "chatbot", "robot"],
                    "responses": [
                        "Je suis un chatbot conçu pour aider les parents d'enfants autistes avec des conseils pratiques et du soutien informationnel.",
                        "Je suis un assistant virtuel spécialisé dans l'autisme. Je ne remplace pas un professionnel, mais je peux vous fournir des informations utiles."
                    ]
                },
                {
                    "patterns": ["autisme c'est quoi", "définition autisme", "qu'est-ce que l'autisme"],
                    "responses": [
                        "L'autisme est un trouble neurodéveloppemental qui affecte la communication sociale et implique des comportements répétitifs et des intérêts restreints. Chaque personne autiste est unique, avec ses propres forces et défis.",
                        "Le trouble du spectre de l'autisme (TSA) est une condition neurologique qui influence la façon dont une personne perçoit le monde et interagit avec les autres. Il se manifeste différemment chez chaque individu."
                    ]
                }
            ]
        }
    
    def _find_best_match(self, user_message, patterns):
        """
        Trouve la meilleure correspondance entre le message de l'utilisateur et les patterns connus
        """
        for word in nltk.word_tokenize(user_message.lower()):
            for pattern in patterns:
                if word in pattern.lower():
                    return True
        return False
    
    def get_rule_based_response(self, message):
        """
        Génère une réponse basée sur des règles prédéfinies et la base de connaissances
        """
        # Rechercher dans les catégories spécifiques
        for category in self.knowledge_base["interaction"]:
            if self._find_best_match(message, category["patterns"]):
                return random.choice(category["responses"])
        
        # Rechercher dans les réponses générales
        for category in self.knowledge_base["general"]:
            if self._find_best_match(message, category["patterns"]):
                return random.choice(category["responses"])
        
        # Réponse par défaut si aucune correspondance
        return "Je ne suis pas sûr de comprendre votre question. Pourriez-vous reformuler ou me demander des conseils sur un sujet spécifique comme la communication, les crises sensorielles, les routines, ou le développement social ?"
    
    def get_model_response(self, message, user_id="default"):
        """
        Génère une réponse en utilisant un modèle de langage pré-entraîné
        """
        if not self.use_transformer:
            return self.get_rule_based_response(message)
        
        # Gérer l'historique des conversations pour ce user_id
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        # Ajouter le message à l'historique
        self.conversation_history[user_id].append(message)
        
        # Limiter l'historique aux 5 derniers messages pour éviter de dépasser la capacité du modèle
        recent_history = self.conversation_history[user_id][-5:]
        
        # Préparer l'entrée pour le modèle
        input_text = " ".join(recent_history)
        inputs = self.tokenizer.encode(input_text + self.tokenizer.eos_token, return_tensors="pt")
        
        # Générer une réponse
        outputs = self.model.generate(
            inputs,
            max_length=150,
            num_return_sequences=1,
            pad_token_id=self.tokenizer.eos_token_id,
            do_sample=True,
            top_k=50,
            top_p=0.95
        )
        
        # Décoder la réponse
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Post-traitement pour extraire uniquement la réponse (pas l'entrée)
        response = response.replace(input_text, "").strip()
        
        # Si la réponse est vide ou trop courte, utiliser le système basé sur des règles
        if not response or len(response) < 10:
            response = self.get_rule_based_response(message)
        
        return response
    
    def get_response(self, message, user_context=None):
        """
        Point d'entrée principal pour obtenir une réponse du chatbot
        """
        user_id = "default"
        if user_context and "user_id" in user_context:
            user_id = user_context["user_id"]
        
        if self.use_transformer:
            return self.get_model_response(message, user_id)
        else:
            return self.get_rule_based_response(message)

# Instance globale du chatbot
_chatbot_instance = None

def get_chatbot_instance():
    """
    Récupère ou crée une instance singleton du chatbot
    """
    global _chatbot_instance
    if _chatbot_instance is None:
        _chatbot_instance = AutismChatbot()
    return _chatbot_instance

def get_chatbot_response(message, context=None):
    """
    Fonction utilitaire pour obtenir une réponse du chatbot
    """
    chatbot = get_chatbot_instance()
    return chatbot.get_response(message, context)