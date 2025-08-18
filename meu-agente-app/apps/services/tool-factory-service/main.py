# apps/services/tool-factory-service/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import os
import json
import subprocess
import uuid
from pathlib import Path
import jinja2

app = FastAPI(title="Tool Factory Service", version="1.0.0")

class Parameter(BaseModel):
    name: str
    type: str  # texto, numero, data, booleano

class Tool(BaseModel):
    name: str
    description: str
    apiEndpoint: str
    parameters: List[Parameter]

class ServiceRequest(BaseModel):
    agent_name: str
    agent_type: str
    tools: List[Tool]

# Template para gerar FastAPI service
SERVICE_TEMPLATE = """
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Union
from datetime import date, datetime
import json

app = FastAPI(title="{{ service_name }}", version="1.0.0")

# Modelos gerados automaticamente
{% for tool in tools %}
class {{ tool.name | title }}Request(BaseModel):
    {% for param in tool.parameters %}
    {{ param.name }}: {% if param.type == 'texto' %}str{% elif param.type == 'numero' %}float{% elif param.type == 'data' %}date{% elif param.type == 'booleano' %}bool{% endif %}
    {% endfor %}

class {{ tool.name | title }}Response(BaseModel):
    success: bool
    data: List[Dict]
    message: str

{% endfor %}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "{{ service_name }}"}

{% for tool in tools %}
@app.post("{{ tool.apiEndpoint }}")
async def {{ tool.name }}(
    {% for param in tool.parameters %}
    {{ param.name }}: {% if param.type == 'texto' %}str{% elif param.type == 'numero' %}float{% elif param.type == 'data' %}str{% elif param.type == 'booleano' %}bool{% endif %}{% if not loop.last %},{% endif %}
    {% endfor %}
) -> {{ tool.name | title }}Response:
    \"\"\"{{ tool.description }}\"\"\"
    
    # Dados mock - implementação real seria aqui
    mock_data = generate_mock_data_for_{{ tool.name }}(
        {% for param in tool.parameters %}
        {{ param.name }}={{ param.name }}{% if not loop.last %},{% endif %}
        {% endfor %}
    )
    
    return {{ tool.name | title }}Response(
        success=True,
        data=mock_data,
        message=f"{{ tool.description }} executada com sucesso"
    )

def generate_mock_data_for_{{ tool.name }}({% for param in tool.parameters %}{{ param.name }}{% if not loop.last %}, {% endif %}{% endfor %}):
    \"\"\"Gera dados mock para {{ tool.name }}\"\"\"
    {% if 'hotel' in tool.name.lower() %}
    return [
        {
            "id": "hotel_1",
            "nome": f"Hotel Premium em {locals().get('destino', 'Destino')}", 
            "preco": 250.0,
            "estrelas": 4,
            "disponivel": True
        },
        {
            "id": "hotel_2", 
            "nome": f"Hotel Econômico em {locals().get('destino', 'Destino')}",
            "preco": 120.0,
            "estrelas": 3,
            "disponivel": True
        }
    ]
    {% elif 'voo' in tool.name.lower() or 'flight' in tool.name.lower() %}
    return [
        {
            "id": "voo_1",
            "companhia": "Companhia A",
            "origem": locals().get('origem', 'Origem'),
            "destino": locals().get('destino', 'Destino'),
            "preco": 450.0,
            "duracao": "2h 30m"
        }
    ]
    {% elif 'restaurante' in tool.name.lower() %}
    return [
        {
            "id": "rest_1",
            "nome": "Restaurante Gourmet",
            "tipo_cozinha": "Internacional",
            "preco_medio": 80.0,
            "avaliacao": 4.5
        }
    ]
    {% else %}
    return [
        {
            "id": "item_1",
            "nome": "Resultado da busca",
            "descricao": "Dados encontrados",
            "relevancia": 0.95
        }
    ]
    {% endif %}

{% endfor %}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port={{ port }})
"""

DOCKERFILE_TEMPLATE = """
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

RUN apt-get update && apt-get install -y --no-install-recommends \\
    curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE {{ port }}

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:{{ port }}/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "{{ port }}"]
"""

REQUIREMENTS_TEMPLATE = """
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-dotenv==1.0.0
httpx==0.25.2
"""

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "tool-factory-service"}

@app.post("/create-service")
async def create_service(request: ServiceRequest):
    """Gera automaticamente um microserviço baseado nas ferramentas do agente"""
    
    try:
        # Gerar ID único para o serviço
        service_id = str(uuid.uuid4())[:8]
        service_name = f"{request.agent_name.lower().replace(' ', '-')}-service-{service_id}"
        port = 8000 + hash(service_name) % 1000  # Porta dinâmica
        
        # Diretório do novo serviço
        service_dir = Path(f"/tmp/generated-services/{service_name}")
        service_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar Jinja2
        template_env = jinja2.Environment(loader=jinja2.BaseLoader())
        
        # Gerar main.py
        main_template = template_env.from_string(SERVICE_TEMPLATE)
        main_content = main_template.render(
            service_name=service_name,
            tools=request.tools,
            port=port
        )
        
        with open(service_dir / "main.py", "w") as f:
            f.write(main_content)
        
        # Gerar Dockerfile
        dockerfile_template = template_env.from_string(DOCKERFILE_TEMPLATE)
        dockerfile_content = dockerfile_template.render(port=port)
        
        with open(service_dir / "Dockerfile", "w") as f:
            f.write(dockerfile_content)
        
        # Gerar requirements.txt
        with open(service_dir / "requirements.txt", "w") as f:
            f.write(REQUIREMENTS_TEMPLATE)
        
        # Tentar startar o serviço (em desenvolvimento local)
        try:
            # Em produção isso seria um deploy real
            print(f"Serviço {service_name} criado em {service_dir}")
            print(f"Porta: {port}")
            
            # Simular start do serviço
            service_status = "created"
            
        except Exception as e:
            print(f"Erro ao iniciar serviço: {e}")
            service_status = "created_but_not_started"
        
        return {
            "message": f"Serviço '{service_name}' criado com sucesso",
            "service_id": service_id,
            "service_name": service_name,
            "port": port,
            "status": service_status,
            "endpoints": [f"http://localhost:{port}{tool.apiEndpoint}" for tool in request.tools],
            "service_path": str(service_dir),
            "tools_created": len(request.tools)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar serviço: {str(e)}")

@app.get("/services")
async def list_services():
    """Lista todos os serviços gerados"""
    
    services_dir = Path("/tmp/generated-services")
    if not services_dir.exists():
        return {"services": []}
    
    services = []
    for service_path in services_dir.iterdir():
        if service_path.is_dir():
            services.append({
                "name": service_path.name,
                "path": str(service_path),
                "created_at": service_path.stat().st_ctime
            })
    
    return {"services": services}

@app.delete("/services/{service_name}")
async def delete_service(service_name: str):
    """Remove um serviço gerado"""
    
    service_path = Path(f"/tmp/generated-services/{service_name}")
    
    if not service_path.exists():
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    
    try:
        # Em produção, pararia o container/processo aqui
        import shutil
        shutil.rmtree(service_path)
        
        return {"message": f"Serviço {service_name} removido com sucesso"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover serviço: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)