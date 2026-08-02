from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

app = FastAPI(title="PanicCam Backend")

# Habilitar CORS completo para conectar Web, Localhost y Roblox sin bloqueos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Diccionario temporal en memoria para los PINs
active_pins = {}

class PinModel(BaseModel):
    pin: str

class StateModel(BaseModel):
    pin: str
    state: str

@app.get("/")
def home():
    return {"status": "ok", "message": "Backend PanicCam activo"}

# 1. ROBLOX: Registra el PIN del jugador
@app.post("/api/create-pin")
def create_pin(data: PinModel):
    pin = str(data.pin).strip()
    active_pins[pin] = {"linked": False, "state": "Tranquilo"}
    print(f"✅ PIN creado desde Roblox: {pin}")
    return {"success": True, "message": "PIN registrado"}

# 2. WEB: Vincula el PIN puesto por el usuario
@app.post("/api/link-pin")
def link_pin(data: PinModel):
    pin = str(data.pin).strip()
    if pin in active_pins:
        active_pins[pin]["linked"] = True
        print(f"🔗 PIN vinculado en Web: {pin}")
        return {"success": True, "message": "Cámara vinculada"}
    
    print(f"❌ Error vinculación: PIN {pin} no existe. PINs activos: {list(active_pins.keys())}")
    raise HTTPException(status_code=400, detail="El PIN no existe. Entrá primero a Roblox.")

# 3. WEB: Actualiza el estado de la cámara
@app.post("/api/update-state")
def update_state(data: StateModel):
    pin = str(data.pin).strip()
    if pin in active_pins:
        active_pins[pin]["state"] = data.state
        return {"success": True}
    raise HTTPException(status_code=400, detail="PIN no encontrado")

# 4. ROBLOX: Lee el estado de la cámara
@app.get("/api/check-status/{pin}")
def check_status(pin: str):
    pin_str = str(pin).strip()
    if pin_str in active_pins:
        return {
            "exists": True,
            "linked": active_pins[pin_str]["linked"],
            "state": active_pins[pin_str]["state"]
        }
    return {
        "exists": False,
        "linked": False,
        "state": "Desconectado"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
