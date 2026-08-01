from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random
import uvicorn

app = FastAPI()

# Permitir que la página web se comunique con este servidor
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Memoria temporal para almacenar los PINs activos
# Estructura: { "8731": {"user_id": 123456, "is_scared": False} }
active_pins = {}

# 1. ROBLOX PIDE UN PIN
@app.get("/generate_pin/{user_id}")
def generate_pin(user_id: int):
    # Generar PIN único de 4 dígitos
    pin = str(random.randint(1000, 9999))
    while pin in active_pins:
        pin = str(random.randint(1000, 9999))
    
    active_pins[pin] = {
        "user_id": user_id,
        "is_scared": False
    }
    return {"pin": pin}

# 2. LA WEB ENVÍA EL ESTADO DE LA CÁMARA
@app.post("/update_status")
def update_status(data: dict):
    pin = data.get("pin")
    is_scared = data.get("is_scared", False)

    if pin in active_pins:
        active_pins[pin]["is_scared"] = is_scared
        return {"status": "success"}
    return {"status": "invalid_pin"}

# 3. ROBLOX CONSULTA EL ESTADO DE SU JUGADOR
@app.get("/get_status/{user_id}")
def get_status(user_id: int):
    for pin, info in active_pins.items():
        if info["user_id"] == user_id:
            return {"is_scared": info["is_scared"]}
    return {"is_scared": False}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)