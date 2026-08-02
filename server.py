const express = require('express');
const cors = require('cors');
const app = express();

app.use(cors());
app.use(express.json());

// Almacenamiento en memoria para los PINs activos
let activePins = {};

app.get('/', (req, res) => {
    res.send('Servidor de PanicCam activo y funcionando en Render 🚀');
});

// 1. ROBLOX registra un PIN recién generado
app.post('/api/create-pin', (req, res) => {
    const { pin } = req.body;
    if (!pin) {
        return res.status(400).json({ success: false, message: "PIN no proporcionado" });
    }

    activePins[pin] = { linked: false, state: "Tranquilo" };
    console.log(`[PIN Creado en Roblox]: ${pin}`);
    res.json({ success: true, message: "PIN registrado con éxito" });
});

// 2. LA WEB intenta vincular con el PIN ingresado por el usuario
app.post('/api/link-pin', (req, res) => {
    const { pin } = req.body;
    
    if (activePins[pin]) {
        activePins[pin].linked = true;
        console.log(`[PIN Vinculado desde Web]: ${pin}`);
        return res.json({ success: true, message: "Cámara vinculada correctamente" });
    } else {
        console.log(`[Rechazado - PIN no encontrado]: ${pin}`);
        return res.status(400).json({ success: false, message: "PIN incorrecto o inexistente" });
    }
});

// 3. LA WEB actualiza el estado emocional (Tranquilo, Concentrado, ¡PÁNICO!)
app.post('/api/update-state', (req, res) => {
    const { pin, state } = req.body;
    if (activePins[pin]) {
        activePins[pin].state = state;
        return res.json({ success: true });
    }
    res.status(400).json({ success: false });
});

// 4. ROBLOX consulta en bucle si su PIN ya fue vinculado y lee el estado
app.get('/api/check-status/:pin', (req, res) => {
    const pin = req.params.pin;
    if (activePins[pin]) {
        res.json({ 
            exists: true, 
            linked: activePins[pin].linked, 
            state: activePins[pin].state 
        });
    } else {
        res.json({ 
            exists: false, 
            linked: false, 
            state: "Ninguno" 
        });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Servidor escuchando en puerto ${PORT}`));
