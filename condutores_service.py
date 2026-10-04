import json

import paho.mqtt.client as mqtt

from database import conectar


TOPICO_CADASTRAR = "detran/condutores/cadastrar"


def ao_conectar(
    client,
    userdata,
    flags,
    reason_code,
    properties
):
    print("Serviço de condutores conectado ao MQTT")

    client.subscribe(TOPICO_CADASTRAR)


def cadastrar_condutor(dados):
    cpf = dados["cpf"]
    nome = dados["nome"]

    conexao = conectar()

    try:
        conexao.execute(
            """
            INSERT INTO condutores (cpf, nome)
            VALUES (?, ?)
            """,
            (cpf, nome)
        )

        conexao.commit()

        return {
            "sucesso": True,
            "mensagem": "Condutor cadastrado com sucesso"
        }

    except Exception as erro:
        return {
            "sucesso": False,
            "mensagem": str(erro)
        }

    finally:
        conexao.close()


def ao_receber(client, userdata, mensagem):
    dados = json.loads(
        mensagem.payload.decode()
    )

    resposta = cadastrar_condutor(dados)

    topico_resposta = dados["resposta_em"]

    client.publish(
        topico_resposta,
        json.dumps(resposta)
    )


client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2
)

client.on_connect = ao_conectar
client.on_message = ao_receber

client.connect(
    "localhost",
    1883
)

print("Serviço de condutores aguardando requisições...")

client.loop_forever()