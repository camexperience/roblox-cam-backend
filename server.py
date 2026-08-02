from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

app = FastAPI(title="PanicCam Backend")

# Permitir conexiones de la Web y Roblox
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Almacenamiento temporal en memoria
active_pins = {}

class PinModel(BaseModel):
    pin: str

class StateModel(BaseModel):
    pin: str
    state: str

@app.get("/")
def home():
    return {"status": "ok", "message": "Backend PanicCam con FastAPI activo 🚀"}

# 1. ROBLOX registra un PIN recién generado
@app.post("/api/create-pin")
def create_pin(data: PinModel):
    pin = str(data.pin)
    active_pins[pin] = {"linked": False, "state": "Tranquilo"}
    print(f"[PIN Creado]: {pin}")
    return {"success": True, "message": "PIN registrado correctamente"}

# 2. WEB vincula la cámara ingresando el PIN
@app.post("/api/link-pin")
def link_pin(data: PinModel):
    pin = str(data.pin)
    if pin in active_pins:
        active_pins[pin]["linked"] = True
        print(f"[PIN Vinculado]: {pin}")
        return {"success": True, "message": "Cámara vinculada"}
    else:
        raise HTTPException(status_code=400, detail="PIN no encontrado")

# 3. WEB actualiza el estado emocional
@app.post("/api/update-state")
def update_state(data: StateModel):
    pin = str(data.pin)
    if pin in active_pins:
        active_pins[pin]["state"] = data.state
        return {"success": True}
    raise HTTPException(status_code=400, detail="PIN no encontrado")

# 4. ROBLOX consulta el estado actual de la cámara
@app.get("/api/check-status/{pin}")
def check_status(pin: str):
    pin_str = str(pin)
    if pin_str in active_pins:
        return {
            "exists": True,
            "linked": active_pins[pin_str]["linked"],
            "state": active_pins[pin_str]["state"]
        }
    return {
        "exists": False,
        "linked": False,
        "state": "Ninguno"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
