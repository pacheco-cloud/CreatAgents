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

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "{{ service_name }}"}

{% for tool in tools %}
@app.post("{{ tool.apiEndpoint }}")
async def {{ tool.name }}_endpoint():
    \"\"\"{{ tool.description }}\"\"\"
    
    # Mock data - implementação real seria aqui
    mock_data = [
        {"id": 1, "resultado": "Mock result for {{ tool.name }}", "timestamp": "2024-01-01T00:00:00Z"}
    ]
    
    return {
        "success": True,
        "data": mock_data,
        "message": "Operação realizada com sucesso"
    }

{% endfor %}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port={{ port }})
"""

DOCKERFILE_TEMPLATE = """
FROM python:3.11-alpine

WORKDIR /app

RUN apk add --no-cache gcc musl-dev

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
        
        # Gerar requirements.txt
        requirements_template = template_env.from_string(REQUIREMENTS_TEMPLATE)
        requirements_content = requirements_template.render()
        
        with open(service_dir / "requirements.txt", "w") as f:
            f.write(requirements_content)
        
        # Gerar Dockerfile
        dockerfile_template = template_env.from_string(DOCKERFILE_TEMPLATE)
        dockerfile_content = dockerfile_template.render(port=port)
        
        with open(service_dir / "Dockerfile", "w") as f:
            f.write(dockerfile_content)
        
        # Em um ambiente real, aqui iniciaríamos o container
        # docker_command = f"docker build -t {service_name} {service_dir} && docker run -d -p {port}:{port} --name {service_name} {service_name}"
        # subprocess.run(docker_command, shell=True, check=True)
        
        return {
            "service_id": service_id,
            "service_name": service_name,
            "port": port,
            "status": "created",
            "endpoints": [tool.apiEndpoint for tool in request.tools],
            "message": f"Serviço {service_name} criado com sucesso"
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
                "created": service_path.stat().st_ctime
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