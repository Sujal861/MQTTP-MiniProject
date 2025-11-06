import paho.mqtt.client as mqtt
import hmac
import hashlib
import time
from pathlib import Path
import ssl

# Load shared key using project-relative path
BASE_DIR = Path(__file__).resolve().parents[1]
with open(BASE_DIR / "shared_key.txt", "r") as f:
    SHARED_KEY = f.read().strip().encode()

# MQTT settings
BROKER = "localhost"
PORT = 8883  # Secure port
TOPIC = "secure/topic"
USERNAME = "sujal"
PASSWORD = "sujal352"
CA_CERT_PATH = str(BASE_DIR / "broker_config" / "ca.crt")

def create_hmac(message):
    return hmac.new(SHARED_KEY, message.encode(), hashlib.sha256).hexdigest()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("📶 Publisher connected to broker securely.")
    else:
        print(f"❌ Publisher failed to connect. Return code: {rc}")

if __name__ == "__main__":
    message = "Temperature is 23°C"
    hmac_hash = create_hmac(message)
    final_message = f"{message}||{hmac_hash}"

    client = mqtt.Client(client_id="pubclient")
    client.username_pw_set(USERNAME, PASSWORD)
    client.tls_set(ca_certs=CA_CERT_PATH, cert_reqs=ssl.CERT_NONE, tls_version=ssl.PROTOCOL_TLSv1_2)
    client.tls_insecure_set(True)
    client.on_connect = on_connect
    client.connect(BROKER, PORT, 60)
    client.loop_start()

    time.sleep(0.2)  # Wait a bit for connection

    result = client.publish(TOPIC, final_message)
    result.wait_for_publish()
    status = result.rc

    if status == 0:
        print(f"✅ Published message with HMAC: {final_message}")
    else:
        print("❌ Failed to send message")

    client.loop_stop()
    client.disconnect()
