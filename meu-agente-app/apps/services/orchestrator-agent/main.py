from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import httpx
from typing import Dict, Any, List

load_dotenv()

app = FastAPI(title="Orchestrator Agent", version="1.0.0")

class ChatRequest(BaseModel):
    message: str
    user_id: str = "default_user"

class ChatResponse(BaseModel):
    response: str
    agent_used: str
    show_canvas: bool = False
    canvas_type: str = None

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "orchestrator-agent"}

@app.post("/process")
async def process_message(request: ChatRequest) -> ChatResponse:
    """Processa a mensagem do usuário e orquestra a resposta"""
    
    try:
        # Chamar OpenAI diretamente se tiver a chave
        openai_key = os.getenv('OPENAI_API_KEY')
        ai_response = "Como posso ajudá-lo hoje?"
        
        if openai_key and openai_key != "your_openai_api_key_here":
            try:
                from openai import OpenAI
                client = OpenAI(api_key=openai_key)
                
                system_prompt = """
                Você é um assistente inteligente que ajuda com agendas pessoais e profissionais.
                Responda de forma útil e educada em português brasileiro.
                Para perguntas sobre agenda pessoal, mencione que está consultando.
                Para perguntas sobre agenda profissional, mencione que está verificando.
                """
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": request.message}
                    ],
                    max_tokens=150,
                    temperature=0.7
                )
                
                ai_response = response.choices[0].message.content
                
            except Exception as e:
                print(f"OpenAI Error: {e}")
                # Continua com resposta padrão
        
        # Determinar se deve mostrar canvas e qual tipo
        message_lower = request.message.lower()
        show_canvas = False
        canvas_type = None
        agent_used = "master"
        
        if any(word in message_lower for word in ["agenda pessoal", "pessoal", "família", "dentista", "aniversário"]):
            show_canvas = True
            canvas_type = "personal"
            agent_used = "Calendário Pessoal"
            ai_response = "Consultando sua agenda pessoal... Encontrei seus próximos compromissos!"
            
        elif any(word in message_lower for word in ["agenda profissional", "profissional", "trabalho", "reunião", "cliente", "equipe"]):
            show_canvas = True
            canvas_type = "professional" 
            agent_used = "Calendário Profissional"
            ai_response = "Verificando sua agenda profissional... Aqui estão suas reuniões!"
        
        return ChatResponse(
            response=ai_response,
            agent_used=agent_used,
            show_canvas=show_canvas,
            canvas_type=canvas_type
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)