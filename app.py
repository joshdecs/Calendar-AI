import os
import shutil
import json
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from googleapiclient.discovery import build
from typing import Optional

from create_event import authenticate_google_calendar, create_calendar_event 
from gemini_call1 import parse_multimodal_content 

app = FastAPI(title="Calendar Auto-Agent API")

# ====================================================================
# CONFIGURATION CORS (ESSENTIELLE POUR LE FRONTEND)
# ====================================================================

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "Calendar Agent is active. Use /schedule_event."}

def get_calendar_service():
    try:
        creds = authenticate_google_calendar()
        service = build("calendar", "v3", credentials=creds)
        return service
    except Exception as e:
        raise HTTPException(status_code=500, detail="Échec de l'authentification Google Calendar.")

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Calendar Agent is running."}

@app.post("/schedule_event")
async def schedule_event(
    instruction: str = Form(..., description="Requête texte ou instruction pour l'IA."),
    file: Optional[UploadFile] = File(None, description="Fichier audio, image, ou document à analyser."),
    service: object = Depends(get_calendar_service)
):
    temp_file_path = None
    
    try:
        if file:
            if not os.path.exists("temp_uploads"):
                os.makedirs("temp_uploads")
            
            temp_file_path = os.path.join("temp_uploads", file.filename)
            with open(temp_file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

        instruction_for_gemini = instruction if instruction.strip() else "Analyse le fichier pour des événements de calendrier et retourne-les."

        all_events_details = parse_multimodal_content(
            text_input=instruction_for_gemini, 
            file_path=temp_file_path
        )

        if not all_events_details or not isinstance(all_events_details, list):
            raise HTTPException(status_code=400, detail="L'IA n'a pas pu extraire d'événement valide. (Gemini a retourné 0 événement ou un format incorrect).")

        results = []
        for event_details in all_events_details:
            event_result = create_calendar_event(service, event_details)
            results.append({"summary": event_details.get('summary'), "link": event_result.get('htmlLink')})

        return JSONResponse(
            content={"status": "success", "count": len(results), "events": results}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne lors de la planification: {e}")
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)