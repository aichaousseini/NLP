# NLP
# DialogAI 💬

Une application intelligente de chatbot multilingue avec résumé automatique et synthèse vocale, développée avec Streamlit.

![DialogAI](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 🌟 Fonctionnalités

- **💬 Chat IA Intelligent** : Conversez avec un modèle d'IA avancé (Gemma2-9b-It)
- **🌍 Support Multilingue** : Détection automatique et réponses en français/anglais
- **📝 Résumé Automatique** : Génération de résumés concis de vos conversations
- **🔊 Synthèse Vocale** : Conversion des résumés en audio téléchargeable
- **🎨 Interface Moderne** : Interface utilisateur élégante et responsive
- **🔒 Sécurité** : Aucune sauvegarde des clés API ou données personnelles

## 🚀 Démonstration

L'application offre un workflow complet :
1. **Chat** avec l'IA pour obtenir des réponses détaillées
2. **Résumé** automatique des réponses importantes
3. **Audio** pour écouter les résumés via synthèse vocale

## 📋 Prérequis

- Python 3.8 ou supérieur
- Clé API Groq (pour le chat IA)
- Clé API Hugging Face (pour les résumés)

## 🛠️ Installation

1. **Clonez le repository**
```bash
git clone https://github.com/votre-username/DialogAI.git
cd DialogAI
```

2. **Installez les dépendances**
```bash
pip install -r requirements.txt
```

3. **Lancez l'application**
```bash
streamlit run app.py
```

## 📦 Dépendances

```
streamlit
requests
gtts
groq
python-dotenv
langdetect
```

## 🔑 Configuration des API

### Groq API
1. Créez un compte sur [Groq Console](https://console.groq.com/signup)
2. Générez une clé API dans la section "API Keys"
3. Saisissez la clé dans l'interface de l'application

### Hugging Face API
1. Créez un compte sur [Hugging Face](https://huggingface.co/join)
2. Générez un token dans Settings > Access Tokens
3. Saisissez le token dans l'interface de l'application

## 💡 Utilisation

### 1. Configuration
- Lancez l'application avec `streamlit run app.py`
- Configurez vos clés API dans la barre latérale
- Les clés sont sécurisées et non sauvegardées

### 2. Chat IA
- Naviguez vers la section "Chat"
- Posez vos questions en français ou anglais
- L'IA détecte automatiquement la langue et répond en conséquence
- Les réponses sont nettoyées de toute balise HTML parasite

### 3. Génération de résumés
- Après une réponse du chat, cliquez sur "Résumer cette réponse"
- Le système génère automatiquement un résumé concis
- Utilisez le modèle BART de Facebook pour des résumés de qualité

### 4. Synthèse vocale
- Convertissez vos résumés en audio
- Modifiez le texte si nécessaire avant la conversion
- Écoutez directement ou téléchargez le fichier MP3

## 🏗️ Architecture

```
DialogAI/
├── app.py                 # Application principale Streamlit
├── requirements.txt       # Dépendances Python
├── README.md             # Documentation
└── .env.example          # Exemple de fichier d'environnement
```

## 🔧 Technologies utilisées

- **Frontend** : Streamlit avec CSS personnalisé
- **Chat IA** : Groq API avec modèle Gemma2-9b-It
- **Résumé** : Hugging Face API avec BART-large-CNN
- **Synthèse vocale** : Google Text-to-Speech (gTTS)
- **Détection de langue** : langdetect

## 🎨 Fonctionnalités techniques

- **Nettoyage automatique** des réponses HTML
- **Détection de langue** automatique (français/anglais)
- **Interface responsive** avec animations CSS
- **Gestion d'état** Streamlit pour une navigation fluide
- **Sécurité** : pas de persistence des clés API

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Forkez le projet
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Poussez vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request


## 👨‍💻 Auteur

**AICHA OUSSEINI**

## 🙏 Remerciements

- [Streamlit](https://streamlit.io/) pour le framework web
- [Groq](https://groq.com/) pour l'API de chat IA
- [Hugging Face](https://huggingface.co/) pour l'API de résumé
- [Google](https://cloud.google.com/text-to-speech) pour la synthèse vocale

## 📊 Roadmap
---

⭐ N'oubliez pas de donner une étoile au projet si vous l'aimez !
