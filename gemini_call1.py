import os
import json
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
client = genai.Client()

SINGLE_EVENT_SCHEMA = {
  "type": "object",
  "properties": {
    "summary": {"type": "string"},
    "start_datetime": {"type": "string"},
    "end_datetime": {"type": "string"}
  },
  "required": ["summary", "start_datetime", "end_datetime"]
}

CALENDAR_EVENTS_SCHEMA = {
    "type": "array",
    "items": SINGLE_EVENT_SCHEMA
}

def parse_multimodal_content(text_input, file_path=None, timezone='America/Toronto'):
    contents = []
    uploaded_file = None
    
    try:
        if file_path:
            uploaded_file = client.files.upload(file=file_path)
            contents.append(uploaded_file)

            timeout = 60
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                file_status = client.files.get(name=uploaded_file.name)
                
                if file_status.state.name == 'ACTIVE':
                    break
                
                if file_status.state.name == 'FAILED':
                    raise Exception(f"Le traitement du fichier a échoué: {file_status.name}")
                
                time.sleep(2) 
            else:
                raise TimeoutError("Le fichier n'est pas devenu actif dans le délai imparti.")

        contents.append(text_input)

        if not contents or (len(contents) == 1 and not text_input.strip()):
            return []

        system_instruction = (
            """Vous êtes un assistant de planification de calendrier très rigoureux. 
            Analysez TOUT le contenu fourni (texte et/ou document) pour en extraire un ou plusieurs événements. 
            
            Règles d'extraction des événements (à retourner dans un tableau JSON) :
            1. Les dates/heures de DÉBUT et de FIN sont OBLIGATOIRES pour CHAQUE événement.
            2. Le format doit être strictement ISO 8601 (YYYY-MM-DDTHH:MM:SS).
            3. Si la plage horaire traverse minuit, vous devez calculer la date de fin au jour suivant.
            4. Si la durée n'est pas précisée, utilisez une durée d'une heure (60 minutes).
            
            Tenez compte de la date/heure actuelle. Le fuseau horaire actuel est : """ 
            + timezone
        )

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=CALENDAR_EVENTS_SCHEMA,
            )
        )
        
        json_string = response.text
        
        if not json_string or json_string.strip() == "":
            return []
            
        return json.loads(json_string)

    except json.JSONDecodeError:
        return []
    
    except Exception as e:
        raise
    
    finally:
        if uploaded_file:
            client.files.delete(name=uploaded_file.name)