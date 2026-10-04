import os

from database import conectar


os.makedirs("data", exist_ok=True)

conexao = conectar()

cursor = conexao.cursor()


cursor.execute("""
    CREATE TABLE IF NOT EXISTS condutores (
        cpf TEXT PRIMARY KEY,
        nome TEXT NOT NULL
    )
""")


cursor.execute("""
    CREATE TABLE IF NOT EXISTS veiculos (
        placa TEXT PRIMARY KEY,
        modelo TEXT NOT NULL,
        valor REAL NOT NULL,
        cpf_condutor TEXT NOT NULL,
        ano_emplacamento INTEGER NOT NULL,

        FOREIGN KEY (cpf_condutor)
        REFERENCES condutores(cpf)
    )
""")


cursor.execute("""
    CREATE TABLE IF NOT EXISTS multas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ano INTEGER NOT NULL,
        descricao TEXT NOT NULL,
        pontuacao INTEGER NOT NULL,
        placa TEXT NOT NULL,
        cpf_condutor TEXT NOT NULL,

        FOREIGN KEY (placa)
        REFERENCES veiculos(placa),

        FOREIGN KEY (cpf_condutor)
        REFERENCES condutores(cpf)
    )
""")


conexao.commit()
conexao.close()

print("Banco de dados criado com sucesso.")