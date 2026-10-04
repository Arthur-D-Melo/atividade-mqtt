import json
import uuid

import paho.mqtt.client as mqtt


BROKER = "localhost"
PORTA = 1883

id_requisicao = str(uuid.uuid4())

topico_resposta = (
    f"detran/respostas/{id_requisicao}"
)


def ao_conectar(
    client,
    userdata,
    flags,
    reason_code,
    properties
):
    client.subscribe(topico_resposta)

    dados = {
    "placa": "ABC1D23",
    "resposta_em": topico_resposta
    }

    client.publish(
        "detran/veiculos/ipva",
        json.dumps(dados)
    )


def ao_receber(client, userdata, mensagem):
    resposta = json.loads(
        mensagem.payload.decode()
    )

    print(resposta)

    client.disconnect()


client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2
)

client.on_connect = ao_conectar
client.on_message = ao_receber

client.connect(
    BROKER,
    PORTA
)

client.loop_forever()