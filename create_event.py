import os.path
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


from gemini_call1 import parse_text_with_gemini 

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

    user_input = input("\n🎙️ Dites-moi l'événement à planifier (ex: 'rendez-vous chez le dentiste le 20 mars à 9h'):\n> ")
    
    print("\n⏳ Analyse en cours par Gemini...")
    event_details = parse_text_with_gemini(user_input)
    
    if event_details:
        print("✅ Analyse réussie. Détails structurés :")
        print(f"   - Résumé: {event_details.get('summary')}")
        print(f"   - Début:  {event_details.get('start_datetime')}")
        
        create_calendar_event(service, event_details)
    else:
        print("❌ Opération annulée car l'analyse Gemini a échoué ou n'a pas pu structurer les données.")

if __name__ == "__main__":
    main()