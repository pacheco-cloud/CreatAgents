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
PERSONAL_EVENTS = [
    Event(id=1, title="Aniversário da cidade", date="2025-01-20", color="#22c55e", type="holiday"),
    Event(id=2, title="Reunião família", date="2025-01-19", color="#22c55e", type="personal"),
    Event(id=3, title="Dentista", date="2025-01-21", color="#22c55e", type="appointment"),
    Event(id=4, title="Academia", date="2025-01-20", color="#22c55e", type="exercise")
]

PROFESSIONAL_EVENTS = [
    Event(id=1, title="Reunião equipe", date="2025-01-20", color="#3b82f6", type="meeting"),
    Event(id=2, title="Apresentação projeto", date="2025-01-21", color="#3b82f6", type="presentation"),
    Event(id=3, title="Call cliente", date="2025-01-19", color="#3b82f6", type="call")
]

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "calendar-service"}

@app.get("/personal")
async def get_personal_calendar() -> List[Event]:
    """Retorna eventos do calendário pessoal"""
    return PERSONAL_EVENTS

@app.get("/professional") 
async def get_professional_calendar() -> List[Event]:
    """Retorna eventos do calendário profissional"""
    return PROFESSIONAL_EVENTS

@app.post("/personal")
async def create_personal_event(event: Event) -> Event:
    """Cria um novo evento pessoal"""
    event.id = max([e.id for e in PERSONAL_EVENTS], default=0) + 1
    event.color = "#22c55e"
    PERSONAL_EVENTS.append(event)
    return event

@app.post("/professional")
async def create_professional_event(event: Event) -> Event:
    """Cria um novo evento profissional"""
    event.id = max([e.id for e in PROFESSIONAL_EVENTS], default=0) + 1
    event.color = "#3b82f6"
    PROFESSIONAL_EVENTS.append(event)
    return event

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
