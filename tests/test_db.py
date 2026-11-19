
from config import Config
import pymysql

print("Testando conexão com o MariaDB...")

try:
    conexao = pymysql.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE,
        charset="utf8mb4"
    )

    print("\nCONEXÃO REALIZADA COM SUCESSO!")

    with conexao.cursor() as cursor:
        cursor.execute("SELECT DATABASE(), VERSION()")
        banco, versao = cursor.fetchone()

        cursor.execute("SHOW TABLES")
        tabelas = cursor.fetchall()

        print("Banco:", banco)
        print("Versão:", versao)
        print("Total de tabelas:", len(tabelas))

    conexao.close()

except Exception as erro:
    print("\nFALHA NA CONEXÃO!")
    print("Detalhes:", erro)
