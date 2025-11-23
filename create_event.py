import os.path
import json
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

TIMEZONE = 'America/Toronto'
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

def authenticate_google_calendar():
    creds = None
    
    token_json_str = os.environ.get("TOKEN_JSON")
    if token_json_str:
        try:
            token_dict = json.loads(token_json_str)
            creds = Credentials.from_authorized_user_info(token_dict, SCOPES)
        except json.JSONDecodeError:
            creds = None
    
    if not creds and os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                raise Exception(f"Échec du rafraîchissement du jeton Google. L'authentification a échoué. Détails : {e}")

        elif not os.environ.get("TOKEN_JSON"):
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

def create_calendar_event(service, event_details):
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
        event = service.events().insert(calendarId='primary', body=event).execute()
        return event 
        
    except Exception as e:
        raise

def main():
    if os.environ.get("TOKEN_JSON"):
        return

    try:
        creds = authenticate_google_calendar()
    except Exception as e:
        return

    service = build("calendar", "v3", credentials=creds)

    user_input = input("\nEntrez votre requête (ex: 'Rdv client mardi à 10h pour 1h30'):\n> ")
    
    # Cet appel ne fonctionnera pas sans l'import de parse_multimodal_content
    # event_details = parse_multimodal_content(user_input) 
    
    # if event_details:
    #     create_calendar_event(service, event_details)

if __name__ == "__main__":
    main()