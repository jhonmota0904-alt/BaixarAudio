import time, os 
from threading import Lock



class Logger:
    __instacia = None
    def __new__(cls):
        if cls.__instacia is None:
            cls.__instacia = super().__new__(cls)
        return cls.__instacia

    def __init__(self, pasta="core/logs"):
        if getattr(self, "_inicializado", False):
            return

        self.pasta = pasta
        os.makedirs(self.pasta, exist_ok=True)

        # Define o caminho dos logs
        self.log_erro = os.path.join(pasta, "log_erro.txt")
        self.log_evento = os.path.join(pasta, "log_evento.txt")
        self.log_aviso = os.path.join(pasta, "log_aviso.txt")

        self.lock = Lock()

    def _escrever(self, caminho: str, mensagem: str, prefixo: str="") -> None:
        data_hora = time.strftime("%d/%m/%Y - %H:%M:%S", time.localtime())
        linha = f"{data_hora} {prefixo}{mensagem}"
        with self.lock:
            with open(caminho, "a", encoding="utf-8") as arquivo:
                arquivo.write(linha + "\n")

    def erro(self, erro: str) -> None:
        self._escrever(self.log_erro, str(erro), prefixo="ERRO: ")

    def evento(self, evento: str) -> None:
        self._escrever(self.log_evento, str(evento), prefixo="EVENTO: ")

    def aviso(self, aviso: str) -> None:
        self._escrever(self.log_aviso, str(aviso), prefixo="AVISO: ")

    def exibir(self, mensagem: str) -> None:
        print(mensagem)



