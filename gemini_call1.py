import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv # <-- NOUVEAU

# Charge les variables d'environnement du fichier .env
load_dotenv()
# La clé Gemini est lue automatiquement si elle est définie dans l'environnement (GEMINI_API_KEY)
client = genai.Client() 

# ----------------------------------------------------------------------
# DÉFINITION DU SCHÉMA JSON POUR L'EXTRACTION
# ----------------------------------------------------------------------
CALENDAR_EVENT_SCHEMA = {
  "type": "object",
  "properties": {
    "summary": {"type": "string", "description": "Titre ou résumé de l'événement en français, nettoyé des détails de date/heure."},
    "start_datetime": {"type": "string", "description": "Heure de début au format YYYY-MM-DDTHH:MM:SS (ISO 8601)."},
    "end_datetime": {"type": "string", "description": "Heure de fin au format YYYY-MM-DDTHH:MM:SS (ISO 8601)."}
  },
  "required": ["summary", "start_datetime", "end_datetime"]
}

def parse_text_with_gemini(text_input, timezone='Europe/Paris'):
    # ... (autres imports et schéma)

    # VÉRIFIEZ BIEN LES TRIPLES GUILLEMETS
    system_instruction = (
        """Vous êtes un assistant de planification de calendrier très rigoureux. 
        Analysez la requête utilisateur pour en extraire un seul événement. 
        
        Règles d'extraction des dates/heures :
        1. Les dates/heures de DÉBUT et de FIN (start_datetime et end_datetime) sont OBLIGATOIRES.
        2. Le format doit être strictement ISO 8601 (YYYY-MM-DDTHH:MM:SS).
        3. Si la plage horaire traverse minuit (ex: 22h à 3h), vous devez calculer la date de fin au jour suivant.
        4. Si la durée n'est pas précisée, utilisez une durée d'une heure (60 minutes).
        
        Tenez compte de la date/heure actuelle. Le fuseau horaire actuel est : """ 
        + timezone
    )
    
    
   
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=text_input,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=CALENDAR_EVENT_SCHEMA,
            )
        )
        
        # Gemini renvoie directement une chaîne JSON structurée
        json_string = response.text
        return json.loads(json_string)

    except Exception as e:
        print(f"Erreur lors de l'appel à Gemini (dans gemini_call1.py) : {e}")
        return None