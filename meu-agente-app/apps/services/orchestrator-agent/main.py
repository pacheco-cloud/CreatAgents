from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import httpx
from typing import Dict, Any, List, Optional, Union

load_dotenv()

app = FastAPI(title="Orchestrator Agent", version="1.0.0")

class ChatRequest(BaseModel):
    message: str
    user_id: str = "default_user"

class ChatResponse(BaseModel):
    response: str
    agent_used: str
    show_canvas: bool = False

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "orchestrator-agent"}

@app.post("/process")
async def process_message(request: ChatRequest) -> ChatResponse:
    """Processa a mensagem do usuário e orquestra a resposta entre agentes especializados"""
    
    try:
        # Primeiro, analisamos se a pergunta precisa de funcionalidades específicas
        message_lower = request.message.lower()
        
        # Verificar se precisa de funcionalidades de agenda
        agenda_keywords = ["agenda", "calendário", "compromisso", "evento", "reunião", "marcar", "agendar", 
                          "data", "horário", "quando", "hoje", "amanhã", "semana", "mês"]
        
        needs_calendar = any(keyword in message_lower for keyword in agenda_keywords)
        
        if needs_calendar:
            # Redirecionar para funcionalidades de agenda
            return await handle_calendar_request(request)
        else:
            # Usar o agente de conhecimento geral
            return await handle_general_request(request)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

async def handle_calendar_request(request: ChatRequest) -> ChatResponse:
    """Processa requisições relacionadas à agenda"""
    try:
        # Consultar eventos através do calendar service
        async with httpx.AsyncClient() as client:
            calendar_response = await client.get("http://calendar-service:8002/all")
            events = calendar_response.json() if calendar_response.status_code == 200 else []
        
        # Usar IA para gerar resposta contextual sobre a agenda
        openai_key = os.getenv('OPENAI_API_KEY')
        ai_response = "Consultando sua agenda..."
        
        if openai_key and openai_key != "your_openai_api_key_here":
            try:
                from openai import OpenAI
                client = OpenAI(api_key=openai_key)
                
                events_context = f"Eventos na agenda: {events}" if events else "Nenhum evento encontrado."
                
                system_prompt = f"""
                Você é um assistente de agenda inteligente. O usuário perguntou: "{request.message}"
                
                Contexto da agenda atual: {events_context}
                
                Responda de forma útil sobre a agenda do usuário. Se não houver eventos relevantes, 
                sugira criar novos eventos se apropriado.
                """
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": request.message}
                    ],
                    max_tokens=200,
                    temperature=0.7
                )
                
                ai_response = response.choices[0].message.content
                
            except Exception as e:
                print(f"OpenAI Error: {e}")
        
        return ChatResponse(
            response=ai_response,
            agent_used="Agenda Service",
            show_canvas=True
        )
        
    except Exception as e:
        print(f"Calendar service error: {e}")
        return ChatResponse(
            response="Desculpe, não foi possível acessar sua agenda no momento.",
            agent_used="Agenda Service",
            show_canvas=False
        )

async def handle_general_request(request: ChatRequest) -> ChatResponse:
    """Processa requisições de conhecimento geral usando o agente principal"""
    try:
        # Buscar configuração do agente de conhecimento geral
        async with httpx.AsyncClient() as client:
            agent_response = await client.get("http://user-settings-service:8004/agents/1")
            agent_config = agent_response.json() if agent_response.status_code == 200 else None
        
        # Usar IA para resposta de conhecimento geral
        openai_key = os.getenv('OPENAI_API_KEY')
        ai_response = "Como posso ajudá-lo hoje?"
        
        if openai_key and openai_key != "your_openai_api_key_here":
            try:
                from openai import OpenAI
                client = OpenAI(api_key=openai_key)
                
                # Usar o prompt do agente de conhecimento geral se disponível
                system_prompt = (agent_config.get('system_prompt') if agent_config 
                               else """Você é um assistente de IA de conhecimento geral, como ChatGPT, Gemini ou Claude. 
                                      Seja útil, preciso e amigável. Responda em português brasileiro.""")
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": request.message}
                    ],
                    max_tokens=300,
                    temperature=0.7
                )
                
                ai_response = response.choices[0].message.content
                
            except Exception as e:
                print(f"OpenAI Error: {e}")
        
        return ChatResponse(
            response=ai_response,
            agent_used="Assistente Geral",
            show_canvas=False
        )
        
    except Exception as e:
        print(f"General agent error: {e}")
        return ChatResponse(
            response="Desculpe, ocorreu um erro ao processar sua solicitação.",
            agent_used="Assistente Geral",
            show_canvas=False
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)