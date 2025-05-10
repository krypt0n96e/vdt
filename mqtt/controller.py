import json
import paho.mqtt.client as mqtt

broker = "localhost"
port = 1883

# Topic
sensor_topic = "iot/sensor/temp"
fan_topic = "iot/control/fan"

status=0

def on_connect(client, userdata, flags, rc):
    print("Connected with result code", rc)
    client.subscribe(sensor_topic)

def on_message(client, userdata, msg):
    global status
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)
        temperature = data['temp']
        print(f"[DATA] Temp = {temperature} °C")

        if temperature > 75 and status == 0:
            status = 1
            fan_msg = json.dumps({"status": "ON"})
            client.publish(fan_topic, fan_msg,qos=1,retain=1)
            print(f"[Fan] Published to {fan_topic}: {fan_msg}")
        elif temperature < 65 and status == 1:
            status = 0
            fan_msg = json.dumps({"status": "OFF"})
            client.publish(fan_topic, fan_msg,qos=1,retain=1)
            print(f"[Fan] Published to {fan_topic}: {fan_msg}")

    except json.JSONDecodeError:
        print("[ERROR] Invalid JSON:", msg.payload)
    except KeyError:
        print("[ERROR] Missing 'temp' in payload:", payload)

client = mqtt.Client(client_id="controller")
client.will_set(
    f"iot/{client._client_id.decode() if isinstance(client._client_id, bytes) else client._client_id}/status",
    payload=json.dumps({"status": "offline"}),
    qos=1,
    retain=True
)
client.on_connect = on_connect
client.on_message = on_message


client.connect(broker, port)
client.loop_start()
client.publish(
    f"iot/{client._client_id.decode() if isinstance(client._client_id, bytes) else client._client_id}/status",
    payload=json.dumps({"status": "online"}),
    qos=1,
    retain=True
)
# Keep the script running
try:
    while True:
        pass
except KeyboardInterrupt:
    client.disconnect()
    print("\nDisconnected")