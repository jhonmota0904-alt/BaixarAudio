import yt_dlp
from concurrent.futures import ThreadPoolExecutor
from core.download.extracao import ExtratorInformacoes
from core.download.strategy import criar_strategy
from core.download.validacao import ValidacaoDownload
from core.eventos.observavel import Observavel
from core.logs.log import Logger
from threading import Lock

class ServicoDownload(Observavel):
    def __init__(self):
        super().__init__()
        self.extrator = ExtratorInformacoes()
        self.logging = Logger()
        self.executor = ThreadPoolExecutor(max_workers=3)
        self._baixados: list[dict] = []
        self._pendentes = 0
        self._lock = Lock()
      
    def baixar(self, para_baixar: list[dict]) -> None:
        novos = []
        for item in para_baixar:
            if item.get("tipo") == 'playlist':
                novos.extend(self.extrator.playlist_urls(item))
            else:
                novos.append(item)

        with self._lock:
            a_submeter = [item for item in novos if item not in self._baixados]
            for item in a_submeter:
                self._baixados.append(item)
            self._pendentes += len(a_submeter)

        if not a_submeter:
            return

        for item in a_submeter:
            self.executor.submit(
                self._executar,
                item['tipo'], item['url'], item['destino'], 
                item['qualidade'], item['formato'],)
        self._baixados.clear()

            
    def _executar(self, tipo: str, url: str, destino: str, qualidade: str, formato: str) -> None:
        try:
            if not ValidacaoDownload(tipo, destino).validar_download():
                self.logging.exibir(f"Validação de tipo e destino barrou download. URL-> {url}")
                self.logging.aviso(f"Validação de tipo e destino barrou download. URL-> {url}")
                return

            try:
                info = self.extrator.extrair(url)
                titulo = info['nome'] if info else url
                self.notificar({"tipo": "iniciado", "titulo": titulo})
                self._baixar_um(tipo, url, destino, qualidade, formato)
                self.notificar({"tipo": "concluido", "titulo": titulo})
            except Exception as erro:
                self.logging.exibir(f"Falha no download de {url} -> {erro}")
                self.logging.erro(f"Falha no download de {url} -> {erro}")
                self.notificar({"tipo": "erro", "mensagem": str(erro)})

        finally:
            with self._lock:
                self._pendentes -= 1
                restam = self._pendentes
                if restam == 0:
                    self.notificar({"tipo": "todos_concluidos"})

    def _baixar_um(self, tipo:str, url: str, destino: str, qualidade: str, formato: str) -> None:
        strategy = criar_strategy(
            tipo, url, destino, qualidade, formato, ao_progredir=self.notificar
        )
        strategy.executar()

