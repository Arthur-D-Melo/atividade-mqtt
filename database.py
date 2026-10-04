import os
import sqlite3


CAMINHO_BANCO = os.getenv(
    "DATABASE_PATH",
    "data/detran.db"
)


def conectar():
    conexao = sqlite3.connect(
        CAMINHO_BANCO,
        timeout=30
    )

    conexao.execute(
        "PRAGMA foreign_keys = ON"
    )

    return conexao