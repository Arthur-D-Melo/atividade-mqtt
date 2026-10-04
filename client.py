import argparse
import json
import os
import uuid

import paho.mqtt.client as mqtt


BROKER = os.getenv("MQTT_HOST", "localhost")
PORTA = int(os.getenv("MQTT_PORT", "1883"))


parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(
    dest="operacao",
    required=True
)


cadastrar = subparsers.add_parser(
    "cadastrar-condutor"
)
cadastrar.add_argument("cpf")
cadastrar.add_argument("nome")


transferir = subparsers.add_parser(
    "transferir"
)
transferir.add_argument("placa")
transferir.add_argument("cpf")


emplacar = subparsers.add_parser(
    "emplacar"
)
emplacar.add_argument("placa")
emplacar.add_argument("modelo")
emplacar.add_argument("valor", type=float)
emplacar.add_argument("cpf")


ipva = subparsers.add_parser(
    "ipva"
)
ipva.add_argument("placa")


veiculos_ano = subparsers.add_parser(
    "veiculos-ano"
)
veiculos_ano.add_argument("ano", type=int)


lancar_multa = subparsers.add_parser(
    "lancar-multa"
)
lancar_multa.add_argument("ano", type=int)
lancar_multa.add_argument("descricao")
lancar_multa.add_argument("pontuacao", type=int)
lancar_multa.add_argument("placa")


multas_veiculo = subparsers.add_parser(
    "multas-veiculo"
)
multas_veiculo.add_argument("placa")
multas_veiculo.add_argument("ano", type=int)


multas_condutor = subparsers.add_parser(
    "multas-condutor"
)
multas_condutor.add_argument("cpf")
multas_condutor.add_argument("ano", type=int)


multas_ano = subparsers.add_parser(
    "multas-ano"
)
multas_ano.add_argument("ano", type=int)


subparsers.add_parser(
    "top5"
)


args = parser.parse_args()


if args.operacao == "cadastrar-condutor":
    topico_pedido = "detran/condutores/cadastrar"

    dados = {
        "cpf": args.cpf,
        "nome": args.nome
    }


elif args.operacao == "transferir":
    topico_pedido = "detran/condutores/transferir"

    dados = {
        "placa": args.placa,
        "cpf": args.cpf
    }


elif args.operacao == "emplacar":
    topico_pedido = "detran/veiculos/emplacar"

    dados = {
        "placa": args.placa,
        "modelo": args.modelo,
        "valor": args.valor,
        "cpf": args.cpf
    }


elif args.operacao == "ipva":
    topico_pedido = "detran/veiculos/ipva"

    dados = {
        "placa": args.placa
    }


elif args.operacao == "veiculos-ano":
    topico_pedido = "detran/veiculos/ano"

    dados = {
        "ano": args.ano
    }


elif args.operacao == "lancar-multa":
    topico_pedido = "detran/multas/lancar"

    dados = {
        "ano": args.ano,
        "descricao": args.descricao,
        "pontuacao": args.pontuacao,
        "placa": args.placa
    }


elif args.operacao == "multas-veiculo":
    topico_pedido = "detran/multas/veiculo"

    dados = {
        "placa": args.placa,
        "ano": args.ano
    }


elif args.operacao == "multas-condutor":
    topico_pedido = "detran/multas/condutor"

    dados = {
        "cpf": args.cpf,
        "ano": args.ano
    }


elif args.operacao == "multas-ano":
    topico_pedido = "detran/multas/ano"

    dados = {
        "ano": args.ano
    }


elif args.operacao == "top5":
    topico_pedido = "detran/multas/top5"

    dados = {}


id_requisicao = str(uuid.uuid4())

topico_resposta = (
    f"detran/respostas/{id_requisicao}"
)

dados["resposta_em"] = topico_resposta


def ao_conectar(
    client,
    userdata,
    flags,
    reason_code,
    properties
):
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
    client.publish(
        topico_pedido,
        json.dumps(dados)
    )


def ao_receber(
    client,
    userdata,
    mensagem
):
    resposta = json.loads(
        mensagem.payload.decode()
    )

    print(
        json.dumps(
            resposta,
            indent=2,
            ensure_ascii=False
        )
    )

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