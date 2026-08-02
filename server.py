from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pins = {}        # {pin: user_id}
user_states = {} # {user_id: is_scared}

class StatusData(BaseModel):
    pin: str
    is_scared: bool

@app.get("/")
def home():
    return {"status": "OK"}

@app.get("/generate_pin/{user_id}")
def generate_pin(user_id: int):
    # Borrar PINs viejos del mismo usuario si vuelve a unirse o pedir PIN
    for old_pin, uid in list(pins.items()):
        if uid == user_id:
            del pins[old_pin]

    pin = str(random.randint(1000, 9999))
    pins[pin] = user_id
    user_states[user_id] = False
    return {"pin": pin}

# Acepta tanto /validate_pin como /verify_pin por si acaso
@app.get("/validate_pin/{pin}")
@app.get("/verify_pin/{pin}")
def validate_pin(pin: str):
    pin_str = str(pin).strip()
    if pin_str in pins:
        return {"valid": True, "user_id": pins[pin_str]}
    return {"valid": False}

@app.post("/update_status")
def update_status(data: StatusData):
    pin_str = str(data.pin).strip()
    if pin_str in pins:
        user_id = pins[pin_str]
        user_states[user_id] = data.is_scared
        return {"success": True}
    return {"success": False, "error": "PIN no encontrado"}

@app.get("/get_status/{user_id}")
def get_status(user_id: int):
    is_scared = user_states.get(user_id, False)
    return {"is_scared": is_scared}
