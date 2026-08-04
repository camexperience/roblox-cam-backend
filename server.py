import random
from typing import Dict, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Panic Cam - Dynamic Stress Server")

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sesiones en memoria: { "1234": {"stress": 0, "connected": False, "user_id": 123456} }
sessions: Dict[str, dict] = {}


# --- MODELOS DE DATOS ---
class CreatePinRequest(BaseModel):
    userId: Optional[int] = None

class LinkPinRequest(BaseModel):
    pin: str

class UpdateStateRequest(BaseModel):
    pin: str
    stress: int


# --- RUTAS DE LA API ---

@app.get("/")
def home():
    return {"status": "ok", "message": "Servidor activo 🚀", "active_sessions": len(sessions)}


@app.post("/api/create-pin")
def create_pin(data: CreatePinRequest):
    """ Genera un PIN único de 4 dígitos para Roblox """
    while True:
        pin = str(random.randint(1000, 9999))
        if pin not in sessions:
            break

    sessions[pin] = {
        "stress": 0,
        "connected": False,
        "user_id": data.userId
    }
    
    print(f"🔑 [ROBLOX] PIN Creado: '{pin}' | UserId: {data.userId}")
    return {"success": True, "pin": pin}


@app.post("/api/link-pin")
def link_pin(data: LinkPinRequest):
    """ Vincula el PIN ingresado desde la Web """
    # Limpiamos el PIN recibido para evitar errores de espacios o tipos
    pin_ingresado = str(data.pin).strip()
    
    print(f"📩 [WEB] Intentando vincular PIN: '{pin_ingresado}' | PINs Activos: {list(sessions.keys())}")
    
    if pin_ingresado in sessions:
        sessions[pin_ingresado]["connected"] = True
        print(f"🟢 [WEB] PIN '{pin_ingresado}' vinculado con éxito!")
        return {"success": True, "message": "PIN vinculado correctamente"}
    else:
        print(f"❌ [WEB] Fallo: El PIN '{pin_ingresado}' no existe.")
        raise HTTPException(status_code=404, detail="PIN no encontrado o expirado")


@app.post("/api/update-state")
def update_state(data: UpdateStateRequest):
    """ Recibe el nivel de estrés desde la Web (0 - 100) """
    pin = str(data.pin).strip()
    if pin in sessions:
        stress_level = max(0, min(100, int(data.stress)))
        sessions[pin]["stress"] = stress_level
        return {"success": True, "stress": stress_level}
    else:
        raise HTTPException(status_code=404, detail="PIN no encontrado")


@app.get("/api/get-state/{pin}")
def get_state(pin: str):
    """ Roblox consulta constantemente el estado """
    clean_pin = str(pin).strip()
    if clean_pin in sessions:
        return {
            "success": True, 
            "stress": sessions[clean_pin]["stress"],
            "connected": sessions[clean_pin]["connected"]
        }
    else:
        return {"success": False, "stress": 0, "connected": False}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
