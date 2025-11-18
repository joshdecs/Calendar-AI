import os.path
import json
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from gemini_call1 import parse_multimodal_content 

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]
TIMEZONE = 'America/Toronto' 


# A. FONCTION D'AUTHENTIFICATION (Mise à jour pour le serveur Railway)

def authenticate_google_calendar():
    """
    Gère l'authentification OAuth2.0. 
    Priorise la lecture du jeton depuis la variable d'environnement (serveur).
    Utilise le fichier local (token.json) si l'environnement n'est pas trouvé (local).
    """
    creds = None
    
    token_json_str = os.environ.get("TOKEN_JSON")
    if token_json_str:
        print("Authentification : Lecture du jeton depuis l'environnement (serveur).")
        try:
            token_dict = json.loads(token_json_str)
            creds = Credentials.from_authorized_user_info(token_dict, SCOPES)
        except json.JSONDecodeError:
            print("Erreur: La variable TOKEN_JSON n'est pas un JSON valide.")
            creds = None
    
    if not creds and os.path.exists("token.json"):
        print("Authentification : Lecture du jeton depuis le fichier local.")
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Authentification : Jetons expirés, rafraîchissement.")
            creds.refresh(Request())
        elif not os.environ.get("TOKEN_JSON"): # Seulement si on n'est pas sur le serveur
            print("Authentification : Démarrage du flux interactif (navigateur).")
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
            
        if creds and not os.environ.get("TOKEN_JSON"):
            with open("token.json", "w") as token:
                token.write(creds.to_json())

    if not creds:
        raise Exception("Échec de l'authentification : Aucun jeton valide trouvé.")
        
    return creds

# B. FONCTION DE CRÉATION D'ÉVÉNEMENT (Retourne l'objet)

def create_calendar_event(service, event_details):
    """Crée un événement en utilisant les détails analysés par Gemini et retourne le résultat de l'API."""
    
    start_time_iso = event_details.get('start_datetime')
    end_time_iso = event_details.get('end_datetime')
    
    event = {
        'summary': event_details.get('summary', 'Nouvel événement'),
        'description': 'Ajouté via votre Gemini Pipeline personnel.',
        'start': {
            'dateTime': start_time_iso,
            'timeZone': TIMEZONE, 
        },
        'end': {
            'dateTime': end_time_iso,
            'timeZone': TIMEZONE,
        },
        'reminders': {'useDefault': True},
    }

    try:
        # Appel de l'API pour insérer l'événement
        event = service.events().insert(calendarId='primary', body=event).execute()
        print(f"✅ Événement Gemini créé: {event.get('htmlLink')}")
        
        # Retourner l'objet événement complet pour l'API web
        return event 
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'événement Google Calendar : {e}")
        raise # Relance l'exception pour que FastAPI puisse la gérer


# C. FONCTION PRINCIPALE (Interface Console pour le test local)

def main():
    if os.environ.get("TOKEN_JSON"):
        print("Le mode console est désactivé lorsque TOKEN_JSON est défini (mode serveur).")
        return

    try:
        creds = authenticate_google_calendar()
    except Exception as e:
        print(f"Erreur fatale : {e}")
        return

    service = build("calendar", "v3", credentials=creds)

    print("\n=======================================================")
    print("🤖 Agent de planification : Prêt à recevoir votre requête.")
    print("=======================================================")
    
    file_path = None
    
    use_file = input("Voulez-vous analyser un fichier (pour tester le multimodal) ? (y/n) : ").lower().strip()
    if use_file == 'y':
        file_path = input("Entrez le chemin complet du fichier (ex: C:/Users/Docs/horaire.pdf) : ").strip()
        if not os.path.exists(file_path):
            print(f"❌ Fichier non trouvé à : {file_path}. Retour à l'entrée texte.")
            file_path = None

    if file_path:
        user_input = input("Ajoutez une instruction pour le document (ex: 'Planifie tous les événements') :\n> ")
    else:
        user_input = input("Entrez votre requête (ex: 'Rdv client mardi à 10h pour 1h30') :\n> ")
        if not user_input.strip():
            print("❌ Opération annulée : Aucune entrée fournie.")
            return

    print("\n⏳ Analyse multimodale en cours par Gemini...")
    all_events_details = parse_multimodal_content(user_input, file_path=file_path)
    
    if all_events_details and isinstance(all_events_details, list):
        print(f"✅ Analyse réussie. {len(all_events_details)} événement(s) trouvé(s).")
        
        for i, event_details in enumerate(all_events_details):
            print(f"\n--- Création Événement {i+1}/{len(all_events_details)} ---")
            print(f"   - Résumé: {event_details.get('summary')}")
            print(f"   - Début:  {event_details.get('start_datetime')}")
            
            create_calendar_event(service, event_details)
    else:
        print("❌ Opération annulée : Aucune structure d'événement valide retournée par Gemini.")

if __name__ == "__main__":
    main()