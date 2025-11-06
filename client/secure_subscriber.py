# Import required libraries
import paho.mqtt.client as mqtt
import hmac
import hashlib
import datetime
from pathlib import Path
import ssl

# Load the shared secret key using project-relative path
BASE_DIR = Path(__file__).resolve().parents[1]
with open(BASE_DIR / "shared_key.txt", "r") as f:
    SHARED_KEY = f.read().strip().encode()

# MQTT settings
BROKER = "localhost"
PORT = 8883  # TLS port
TOPIC = "secure/topic"
USERNAME = "sujal"
PASSWORD = "sujal352"

# Paths to TLS certificates
CA_CERT_PATH = str(BASE_DIR / "broker_config" / "ca.crt")

# HMAC verification
def verify_hmac(message, received_hmac):
    calculated_hmac = hmac.new(SHARED_KEY, message.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(calculated_hmac, received_hmac), calculated_hmac

# MQTT Callbacks
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("📶 Connected to broker securely!")
        client.subscribe(TOPIC)
        print(f"✅ Subscribed to topic: {TOPIC}")
    else:
        print(f"❌ Connection failed with code {rc}")

def on_message(client, userdata, msg):
    try:
        print("\n" + "="*60)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"🕒 Time: {timestamp}")
        payload = msg.payload.decode()
        print(f"📨 Raw message received: {payload}")

        if "||" in payload:
            message, received_hmac = payload.split("||", 1)
            print(f"🧾 Parsed message: {message}")
            print(f"🔐 HMAC from message: {received_hmac}")
            valid, expected_hmac = verify_hmac(message, received_hmac)

            if valid:
                print("✅ Message is authentic!")
            else:
                print("❌ HMAC verification failed!")
                print(f"🧮 Expected HMAC: {expected_hmac}")
        else:
            print(f"⚠️ Malformed message (missing '||'):\n   {payload}")

    except Exception as e:
        print(f"❗ Error processing message: {e}")

# Main function
if __name__ == "__main__":
    print("📡 Waiting for messages...")

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="subclient")

    # Authentication
    client.username_pw_set(USERNAME, PASSWORD)

    # TLS configuration
    client.tls_set(ca_certs=CA_CERT_PATH, cert_reqs=ssl.CERT_NONE, tls_version=ssl.PROTOCOL_TLSv1_2)
    client.tls_insecure_set(True)

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, PORT, 60)
    client.loop_forever()
