import json
from datetime import datetime

import paho.mqtt.client as mqtt

from database import conectar


TOPICO_EMPLACAR = "detran/veiculos/emplacar"
TOPICO_IPVA = "detran/veiculos/ipva"
TOPICO_ANO = "detran/veiculos/ano"


def ao_conectar(
    client,
    userdata,
    flags,
    reason_code,
    properties
):
    print("Serviço de veículos conectado ao MQTT")

    client.subscribe(TOPICO_EMPLACAR)
    client.subscribe(TOPICO_IPVA)
    client.subscribe(TOPICO_ANO)


def emplacar_veiculo(dados):
    placa = dados["placa"]
    modelo = dados["modelo"]
    valor = dados["valor"]
    cpf = dados["cpf"]

    ano = datetime.now().year

    conexao = conectar()

    try:
        condutor = conexao.execute(
            """
            SELECT cpf
            FROM condutores
            WHERE cpf = ?
            """,
            (cpf,)
        ).fetchone()

        if condutor is None:
            return {
                "sucesso": False,
                "mensagem": "Condutor não cadastrado"
            }

        conexao.execute(
            """
            INSERT INTO veiculos (
                placa,
                modelo,
                valor,
                cpf_condutor,
                ano_emplacamento
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                placa,
                modelo,
                valor,
                cpf,
                ano
            )
        )

        conexao.commit()

        return {
            "sucesso": True,
            "mensagem": "Veículo emplacado com sucesso"
        }

    except Exception as erro:
        return {
            "sucesso": False,
            "mensagem": str(erro)
        }

    finally:
        conexao.close()


def calcular_ipva(dados):
    placa = dados["placa"]

    conexao = conectar()

    try:
        veiculo = conexao.execute(
            """
            SELECT valor
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

        valor = veiculo[0]

        return {
            "sucesso": True,
            "placa": placa,
            "ipva": valor * 0.02
        }

    finally:
        conexao.close()


def veiculos_por_ano(dados):
    ano = dados["ano"]

    conexao = conectar()

    try:
        registros = conexao.execute(
            """
            SELECT
                placa,
                modelo,
                valor,
                cpf_condutor,
                ano_emplacamento
            FROM veiculos

            WHERE ano_emplacamento = ?

            ORDER BY placa
            """,
            (ano,)
        ).fetchall()

        veiculos = []

        for registro in registros:
            veiculos.append({
                "placa": registro[0],
                "modelo": registro[1],
                "valor": registro[2],
                "cpf_condutor": registro[3],
                "ano_emplacamento": registro[4]
            })

        return {
            "sucesso": True,
            "veiculos": veiculos
        }

    finally:
        conexao.close()


def ao_receber(client, userdata, mensagem):
    dados = json.loads(
        mensagem.payload.decode()
    )

    if mensagem.topic == TOPICO_EMPLACAR:
        resposta = emplacar_veiculo(dados)

    elif mensagem.topic == TOPICO_IPVA:
        resposta = calcular_ipva(dados)

    elif mensagem.topic == TOPICO_ANO:
        resposta = veiculos_por_ano(dados)

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
    "localhost",
    1883
)

print("Serviço de veículos aguardando requisições...")

client.loop_forever()