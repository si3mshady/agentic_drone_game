from fastapi import FastAPI, Request
from kafka import KafkaProducer
import json

app = FastAPI()

producer = KafkaProducer(
    bootstrap_servers='kafka:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

latest_move = "stay"

@app.post("/game-state")
async def game_state(request: Request):
    data = await request.json()
    producer.send("drone.telemetry", value=data)
    return {"status": "sent"}

@app.post("/move")
async def set_move(request: Request):
    global latest_move
    latest_move = (await request.json()).get("move", "stay")
    return {"status": "updated"}

@app.get("/move")
async def get_move():
    return {"move": latest_move}
