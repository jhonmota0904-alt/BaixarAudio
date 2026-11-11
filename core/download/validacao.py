import os
import core.logs.log as log

class ValidadorTipoDownload:    
    def __init__(self, tipo_download):
        self.opcoes_download = ['audio', 'video', 'playlist']
        self.tipo_suportado = bool(tipo_download in self.opcoes_download)
        self.tipo = tipo_download


class PreparadorDestino:
    def __init__(self, destino):
        self.logging = log.Logger()
        self.destino = destino
        self.destino_existe = self.checar_destino()


    def checar_destino(self):
        try:
            return os.path.exists(self.destino)
        except TypeError:
            self.logging.exibir(f"O destino não pode estar vazio")
            self.logging.erro(f"O destino não pode estar vazio")

    def criar_destino(self) -> bool:
        try:
            os.makedirs(self.destino, exist_ok=True)
            self.logging.exibir("Pasta destino criada")
            self.logging.evento("Pasta destino criada")
            return True
        
        # Ainda para fazer
        except PermissionError:
            self.logging.exibir(f"Sem permissão para criar pasta destino")
            self.logging.erro(f"Sem permissão para criar pasta destino")
            return False
        
        except Exception as erro:
            self.logging.exibir(f"Erro na hora de criar pasta destino -> {erro}")
            self.logging.erro(f"Erro na hora de criar pasta destino -> {erro}")
            return False
           

class ValidacaoDownload:
    def __init__(self, tipo, destino):
        self.logging = log.Logger()
        self.validador_tipo = ValidadorTipoDownload(tipo)
        self.preparador_destino = PreparadorDestino(destino)

    def tipo(self) -> bool:
        tipo_valido = self.validador_tipo.tipo_suportado
        if not tipo_valido:
            self.logging.exibir(f"Tipo não compatível -> {self.validador_tipo.tipo}")
            self.logging.aviso(f"Tipo não compatível -> {self.validador_tipo.tipo}")
        return tipo_valido

    def destino(self) -> bool:
        destino_existe = self.preparador_destino.destino_existe
        if not destino_existe:
            return self.preparador_destino.criar_destino()
        return destino_existe

    def validar_download(self) -> bool:
        if not self.tipo():
            return False

        if not self.destino():
            return False

        return True
    