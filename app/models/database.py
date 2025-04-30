import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

#gerencia a conexão com o banco de dados
class Database:
    def __init__(self):
        self.db_config = {
            "host": os.getenv("DB_HOST"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "database": os.getenv("DB_NAME")
        }
        self.conexao = None

    def _conectar(self):
        self.conexao = mysql.connector.connect(**self.db_config)

    def execute(self, query, params=None, fetch=False, varios=False):
        cursor = None
        try:
            self._conectar()
            cursor = self.conexao.cursor(dictionary=True)

            if varios:
                cursor.executemany(query, params or [])
            else:
                cursor.execute(query, params or ())

            if fetch:
                return cursor.fetchall()

            self.conexao.commit()
            return cursor.lastrowid

        except mysql.connector.Error as e:
            if self.conexao:
                self.conexao.rollback()
            print(f"Erro no banco de dados: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if self.conexao:
                self.conexao.close()
