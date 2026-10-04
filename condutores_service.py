import json
import os

import paho.mqtt.client as mqtt

from database import conectar


MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))

TOPICO_CADASTRAR = "detran/condutores/cadastrar"
TOPICO_TRANSFERIR = "detran/condutores/transferir"


def ao_conectar(
    client,
    userdata,
    flags,
    reason_code,
    properties
):
    print("Serviço de condutores conectado ao MQTT")

    client.subscribe(TOPICO_CADASTRAR)
    client.subscribe(TOPICO_TRANSFERIR)


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


def transferir_proprietario(dados):
    placa = dados["placa"]
    novo_cpf = dados["cpf"]

    conexao = conectar()

    try:
        condutor = conexao.execute(
            """
            SELECT cpf
            FROM condutores
            WHERE cpf = ?
            """,
            (novo_cpf,)
        ).fetchone()

        if condutor is None:
            return {
                "sucesso": False,
                "mensagem": "Novo proprietário não cadastrado"
            }

        veiculo = conexao.execute(
            """
            SELECT placa
            FROM veiculos
            WHERE placa = ?
            """,
            (placa,)
        ).fetchone()

        if veiculo is None:
            return {
                "sucesso": False,
                "mensagem": "Veículo não encontrado"
            }

        conexao.execute(
            """
            UPDATE veiculos
            SET cpf_condutor = ?
            WHERE placa = ?
            """,
            (novo_cpf, placa)
        )

        conexao.commit()

        return {
            "sucesso": True,
            "mensagem": "Proprietário transferido com sucesso"
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

    if mensagem.topic == TOPICO_CADASTRAR:
        resposta = cadastrar_condutor(dados)

    elif mensagem.topic == TOPICO_TRANSFERIR:
        resposta = transferir_proprietario(dados)

    else:
        return

    client.publish(
        dados["resposta_em"],
        json.dumps(resposta)
    )


client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2
)

client.on_connect = ao_conectar
client.on_message = ao_receber

client.connect(
    MQTT_HOST,
    MQTT_PORT
)

print("Serviço de condutores aguardando requisições...")

client.loop_forever()