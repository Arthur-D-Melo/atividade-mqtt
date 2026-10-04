import json
import uuid

import paho.mqtt.client as mqtt


BROKER = "localhost"
PORTA = 1883

id_requisicao = str(uuid.uuid4())

topico_resposta = (
    f"detran/respostas/{id_requisicao}"
)


TOPICO_PEDIDO = "detran/multas/lancar"

DADOS = {
    "ano": 2026,
    "descricao": "Excesso de velocidade",
    "pontuacao": 5,
    "placa": "ABC1D23",
    "resposta_em": topico_resposta
}


def ao_conectar(
    client,
    userdata,
    flags,
    reason_code,
    properties
):
    print("Cliente conectado ao MQTT")

    client.subscribe(
        topico_resposta
    )


def ao_inscrever(
    client,
    userdata,
    mid,
    reason_codes,
    properties
):
    print("Inscrição no tópico de resposta confirmada")

    client.publish(
        TOPICO_PEDIDO,
        json.dumps(DADOS)
    )


def ao_receber(
    client,
    userdata,
    mensagem
):
    resposta = json.loads(
        mensagem.payload.decode()
    )

    print(resposta)

    client.disconnect()


client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2
)

client.on_connect = ao_conectar
client.on_subscribe = ao_inscrever
client.on_message = ao_receber

client.connect(
    BROKER,
    PORTA
)

client.loop_forever()