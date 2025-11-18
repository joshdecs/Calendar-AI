import os.path
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


from gemini_call1 import parse_multimodal_content


SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

# FONCTION D'AUTHENTIFICATION 

def authenticate_google_calendar():
    """Gère l'authentification OAuth2.0."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0) 
        
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    
    return creds


# FONCTION DE CRÉATION D'ÉVÉNEMENT 


def create_calendar_event(service, event_details):
    """Crée un événement en utilisant les détails analysés par Gemini."""
    
    start_time_iso = event_details.get('start_datetime')
    end_time_iso = event_details.get('end_datetime')
    timezone = 'America/Toronto' 
    
    event = {
        'summary': event_details.get('summary', 'Nouvel événement'),
        'description': 'Ajouté via votre Gemini Pipeline personnel.',
        'start': {
            'dateTime': start_time_iso,
            'timeZone': timezone, 
        },
        'end': {
            'dateTime': end_time_iso,
            'timeZone': timezone,
        },
        'reminders': {'useDefault': True},
    }

    try:
        event = service.events().insert(calendarId='primary', body=event).execute()
        print(f"\n✅ Événement Gemini créé: {event.get('htmlLink')}")
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'événement Google Calendar : {e}")



# FONCTION PRINCIPALE 

def main():
    # 1. Authentification
    creds = authenticate_google_calendar()
    service = build("calendar", "v3", credentials=creds)

    # 2. Entrée utilisateur et sélection multimodale
    print("\n=======================================================")
    print("🤖 Agent de planification : Prêt à recevoir votre requête.")
    print("=======================================================")
    
    file_path = None
    
    # Demander si l'utilisateur veut uploader un fichier
    use_file = input("Voulez-vous analyser un fichier (audio/doc) ? (y/n) : ").lower().strip()
    if use_file == 'y':
        file_path = input("Entrez le chemin complet du fichier (ex: C:/Users/Docs/horaire.pdf) : ").strip()
        if not os.path.exists(file_path):
            print(f"❌ Fichier non trouvé à : {file_path}. Retour à l'entrée texte.")
            file_path = None

    # Obtenir la requête texte ou l'instruction
    if file_path:
        user_input = input("Ajoutez une instruction pour le document (ex: 'Planifie tous les événements après 14h') :\n> ")
    else:
        user_input = input("Entrez votre requête (ex: 'Rdv client mardi à 10h pour 1h30') :\n> ")
        if not user_input.strip():
            print("❌ Opération annulée : Aucune entrée fournie.")
            return

    # 3. Analyse PNL/Multimodale via Gemini
    print("\n⏳ Analyse multimodale en cours par Gemini...")
    all_events_details = parse_multimodal_content(user_input, file_path=file_path)
    
    # 4. Création des événements (Boucle)
    if all_events_details and isinstance(all_events_details, list):
        print(f"✅ Analyse réussie. {len(all_events_details)} événement(s) trouvé(s).")
        
        for i, event_details in enumerate(all_events_details):
            print(f"\n--- Création Événement {i+1}/{len(all_events_details)} ---")
            print(f"   - Résumé: {event_details.get('summary')}")
            print(f"   - Début:  {event_details.get('start_datetime')}")
            
            # Utilisation de la fonction existante
            create_calendar_event(service, event_details)
    else:
        print("❌ Opération annulée : Aucune structure d'événement valide retournée par Gemini.")

if __name__ == "__main__":
    main()
