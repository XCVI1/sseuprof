import configparser
import os

# Путь к файлу конфигурации
config_file_path = os.path.join(os.path.dirname(__file__), 'config.pgsql')

# Чтение параметров из файла конфигурации
config = configparser.ConfigParser()
config.read(config_file_path)

DATABASE = {
    'host': config.get('postgresql', 'host'),
    'port': config.getint('postgresql', 'port'),
    'dbname': config.get('postgresql', 'dbname'),
    'user': config.get('postgresql', 'user'),
    'password': config.get('postgresql', 'password')
}

TOKEN = '7544054917:AAHY9c5eMYQPXWZ15mNS8wqVFlRmSOJtwrI'