
import config
from config import Config

print("Arquivo config carregado:", config.__file__)
print("Arquivo da classe Config:", Config.__module__)
print("Senha configurada:", bool(Config.MYSQL_PASSWORD))
print("Tamanho da senha:", len(Config.MYSQL_PASSWORD))
print("Banco:", Config.MYSQL_DATABASE)