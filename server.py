import random
from typing import Dict, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Panic Cam - Dynamic Stress Server")

# Configuración de CORS para permitir peticiones desde cualquier origen (Web/Browser)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Estructura en memoria para almacenar sesiones por PIN
# Formato: { "8731": {"stress": 0, "connected": False, "user_id": 1234567} }
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
    return {"status": "ok", "message": "Servidor de Estrés Python para Roblox está activo 🚀"}


@app.post("/api/create-pin")
def create_pin(data: CreatePinRequest):
    """
    Roblox llama a este endpoint al entrar un jugador para generar un PIN único de 4 dígitos.
    """
    # Generar un PIN de 4 dígitos único
    while True:
        pin = str(random.randint(1000, 9999))
        if pin not in sessions:
            break

    sessions[pin] = {
        "stress": 0,
        "connected": False,
        "user_id": data.userId
    }
    
    print(f"🔑 PIN Creado: {pin} para UserId: {data.userId}")
    return {"success": True, "pin": pin}


@app.post("/api/link-pin")
def link_pin(data: LinkPinRequest):
    """
    La web llama a este endpoint cuando el usuario ingresa su PIN en la página.
    """
    pin = data.pin.strip()
    if pin in sessions:
        sessions[pin]["connected"] = True
        print(f"🟢 PIN Vinculado con éxito en la Web: {pin}")
        return {"success": True, "message": "PIN vinculado con éxito"}
    else:
        raise HTTPException(status_code=404, detail="PIN no encontrado o expirado")


@app.post("/api/update-state")
def update_state(data: UpdateStateRequest):
    """
    La web envía constantemente el nivel de estrés calculado (0 a 100).
    """
    pin = data.pin.strip()
    if pin in sessions:
        # Asegurar que el nivel de estrés esté acotado entre 0 y 100
        stress_level = max(0, min(100, data.stress))
        sessions[pin]["stress"] = stress_level
        return {"success": True, "stress": stress_level}
    else:
        raise HTTPException(status_code=404, detail="PIN no encontrado")


@app.get("/api/get-state/{pin}")
def get_state(pin: str):
    """
    Roblox consulta continuamente el estado del jugador mediante su PIN.
    """
    clean_pin = pin.strip()
    if clean_pin in sessions:
        return {
            "success": True, 
            "stress": sessions[clean_pin]["stress"],
            "connected": sessions[clean_pin]["connected"]
        }
    else:
        return {"success": False, "stress": 0, "connected": False}


# Si ejecutás el archivo directamente con python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
