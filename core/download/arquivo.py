import os
import csv
from core.logs.log import Logger

class Arquivo:
    def __init__(self, arquivo: str="core"):
        self.arquivo = arquivo
        self.logging = Logger()
      
    def ler(self, arquivo:str) -> list[dict]:
        arquivo = os.path.join(self.arquivo, arquivo)
        try:
            with open(arquivo, "r", encoding="utf-8", newline="") as arquivo:
                leitor = csv.DictReader(
                    arquivo,
                    fieldnames=['tipo', 'tipo_playlist', 'qualidade', 'formato', 'url', 'destino'],
                    delimiter=";")
                return [linha for linha in leitor]
            
        except FileNotFoundError:
            self.logging.exibir(f"Arquivo '{arquivo}' não encontrado!")
            self.logging.erro(f"Arquivo '{arquivo}' não encontrado!")
        except Exception as erro:
            self.logging.exibir(erro)
            self.logging.erro(erro)

    def ler_historico_fila(self, arquivo:str) -> list[dict]:
        arquivo = os.path.join(self.arquivo, arquivo)
        try:
            with open(arquivo, "r", encoding="utf-8", newline="") as arquivo:
                leitor = csv.DictReader(
                    arquivo,
                    fieldnames=['nome'],
                    delimiter=";")
                return [linha for linha in leitor]
            
        except FileNotFoundError:
            self.logging.exibir(f"Arquivo '{arquivo}' não encontrado!")
            self.logging.erro(f"Arquivo '{arquivo}' não encontrado!")
        except Exception as erro:
            self.logging.exibir(erro)
            self.logging.erro(erro)

    def escrever(self, dados: list, caminho:str) -> None:
        if not dados:
            return
        caminho = os.path.join(self.arquivo, caminho)
        
        try:
            with open(caminho, 'a', newline="", encoding='utf-8') as arquvio:
                escritor = csv.writer(arquvio, delimiter=';')
                escritor.writerow(dados)
            self.logging.exibir(f"Nova linha escrit em '{caminho}'")
            self.logging.evento(f"Nova linha escrit em '{caminho}'")
            
        except FileNotFoundError:
            self.logging.exibir(f"Arquivo '{caminho}' não encontrado!")
            self.logging.erro(f"Arquivo '{caminho}' não encontrado!")
        except Exception as erro:
            self.logging.exibir(erro)
            self.logging.erro(erro)

    def limpar(self, arquivo) -> None:
        arquivo = os.path.join(self.arquivo, arquivo)
        try:
            os.remove(arquivo)
            self.logging.exibir(f"Arquivo '{arquivo}' removido.")
            self.logging.evento(f"Arquivo '{arquivo}' removido.")
        except FileNotFoundError:
            self.logging.exibir(f"Arquivo '{arquivo}' não encontrado!")
            self.logging.erro(f"Arquivo '{arquivo}' não encontrado!")
        except Exception as erro:
            self.logging.exibir(erro)       
            self.logging.erro(erro)       

