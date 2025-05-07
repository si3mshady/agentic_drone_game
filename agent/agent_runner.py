import os
import openai
import json
import requests
import asyncio
from kafka import KafkaConsumer
from agents import Agent, Runner

openai.api_key = os.getenv("OPENAI_API_KEY")

agent = Agent(
    name="Drone Co-Pilot",
    instructions="""You help a drone avoid obstacles. Respond only with: left, right, or stay.
You will be given:
Drone: x=..., y=...
Obstacles: [{x, y, size}...]
Your job is to choose the safest move."""
)

consumer = KafkaConsumer(
    "drone.telemetry",
    bootstrap_servers='kafka:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

async def decide_and_post(state):
    prompt = f"Drone: x={state['droneX']}, y={state['droneY']}\nObstacles: {json.dumps(state['obstacles'])}"
    result = await Runner.run(agent, prompt)
    move = result.final_output.strip().lower()
    print("[Agent Decision]", move)
    requests.post("http://backend:8000/move", json={"move": move})

async def main():
    for msg in consumer:
        await decide_and_post(msg.value)

if __name__ == "__main__":
    asyncio.run(main())
