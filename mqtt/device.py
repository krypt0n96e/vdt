import json
import paho.mqtt.client as mqtt

broker = "localhost"
port = 1883
topic = "iot/control/fan"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code", rc)
    client.subscribe(topic)

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)
        fan_status = data.get("status")

        if fan_status == "ON":
            print("🔴 Fan is turned ON")
            # ở đây có thể bật relay hoặc GPIO thật nếu chạy trên ESP32/RPi
        elif fan_status == "OFF":
            print("🟢 Fan is turned OFF")
        else:
            print("⚠️ Unknown command:", fan_status)

    except json.JSONDecodeError:
        print("[ERROR] Invalid JSON:", msg.payload)

client = mqtt.Client(client_id="fan_device")
client.will_set(
    f"iot/{client._client_id.decode() if isinstance(client._client_id, bytes) else client._client_id}/status",
    payload=json.dumps({"status": "offline"}),
    qos=1,
    retain=True
)

client.on_connect = on_connect
client.on_message = on_message
client.publish(
    f"iot/{client._client_id.decode() if isinstance(client._client_id, bytes) else client._client_id}/status",
    payload=json.dumps({"status": "online"}),
    qos=1,
    retain=True
)

client.connect(broker, port)
client.loop_forever()
