import paho.mqtt.client as mqtt


client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2
)

client.connect(
    "localhost",
    1883
)

client.publish(
    "detran/teste",
    "Ola MQTT"
)

print("Mensagem enviada")

client.disconnect()