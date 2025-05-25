import os
import io
import streamlit as st
import requests
from gtts import gTTS
from groq import Groq
from dotenv import load_dotenv
import langdetect
import re

# Chargement des variables d'environnement
load_dotenv()

# Configuration de la page
st.set_page_config(
    page_title="DialogAI",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour améliorer l'apparence
st.markdown("""
<style>
    .main-header {
        font-size: 3rem !important;
        color: #1E90FF;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem !important;
        color: #4682B4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .author {
        font-size: 1.2rem !important;
        color: #6495ED;
        text-align: center;
        font-style: italic;
        margin-bottom: 2rem;
    }
    .menu-item {
        background-color: #f0f8ff;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 15px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        transition: transform 0.3s;
    }
    .menu-item:hover {
        transform: scale(1.02);
        box-shadow: 3px 3px 7px rgba(0,0,0,0.2);
    }
    .api-input {
        background-color: #f9f9f9;
        padding: 15px;
        border-radius: 5px;
        margin-top: 10px;
        margin-bottom: 20px;
    }
    .chat-message {
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .user-message {
        background-color: #e6f7ff;
        text-align: right;
    }
    .bot-message {
        background-color: #f0f0f0;
    }
    .result-container {
        background-color: #f5f5f5;
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
        margin-bottom: 20px;
    }
    .tooltip {
        position: relative;
        display: inline-block;
        border-bottom: 1px dotted black;
    }
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: #555;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
</style>
""", unsafe_allow_html=True)

# Fonction pour nettoyer les réponses du chatbot (enlever les balises HTML parasites)
def clean_bot_response(response):
    """
    Nettoie la réponse du chatbot en supprimant les balises HTML parasites
    """
    # Supprimer les balises div, span et autres balises HTML communes
    cleaned = re.sub(r'</?div[^>]*>', '', response)
    cleaned = re.sub(r'</?span[^>]*>', '', cleaned)
    cleaned = re.sub(r'</?p[^>]*>', '', cleaned)
    cleaned = re.sub(r'</?br[^>]*>', '', cleaned)
    
    # Supprimer les balises HTML restantes de manière générale
    cleaned = re.sub(r'<[^>]+>', '', cleaned)
    
    # Nettoyer les espaces multiples
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned

# Initialisation des variables de session si elles n'existent pas
if 'last_response' not in st.session_state:
    st.session_state.last_response = ""
if 'summary_text' not in st.session_state:
    st.session_state.summary_text = ""
if 'current_page' not in st.session_state:
    st.session_state.current_page = "accueil"
# Suppression de la persistence des clés API
if 'groq_api_key' not in st.session_state:
    st.session_state.groq_api_key = ""
if 'hf_api_key' not in st.session_state:
    st.session_state.hf_api_key = ""

# Barre latérale avec navigation
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/chat.png", width=100)
    
    st.subheader("Navigation")
    if st.button("🏠 Accueil", key="nav_accueil"):
        st.session_state.current_page = "accueil"
        st.rerun()
    
    # Section API avec saisie obligatoire à chaque session
    st.subheader("🔑 Clés API")
    
    st.session_state.groq_api_key = st.text_input("🤖 Clé API Groq", 
                                                  value="", 
                                                  type="password",
                                                  placeholder="Saisissez votre clé API Groq",
                                                  help="Nécessaire pour le chat avec l'IA")
    
    st.session_state.hf_api_key = st.text_input("🤗 Clé API Hugging Face", 
                                                value="", 
                                                type="password",
                                                placeholder="Saisissez votre clé API HF",
                                                help="Nécessaire pour la génération de résumés")
    
    # Indicateurs de statut des API (seulement si les clés sont présentes)
    if st.session_state.groq_api_key:
        st.success("✅ Clé Groq configurée")
        
    if st.session_state.hf_api_key:
        st.success("✅ Clé HF configurée")
    
    st.markdown("---")
    
    # Autres boutons de navigation
    if st.button("💬 Chat", key="nav_chat"):
        st.session_state.current_page = "chat"
        st.rerun()
    if st.button("📝 Résumé", key="nav_resume"):
        st.session_state.current_page = "resume"
        st.rerun()
    if st.button("🔊 Audio", key="nav_audio"):
        st.session_state.current_page = "audio"
        st.rerun()
    if st.button("⚙️ Configuration", key="nav_config"):
        st.session_state.current_page = "config"
        st.rerun()

# Page d'accueil
if st.session_state.current_page == "accueil":
    st.markdown("<h1 class='main-header'>Bienvenue sur DialogAI</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    <p class='sub-header'>Une application intelligente qui vous permet de discuter avec un chatbot, 
    de résumer les conversations et de les écouter grâce à la synthèse vocale.</p>
    """, unsafe_allow_html=True)
    
    st.markdown("<p class='author'>✨ Fonctionnalités  </p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class='menu-item'>
            <h3>💬 Chat avec IA</h3>
            <p>Discutez avec un modèle d'IA avancé et obtenez des réponses intelligentes à vos questions.</p>
            <br>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Accéder au Chat", key="btn_chat"):
            st.session_state.current_page = "chat"
            st.rerun()
            
    with col2:
        st.markdown("""
        <div class='menu-item'>
            <h3>📝 Résumé de texte</h3>
            <p>Générez automatiquement un résumé concis de vos conversations avec l'IA.</p>
            <br>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Créer un résumé", key="btn_resume"):
            st.session_state.current_page = "resume"
            st.rerun()
            
    with col3:
        st.markdown("""
        <div class='menu-item'>
            <h3>🔊 Synthèse vocale</h3>
            <p>Écoutez les résumés de vos conversations grâce à la technologie de synthèse vocale.</p>
            <br>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Écouter en audio", key="btn_audio"):
            st.session_state.current_page = "audio"
            st.rerun()

# Page de chat
elif st.session_state.current_page == "chat":
    st.title("💬 Chat avec IA")
    
    st.info("Cette page vous permet de discuter avec un modèle d'IA avancé. Posez vos questions et obtenez des réponses détaillées.")
    
    # Vérification de la clé API
    if not st.session_state.groq_api_key:
        st.error("❌ Clé API Groq manquante. Veuillez la configurer dans la barre latérale.")
    else:
        # Interface de chat
        message = st.text_input("Entrez votre message:", key="chat_input")
        
        # Modèle fixé à Gemma2-9b-It
        model = "gemma2-9b-it"
        
        if st.button("Envoyer", key="send_chat"):
            if message:
                try:
                    # Utiliser le client Groq pour obtenir une réponse
                    client = Groq(api_key=st.session_state.groq_api_key)
                    
                    # Détecter la langue du message
                    try:
                        langue_message = langdetect.detect(message)
                    except:
                        langue_message = 'fr'  # Par défaut en français en cas d'erreur
                    
                    # Créer un système prompt qui demande de répondre dans la même langue
                    system_prompt = ""
                    if langue_message == 'en':
                        system_prompt = "Please respond in English to the user's queries. Provide clear and helpful responses without any HTML tags or formatting."
                    else:
                        system_prompt = "Veuillez répondre en français aux questions de l'utilisateur. Fournissez des réponses claires et utiles sans balises HTML ou formatage."
                    
                    chat_completion = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": message}
                        ],
                        model=model
                    )
                    
                    # Nettoyer la réponse du bot et la stocker
                    bot_response = chat_completion.choices[0].message.content
                    cleaned_response = clean_bot_response(bot_response)
                    st.session_state.last_response = cleaned_response
                    
                    # Afficher la réponse
                    st.markdown(f"""
                    <div class='result-container'>
                        <h4>Réponse:</h4>
                        <p>{cleaned_response}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"Erreur lors de la communication avec l'API Groq: {str(e)}")
        
        # Bouton pour résumer la dernière réponse
        if st.session_state.last_response:
            if st.button("📝 Résumer cette réponse", key="go_to_summary"):
                if st.session_state.hf_api_key:
                    st.session_state.current_page = "resume"
                    st.rerun()
                else:
                    st.error("❌ Clé API Hugging Face manquante pour générer un résumé.")

# Page de résumé
elif st.session_state.current_page == "resume":
    st.title("📝 Résumé de conversation")
    
    st.info("Cette page vous permet de résumer la dernière réponse de l'IA pour en extraire les points essentiels.")
    
    # Vérification de la clé API
    if not st.session_state.hf_api_key:
        st.error("❌ Clé API Hugging Face manquante. Veuillez la configurer dans la barre latérale.")
    else:
        # Vérification qu'il y a une réponse à résumer
        if st.session_state.last_response:
            if st.button("🔄 Générer le résumé", key="generate_summary"):
                try:
                    with st.spinner("Génération du résumé en cours..."):
                        # Appel à l'API Hugging Face pour le résumé
                        API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
                        headers = {"Authorization": f"Bearer {st.session_state.hf_api_key}"}
                        
                        # Détecter la langue du texte
                        try:
                            langue_texte = langdetect.detect(st.session_state.last_response)
                        except:
                            langue_texte = 'fr'  # Par défaut en français en cas d'erreur
                        
                        # Utiliser des instructions spécifiques à la langue pour le résumé
                        prompt = st.session_state.last_response
                        if langue_texte == 'fr':
                            prompt = "Résumez ce texte en français: " + st.session_state.last_response
                        elif langue_texte == 'en':
                            prompt = "Summarize this text in English: " + st.session_state.last_response
                        
                        response = requests.post(
                            API_URL, 
                            headers=headers, 
                            json={"inputs": prompt}
                        )
                        
                        output = response.json()
                        
                        if isinstance(output, list) and len(output) > 0 and 'summary_text' in output[0]:
                            st.session_state.summary_text = output[0]['summary_text']
                            
                            st.markdown("<div class='result-container'>", unsafe_allow_html=True)
                            st.subheader("✅ Résumé de la réponse")
                            st.write(st.session_state.summary_text)
                            st.markdown("</div>", unsafe_allow_html=True)
                            
                        else:
                            st.error(f"Erreur lors de la génération du résumé. Réponse de l'API: {output}")
                
                except Exception as e:
                    st.error(f"Erreur lors de la communication avec l'API Hugging Face: {str(e)}")
            
            # Boutons d'action si un résumé existe
            if st.session_state.summary_text:
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔊 Convertir en audio", key="audio_convert_btn"):
                        st.session_state.current_page = "audio"
                        st.rerun()
                with col2:
                    if st.button("💬 Revenir au chat", key="back_to_chat"):
                        st.session_state.current_page = "chat"
                        st.rerun()
        else:
            st.warning("Aucune réponse à résumer. Veuillez d'abord poser une question au chatbot.")
            
            if st.button("💬 Aller au chat", key="goto_chat_from_resume"):
                if st.session_state.groq_api_key:
                    st.session_state.current_page = "chat"
                    st.rerun()
                else:
                    st.error("❌ Clé API Groq manquante pour accéder au chat.")

# Page d'audio
elif st.session_state.current_page == "audio":
    st.title("🔊 Synthèse vocale")
    
    st.info("Cette page vous permet de convertir le résumé de votre conversation en audio et de l'écouter.")
    
    if st.session_state.summary_text:
        st.subheader("Texte à convertir en audio")
        speech_text = st.text_area("Vous pouvez modifier le texte avant de générer l'audio:", value=st.session_state.summary_text, height=200)
        
        # Détection automatique de la langue (français ou anglais)
        try:
            langue = langdetect.detect(speech_text)
            if langue == 'fr':
                langue_affichee = "Français"
            elif langue == 'en':
                langue_affichee = "Anglais"
            else:
                # Par défaut, utiliser le français si la langue n'est ni française ni anglaise
                langue = 'fr'
                langue_affichee = "Français (par défaut)"
                
            st.info(f"🌐 Langue détectée: {langue_affichee}")
        except:
            # En cas d'erreur de détection, utiliser le français par défaut
            langue = 'fr'
            st.info("🌐 Langue détectée: Français (par défaut)")
        
        # Bouton pour générer l'audio
        if st.button("🔄 Générer l'audio", key="generate_audio"):
            if speech_text.strip() == "":
                st.warning("❗ Veuillez entrer un texte.")
            else:
                try:
                    with st.spinner("Génération de l'audio en cours..."):
                        # Génération de l'audio
                        tts = gTTS(text=speech_text, lang=langue, slow=False)
                        
                        # Sauvegarde dans un buffer mémoire
                        audio_bytes_io = io.BytesIO()
                        tts.write_to_fp(audio_bytes_io)
                        audio_bytes_io.seek(0)
                        
                        st.markdown("<div class='result-container'>", unsafe_allow_html=True)
                        st.subheader("🎵 Écoutez le résumé")
                        
                        # Affichage de l'audio dans l'application
                        st.audio(audio_bytes_io, format="audio/mp3")
                        
                        # Bouton de téléchargement
                        st.download_button(
                            label="⬇️ Télécharger l'audio",
                            data=audio_bytes_io,
                            file_name="dialogue_resume.mp3",
                            mime="audio/mp3"
                        )
                        st.markdown("</div>", unsafe_allow_html=True)
                
                except Exception as e:
                    st.error(f"Erreur lors de la génération de l'audio: {str(e)}")
        
        # Navigation
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📝 Revenir au résumé", key="back_to_summary"):
                st.session_state.current_page = "resume"
                st.rerun()
        with col2:
            if st.button("💬 Revenir au chat", key="back_to_chat_from_audio"):
                st.session_state.current_page = "chat"
                st.rerun()
    else:
        st.warning("Aucun résumé à convertir en audio. Veuillez d'abord générer un résumé.")
        
        if st.button("📝 Aller au résumé", key="goto_resume_from_audio"):
            if st.session_state.hf_api_key:
                st.session_state.current_page = "resume"
                st.rerun()
            else:
                st.error("❌ Clé API Hugging Face manquante pour générer un résumé.")

# Page de configuration
elif st.session_state.current_page == "config":
    st.title("⚙️ Configuration de l'application")
    
    st.info("Cette page vous permet de configurer l'application et d'apprendre à l'utiliser efficacement.")
    
    # Configuration des API
    st.header("🔑 Configuration des clés API")
    
    st.markdown("""
    Pour utiliser toutes les fonctionnalités de DialogAI, vous devez configurer deux clés API à chaque session:
    
    1. **Clé API Groq**: Nécessaire pour le chat avec l'IA
    2. **Clé API Hugging Face**: Nécessaire pour la génération de résumés
    
    🔒 **Sécurité**: Vos clés API ne sont jamais sauvegardées et restent privées.
    """)
    
    with st.expander("🤖 Comment obtenir une clé API Groq"):
        st.markdown("""
        1. Créez un compte sur [Groq Console](https://console.groq.com/signup)
        2. Une fois connecté, accédez à votre profil
        3. Allez dans la section "API Keys"
        4. Cliquez sur "Create API Key"
        5. Copiez la clé générée et collez-la dans le champ correspondant dans la barre latérale
        """)
    
    with st.expander("🤗 Comment obtenir une clé API Hugging Face"):
        st.markdown("""
        1. Créez un compte sur [Hugging Face](https://huggingface.co/join)
        2. Une fois connecté, accédez à votre profil
        3. Allez dans la section "Settings" puis "Access Tokens"
        4. Cliquez sur "New token"
        5. Donnez un nom à votre token et sélectionnez les permissions appropriées
        6. Copiez le token généré et collez-le dans le champ correspondant dans la barre latérale
        """)
    
    st.markdown("---")
    
    # Guide d'utilisation
    st.header("📚 Guide d'utilisation")
    
    tabs = st.tabs(["🚀 Démarrage", "💬 Chat", "📝 Résumé", "🔊 Audio", "💡 Conseils"])
    
    with tabs[0]:
        st.subheader("Comment démarrer avec DialogAI")
        st.markdown("""
        1. **Configuration des API**: Commencez par configurer vos clés API dans la barre latérale
        2. **Navigation**: Utilisez les boutons de la barre latérale pour naviguer entre les différentes fonctionnalités
        3. **Workflow**: Suivez le processus logique: Chat → Résumé → Audio
        4. **Sécurité**: Vos clés ne sont pas sauvegardées, saisissez-les à chaque session
        """)
    
    with tabs[1]:
        st.subheader("Utilisation du chat")
        st.markdown("""
        1. Accédez à la page Chat depuis la barre latérale
        2. Le modèle d'IA utilisé est Gemma2-9b-It
        3. Tapez votre message dans le champ de saisie (en français ou en anglais)
        4. L'assistant détecte automatiquement la langue et répond dans la même langue
        5. Cliquez sur "Envoyer" pour obtenir une réponse propre et bien formatée
        6. Vous pouvez résumer la réponse directement
        """)
    
    with tabs[2]:
        st.subheader("Création de résumés")
        st.markdown("""
        1. Après avoir reçu une réponse du chat, cliquez sur "Résumer cette réponse"
        2. Accédez à la page Résumé
        3. Cliquez sur "Générer le résumé" pour créer un résumé concis
        4. Le résumé s'affichera directement
        5. Utilisez le bouton "Convertir en audio" pour passer à l'étape suivante
        """)
    
    with tabs[3]:
        st.subheader("Conversion en audio")
        st.markdown("""
        1. Après avoir généré un résumé, accédez à la page Audio
        2. Vous verrez le texte du résumé
        3. Vous pouvez modifier le texte avant de générer l'audio
        4. La langue est détectée automatiquement (français ou anglais)
        5. Cliquez sur "Générer l'audio" pour créer un fichier audio
        6. Écoutez l'audio directement ou téléchargez-le
        """)
    
    with tabs[4]:
        st.subheader("Conseils et astuces")
        st.markdown("""
        - **Pour de meilleurs résumés**: Assurez-vous que la réponse du chat soit claire et bien structurée
        - **Performances du chat**: Les réponses peuvent prendre quelques secondes selon la complexité de votre question
        - **Qualité audio**: La synthèse vocale fonctionne mieux avec des textes bien ponctués
        - **Sécurité**: Vos clés API ne sont jamais sauvegardées pour votre protection
        - **Navigation**: Tous les boutons de navigation fonctionnent correctement entre les pages
        """)
    
    st.markdown("---")
    
    # À propos
    st.header("ℹ️ À propos de DialogAI")
    st.markdown("""
    DialogAI est une application bilingue (français/anglais) qui intègre plusieurs technologies d'IA:
    
    - **Chat IA**: Utilise le modèle Gemma2-9b-It via l'API Groq pour générer des réponses intelligentes et propres
    - **Résumé automatique**: Utilise le modèle BART de Facebook via l'API Hugging Face
    - **Synthèse vocale**: Utilise la bibliothèque gTTS (Google Text-to-Speech)
    
    🔒 **Sécurité et confidentialité**: L'application ne sauvegarde aucune donnée personnelle ni clé API.
    
    L'application détecte automatiquement la langue utilisée et adapte ses réponses en conséquence.
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #777;">
    <p>© 2025 DialogAI | Développé avec ❤️ par AICHA OUSSEINI</p>
   
</div>
""", unsafe_allow_html=True)