import paho.mqtt.client as mqtt


def ao_conectar(client, userdata, flags, reason_code, properties):
    print("Serviço de condutores conectado ao MQTT")

    client.subscribe("detran/teste")


def ao_receber(client, userdata, mensagem):
    texto = mensagem.payload.decode()

    print(f"Mensagem recebida: {texto}")


client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2
)

client.on_connect = ao_conectar
client.on_message = ao_receber

client.connect(
    "localhost",
    1883
)

print("Aguardando mensagens...")

client.loop_forever()