import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv
import time

load_dotenv()
client = genai.Client()

# 1. DÉFINITION DU SCHÉMA JSON POUR L'EXTRACTION DE PLUSIEURS ÉVÉNEMENTS

SINGLE_EVENT_SCHEMA = {
  "type": "object",
  "properties": {
    "summary": {"type": "string", "description": "Titre ou résumé de l'événement en français, nettoyé des détails de date/heure."},
    "start_datetime": {"type": "string", "description": "Heure de début au format YYYY-MM-DDTHH:MM:SS (ISO 8601)."},
    "end_datetime": {"type": "string", "description": "Heure de fin au format YYYY-MM-DDTHH:MM:SS (ISO 8601)."}
  },
  "required": ["summary", "start_datetime", "end_datetime"]
}

CALENDAR_EVENTS_SCHEMA = {
    "type": "array",
    "items": SINGLE_EVENT_SCHEMA
}


def parse_multimodal_content(text_input, file_path=None, timezone='America/Toronto'):
    """
    Appelle l'API Gemini pour analyser le contenu (texte + fichier) et le convertir 
    en un tableau JSON d'événements.
    """
    
    contents = []
    
    if file_path:
        print(f"Chargement du fichier : {file_path}")
        uploaded_file = client.files.upload(file=file_path)
        contents.append(uploaded_file)
        
        print("Attente de l'activation du fichier (2 secondes)...")
        time.sleep(2) 

        contents.append(text_input)

    system_instruction = (
        """Vous êtes un assistant de planification de calendrier très rigoureux. 
        Analysez TOUT le contenu fourni (texte et/ou document) pour en extraire un ou plusieurs événements. 
        
        Règles d'extraction des événements (à retourner dans un tableau JSON) :
        1. Les dates/heures de DÉBUT et de FIN (start_datetime et end_datetime) sont OBLIGATOIRES pour CHAQUE événement.
        2. Le format doit être strictement ISO 8601 (YYYY-MM-DDTHH:MM:SS).
        3. Si la plage horaire traverse minuit (ex: 22h à 3h), vous devez calculer la date de fin au jour suivant.
        4. Si la durée n'est pas précisée, utilisez une durée d'une heure (60 minutes).
        5. Tenez compte de la date/heure actuelle. Le fuseau horaire actuel est : """ 
        + timezone
    )

    try:
        response = client.models.generate_content(
            model='gemini-2.5-pro', 
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=CALENDAR_EVENTS_SCHEMA, 
            )
        )
        
        
        if file_path:
            client.files.delete(name=uploaded_file.name)
            
        json_string = response.text
        return json.loads(json_string)

    except Exception as e:
        print(f"Erreur lors de l'appel à Gemini (dans gemini_call1.py) : {e}")
        if file_path and 'uploaded_file' in locals():
             client.files.delete(name=uploaded_file.name)
        return None

if __name__ == '__main__':
    test_phrase = "Je dois planifier un appel client demain à 11h (45min) et prendre mon café avec Léo après, à 13h."
    print(f"Analyse de : {test_phrase}")
    
    resultats = parse_multimodal_content(test_phrase)
    
    if resultats:
        print("\nRésultat JSON structuré :")
        print(json.dumps(resultats, indent=2)) 
        print(f"Nombre d'événements trouvés : {len(resultats)}")