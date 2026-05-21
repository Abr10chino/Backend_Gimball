import os
import json
import asyncio
from paho.mqtt.client import Client as MQTTClient
from app.websocket import manager

MQTT_BROKER = os.getenv("MQTT_BROKER", "broker.hivemq.com")
TOPIC_GIROSCOPIO = os.getenv("TOPIC_GIROSCOPIO", "jboteo_gimbal/datos/giroscopio")
TOPIC_SENSORES = os.getenv("TOPIC_SENSORES", "jboteo_gimbal/datos/sensores")
TOPIC_JOYSTICK = os.getenv("TOPIC_JOYSTICK", "jboteo_gimbal/datos/joystick")

mqttClient = MQTTClient()
fastapi_loop = None

def on_message(client, userdata, msg):
    global fastapi_loop
    try:
        payload = json.loads(msg.payload.decode())
        
        data_to_send = {
            "topic": msg.topic,
            "data": payload
        }
        
        if fastapi_loop is not None:
            asyncio.run_coroutine_threadsafe(manager.broadcast(data_to_send), fastapi_loop)
        else:
            print("[MQTT Warning] El loop de FastAPI aún no está registrado.")
        
    except Exception as e:
        print(f"[MQTT Error] No se pudo procesar el mensaje: {e}")

def startMQTT(loop_principal):
    global fastapi_loop
    fastapi_loop = loop_principal
    
    mqttClient.on_message = on_message
    mqttClient.connect(MQTT_BROKER, 1883, 60)

    mqttClient.subscribe(TOPIC_GIROSCOPIO)
    mqttClient.subscribe(TOPIC_SENSORES)
    mqttClient.subscribe(TOPIC_JOYSTICK)

    mqttClient.loop_start()
    print("[MQTT] Cliente conectado y escuchando tópicos con loop registrado...")

def stopMQTT():
    mqttClient.loop_stop()
    mqttClient.disconnect()
    print("[MQTT] Cliente desconectado.")