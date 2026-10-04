import json
import os

import paho.mqtt.client as mqtt

from database import conectar


MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))

TOPICO_LANCAR = "detran/multas/lancar"
TOPICO_VEICULO = "detran/multas/veiculo"
TOPICO_CONDUTOR = "detran/multas/condutor"
TOPICO_ANO = "detran/multas/ano"
TOPICO_TOP5 = "detran/multas/top5"


def ao_conectar(
    client,
    userdata,
    flags,
    reason_code,
    properties
):
    print("Serviço de multas conectado ao MQTT")

    client.subscribe(TOPICO_LANCAR)
    client.subscribe(TOPICO_VEICULO)
    client.subscribe(TOPICO_CONDUTOR)
    client.subscribe(TOPICO_ANO)
    client.subscribe(TOPICO_TOP5)


def lancar_multa(dados):
    ano = dados["ano"]
    descricao = dados["descricao"]
    pontuacao = dados["pontuacao"]
    placa = dados["placa"]

    conexao = conectar()

    try:
        veiculo = conexao.execute(
            """
            SELECT cpf_condutor
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

        cpf_condutor = veiculo[0]

        conexao.execute(
            """
            INSERT INTO multas (
                ano,
                descricao,
                pontuacao,
                placa,
                cpf_condutor
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                ano,
                descricao,
                pontuacao,
                placa,
                cpf_condutor
            )
        )

        conexao.commit()

        return {
            "sucesso": True,
            "mensagem": "Multa lançada com sucesso"
        }

    except Exception as erro:
        return {
            "sucesso": False,
            "mensagem": str(erro)
        }

    finally:
        conexao.close()


def multas_veiculo(dados):
    placa = dados["placa"]
    ano = dados["ano"]

    conexao = conectar()

    try:
        registros = conexao.execute(
            """
            SELECT
                m.ano,
                m.descricao,
                m.pontuacao,
                m.placa,
                m.cpf_condutor,
                c.nome
            FROM multas m

            JOIN condutores c
                ON c.cpf = m.cpf_condutor

            WHERE m.placa = ?
              AND m.ano = ?

            ORDER BY m.id
            """,
            (placa, ano)
        ).fetchall()

        multas = []

        for registro in registros:
            multas.append({
                "ano": registro[0],
                "descricao": registro[1],
                "pontuacao": registro[2],
                "placa": registro[3],
                "cpf_condutor": registro[4],
                "nome_condutor": registro[5]
            })

        return {
            "sucesso": True,
            "multas": multas
        }

    finally:
        conexao.close()


def multas_condutor(dados):
    cpf = dados["cpf"]
    ano = dados["ano"]

    conexao = conectar()

    try:
        registros = conexao.execute(
            """
            SELECT
                ano,
                descricao,
                pontuacao,
                placa
            FROM multas

            WHERE cpf_condutor = ?
              AND ano = ?

            ORDER BY id
            """,
            (cpf, ano)
        ).fetchall()

        multas = []

        for registro in registros:
            multas.append({
                "ano": registro[0],
                "descricao": registro[1],
                "pontuacao": registro[2],
                "placa": registro[3]
            })

        return {
            "sucesso": True,
            "multas": multas
        }

    finally:
        conexao.close()


def multas_ano(dados):
    ano = dados["ano"]

    conexao = conectar()

    try:
        registros = conexao.execute(
            """
            SELECT
                m.ano,
                m.descricao,
                m.pontuacao,
                m.placa,
                m.cpf_condutor,
                c.nome
            FROM multas m

            JOIN condutores c
                ON c.cpf = m.cpf_condutor

            WHERE m.ano = ?

            ORDER BY m.id
            """,
            (ano,)
        ).fetchall()

        multas = []

        for registro in registros:
            multas.append({
                "ano": registro[0],
                "descricao": registro[1],
                "pontuacao": registro[2],
                "placa": registro[3],
                "cpf_condutor": registro[4],
                "nome_condutor": registro[5]
            })

        return {
            "sucesso": True,
            "multas": multas
        }

    finally:
        conexao.close()


def top5_condutores():
    conexao = conectar()

    try:
        registros = conexao.execute(
            """
            SELECT
                m.cpf_condutor,
                c.nome,
                SUM(m.pontuacao) AS total_pontos

            FROM multas m

            JOIN condutores c
                ON c.cpf = m.cpf_condutor

            GROUP BY
                m.cpf_condutor,
                c.nome

            ORDER BY total_pontos DESC

            LIMIT 5
            """
        ).fetchall()

        condutores = []

        for registro in registros:
            condutores.append({
                "cpf": registro[0],
                "nome": registro[1],
                "pontuacao": registro[2]
            })

        return {
            "sucesso": True,
            "condutores": condutores
        }

    finally:
        conexao.close()


def ao_receber(client, userdata, mensagem):
    dados = json.loads(
        mensagem.payload.decode()
    )

    if mensagem.topic == TOPICO_LANCAR:
        resposta = lancar_multa(dados)

    elif mensagem.topic == TOPICO_VEICULO:
        resposta = multas_veiculo(dados)

    elif mensagem.topic == TOPICO_CONDUTOR:
        resposta = multas_condutor(dados)

    elif mensagem.topic == TOPICO_ANO:
        resposta = multas_ano(dados)

    elif mensagem.topic == TOPICO_TOP5:
        resposta = top5_condutores()

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

print("Serviço de multas aguardando requisições...")

client.loop_forever()