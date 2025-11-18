
# 🤖 Calendar-Auto-Agent (Gemini Pipeline)

**Un agent d'automatisation intelligent pour Google Calendar**,
utilisant l'IA multimodale de **Gemini** pour créer automatiquement des
événements à partir de texte, d'audio ou de documents (images, PDFs).

<p align="center">
```
<img src="https://img.shields.io/badge/Backend-Python-3776AB.svg">
<img src="https://img.shields.io/badge/AI_Engine-Gemini-4285F4.svg">
<img src="https://img.shields.io/badge/API-Google_Calendar-4285F4.svg">
<img src="https://img.shields.io/badge/Status-In_Progress-yellow.svg">
<img src="https://img.shields.io/badge/Version-V0.2_PNL_Core-orange.svg">

</p>
```

------------------------------------------------------------------------

## 🎯 Aperçu du Projet

**Calendar-Auto-Agent** vise à éliminer totalement la création manuelle
d'événements dans Google Calendar.\
Grâce à un pipeline intelligent, l'application :

-   Analyse une requête textuelle, vocale ou un document (photo de
    planning, PDF...)
-   Extrait automatiquement les informations clés
-   Formate un événement conforme à l'API Google Calendar
-   Insère l'événement directement dans l'agenda de l'utilisateur

L'objectif final : **une app web/mobile** permettant à l'utilisateur de
simplement *parler* ou *téléverser un document*, et l'événement est créé
instantanément.

------------------------------------------------------------------------

## 🧩 Architecture Actuelle (Version 0.2)

### 1. 🟦 Google Calendar API --- `create_event.py`

-   Authentification OAuth 2.0 via `credentials.json` et `token.json`
-   Création d'un événement dans le calendrier principal
-   Formatage ISO 8601 conforme aux exigences Google

### 2. 🧠 Gemini PNL Core --- `gemini_call1.py`

-   Pipeline **Texte → JSON structuré**
-   Sortie imposée via un schéma strict (titre, start, end)
-   Gestion intelligente des dates :
    -   Fuseau horaire : **America/Toronto**
    -   Gestion des durées implicites
    -   Gestion des chevauchements de jours (ex. : 22h → 3h)
-   Sécurité : charge la clé API depuis `.env` via `python-dotenv`

------------------------------------------------------------------------

## ⏭️ Feuille de Route

  ------------------------------------------------------------------------------
  Étape               Description             Fichiers concernés
  ------------------- ----------------------- ----------------------------------
  **3. Intégration    Support des entrées     gemini_call1.py
  multimodale**       audio, image, PDF.      
                      Extraction              
                      automatique + envoi au  
                      module PNL.             

  **4. Déploiement    Transformation en API   app.py / main.py
  Web                 REST accessible en      
  (Flask/FastAPI)**   ligne.                  

  **5. Interface      Frontend simple avec    frontend/ (HTML, JS)
  Utilisateur**       enregistrement vocal +  
                      upload de documents.    
  ------------------------------------------------------------------------------

------------------------------------------------------------------------

## 🧰 Installation & Exécution (V0.2)

### Prérequis

-   Python **3.10+**

-   Une clé API Google Calendar : fichier `credentials.json`

-   Une clé Gemini dans `.env` :

        GEMINI_API_KEY=...

-   Dépendances :

    ``` bash
    pip install google-api-python-client google-genai python-dotenv
    ```

### Lancement

``` bash
python create_event.py
```

Lors de la première utilisation, une page d'authentification Google
s'ouvrira automatiquement.

------------------------------------------------------------------------

## 📌 Structure du Projet

    .
    ├── create_event.py        # Gestion Google Calendar API
    ├── gemini_call1.py        # Pipeline IA texte → JSON
    ├── token.json             # Token OAuth2 (créé automatiquement)
    ├── credentials.json       # Identifiants Google OAuth
    ├── .env                   # Clé API Gemini
    └── README.md

------------------------------------------------------------------------

## 🤝 Contributions

Les contributions sont les bienvenues !\
Propositions d'améliorations, issues ou pull requests --- tout est
apprécié.

------------------------------------------------------------------------

## 📜 Licence

Ajoutez ici votre licence (MIT, GPL, Apache 2.0...)
