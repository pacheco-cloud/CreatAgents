from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, date
from typing import List, Optional
import json

app = FastAPI(title="Calendar Service", version="1.0.0")

class Event(BaseModel):
    id: str
    title: str
    date: str
    color: str
    type: str = "event"

# Mock data - em produção isso viria de um banco de dados
ALL_EVENTS = [
    Event(id="1", title="Aniversário da cidade", date="2025-01-20", color="#22c55e", type="holiday"),
    Event(id="2", title="Reunião família", date="2025-01-19", color="#22c55e", type="personal"),
    Event(id="3", title="Dentista", date="2025-01-21", color="#22c55e", type="appointment"),
    Event(id="4", title="Academia", date="2025-01-20", color="#22c55e", type="exercise"),
    Event(id="5", title="Reunião equipe", date="2025-01-20", color="#3b82f6", type="meeting"),
    Event(id="6", title="Apresentação projeto", date="2025-01-21", color="#3b82f6", type="presentation"),
    Event(id="7", title="Call cliente", date="2025-01-19", color="#3b82f6", type="call")
]

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "calendar-service"}

@app.get("/all")
async def get_all_calendar() -> List[Event]:
    """Retorna todos os eventos da agenda"""
    return ALL_EVENTS

@app.get("/personal")
async def get_personal_calendar() -> List[Event]:
    """Retorna eventos do calendário pessoal (mantido para compatibilidade)"""
    return [e for e in ALL_EVENTS if e.type in ["holiday", "personal", "appointment", "exercise"]]

@app.get("/professional") 
async def get_professional_calendar() -> List[Event]:
    """Retorna eventos do calendário profissional (mantido para compatibilidade)"""
    return [e for e in ALL_EVENTS if e.type in ["meeting", "presentation", "call"]]

@app.post("/create")
async def create_event(event: Event) -> Event:
    """Cria um novo evento na agenda"""
    event.id = max([e.id for e in ALL_EVENTS], default=0) + 1
    # Define cor baseada no tipo
    if event.type in ["meeting", "presentation", "call"]:
        event.color = "#3b82f6"  # Azul para eventos profissionais
    else:
        event.color = "#22c55e"  # Verde para eventos pessoais
    ALL_EVENTS.append(event)
    return event

@app.post("/personal")
async def create_personal_event(event: Event) -> Event:
    """Cria um novo evento pessoal (mantido para compatibilidade)"""
    event.id = max([e.id for e in ALL_EVENTS], default=0) + 1
    event.color = "#22c55e"
    ALL_EVENTS.append(event)
    return event

@app.post("/professional")
async def create_professional_event(event: Event) -> Event:
    """Cria um novo evento profissional (mantido para compatibilidade)"""
    event.id = max([e.id for e in ALL_EVENTS], default=0) + 1
    event.color = "#3b82f6"
    ALL_EVENTS.append(event)
    return event

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
