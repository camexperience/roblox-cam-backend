import random
from typing import Dict, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions: Dict[str, dict] = {}

class CreatePinRequest(BaseModel):
    userId: Optional[int] = None

class LinkPinRequest(BaseModel):
    pin: str

class UpdateStateRequest(BaseModel):
    pin: str
    stress: int

@app.get("/")
def home():
    return {"status": "ok"}

@app.post("/api/create-pin")
def create_pin(data: CreatePinRequest):
    while True:
        pin = str(random.randint(1000, 9999))
        if pin not in sessions:
            break

    sessions[pin] = {"stress": 0, "connected": False, "user_id": data.userId}
    print(f"PIN Creado: {pin}")
    return {"success": True, "pin": pin}

@app.post("/api/link-pin")
def link_pin(data: LinkPinRequest):
    pin = data.pin.strip()
    if pin in sessions:
        sessions[pin]["connected"] = True
        print(f"PIN Conectado: {pin}")
        return {"success": True}
    else:
        raise HTTPException(status_code=404, detail="PIN no encontrado")

@app.post("/api/update-state")
def update_state(data: UpdateStateRequest):
    pin = data.pin.strip()
    if pin in sessions:
        sessions[pin]["stress"] = max(0, min(100, data.stress))
        return {"success": True}
    else:
        raise HTTPException(status_code=404, detail="PIN no encontrado")

@app.get("/api/get-state/{pin}")
def get_state(pin: str):
    if pin in sessions:
        return {
            "success": True, 
            "stress": sessions[pin]["stress"],
            "connected": sessions[pin]["connected"]
        }
    return {"success": False, "stress": 0, "connected": False}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
