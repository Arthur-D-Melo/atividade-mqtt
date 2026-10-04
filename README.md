# Atividade MQTT - Sistemas Distribuídos

Atividade desenvolvida utilizando MQTT para comunicação entre microsserviços.

O sistema possui três serviços principais:

- serviço de condutores;
- serviço de veículos;
- serviço de multas.

A comunicação entre eles é feita pelo broker Mosquitto utilizando o protocolo MQTT.

Os dados são armazenados em um banco SQLite compartilhado entre os serviços.

## Funcionalidades

O sistema permite:

- cadastrar condutores;
- emplacar veículos;
- calcular o IPVA de um veículo;
- transferir o proprietário de um veículo;
- lançar multas;
- consultar veículos emplacados por ano;
- consultar multas de um veículo por ano;
- consultar multas de um condutor por ano;
- consultar multas lançadas em um ano;
- consultar os 5 condutores com maior pontuação em multas.

## Execução

É necessário ter Docker instalado e em execução.

Para construir os containers:

```bash
docker compose build
```

Para iniciar o sistema:

```bash
docker compose up -d
```

Para verificar os containers:

```bash
docker compose ps -a
```

O container `detran-init-db` deve aparecer como `Exited (0)`, pois ele apenas cria ou verifica as tabelas do banco e encerra.

## Exemplos de uso

Cadastrar um condutor:

```bash
docker compose run --rm client python client.py cadastrar-condutor 12345678900 Arthur
```

Emplacar um veículo:

```bash
docker compose run --rm client python client.py emplacar ABC1D23 Civic 80000 12345678900
```

Calcular o IPVA:

```bash
docker compose run --rm client python client.py ipva ABC1D23
```

Cadastrar o novo proprietário:

```bash
docker compose run --rm client python client.py cadastrar-condutor 98765432100 Joao
```

Transferir o proprietário:

```bash
docker compose run --rm client python client.py transferir ABC1D23 98765432100
```

Lançar uma multa:

```bash
docker compose run --rm client python client.py lancar-multa 2026 "Excesso de velocidade" 5 ABC1D23
```

Consultar veículos emplacados em um ano:

```bash
docker compose run --rm client python client.py veiculos-ano 2026
```

Consultar multas de um veículo:

```bash
docker compose run --rm client python client.py multas-veiculo ABC1D23 2026
```

Consultar multas de um condutor:

```bash
docker compose run --rm client python client.py multas-condutor 98765432100 2026
```

Consultar multas lançadas em um ano:

```bash
docker compose run --rm client python client.py multas-ano 2026
```

Consultar os 5 condutores com maior pontuação:

```bash
docker compose run --rm client python client.py top5
```

## Encerrando

Para parar os containers:

```bash
docker compose down
```

O banco de dados permanece salvo na pasta `data/`.