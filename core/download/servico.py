from concurrent.futures import Future, ThreadPoolExecutor
from core.download.extracao import ExtratorInformacoes
from core.download.strategy import criar_strategy
from core.download.validacao import ValidacaoDownload
from core.eventos.observavel import Observavel
from core.logs.log import Logger
from threading import Event, Lock

class ServicoDownload(Observavel):
    def __init__(self):
        super().__init__()
        self.extrator = ExtratorInformacoes()
        self.logging = Logger()
        self.executor = ThreadPoolExecutor(max_workers=3)
        self._baixados: list[dict] = []
        self._pendentes = 0
        self._lock = Lock()
        self._cancelamento = Event()
        self._encerrando = False

    def killer(self) -> None:
        with self._lock:
            self._encerrando = True
            self._cancelamento.set()

        self.executor.shutdown(wait=True, cancel_futures=True)

    def baixar(self, para_baixar: list[dict]) -> None:
        novos = []
        for item in para_baixar:
            if item.get("tipo") == 'playlist':
                novos.extend(self.extrator.playlist_urls(item))
                #novos.update(map(dict, self.extrator.playlist_urls(item)))
            else:
                novos.append(item)

        with self._lock:
            if self._encerrando:
                raise RuntimeError("Não é possível iniciar downloads durante o encerramento.")

            a_submeter = [item for item in novos if item not in self._baixados]
            try:
                for item in a_submeter:
                    tarefa = self.executor.submit(
                        self._executar,
                        item['tipo'], item['url'], item['destino'],
                        item['qualidade'], item['formato'],
                    )
                    self._baixados.append(item)
                    self._pendentes += 1
                    tarefa.add_done_callback(self._ajustar_pendentes_cancelados)
            finally:
                self._baixados.clear()

    def _ajustar_pendentes_cancelados(self, tarefa: Future) -> None:
        if tarefa.cancelled():
            with self._lock:
                self._pendentes -= 1

            
    def _executar(self, tipo: str, url: str, destino: str, qualidade: str, formato: str) -> None:
        try:
            if self._cancelamento.is_set():
                return

            if not ValidacaoDownload(tipo, destino).validar_download():
                self.logging.exibir(f"Validação de tipo e destino barrou download. URL-> {url}")
                self.logging.aviso(f"Validação de tipo e destino barrou download. URL-> {url}")
                return

            try:
                info = self.extrator.extrair(url, cancelamento=self._cancelamento)
                if self._cancelamento.is_set():
                    return

                titulo = info['nome'] if info else url
                self.notificar({"tipo": "iniciado", "titulo": titulo})
                self._baixar_um(tipo, url, destino, qualidade, formato)
                if not self._cancelamento.is_set():
                    self.notificar({"tipo": "concluido", "titulo": titulo})
            except Exception as erro:
                if not self._cancelamento.is_set():
                    self.logging.exibir(f"Falha no download de {url} -> {erro}")
                    self.logging.erro(f"Falha no download de {url} -> {erro}")
                    self.notificar({"tipo": "erro", "mensagem": str(erro)})

        finally:
            with self._lock:
                self._pendentes -= 1
                restam = self._pendentes
                if restam == 0 and not self._cancelamento.is_set():
                    self.notificar({"tipo": "todos_concluidos"})

    def _baixar_um(self, tipo:str, url: str, destino: str, qualidade: str, formato: str) -> None:
        strategy = criar_strategy(
            tipo, url, destino, qualidade, formato,
            ao_progredir=self.notificar,
            cancelamento=self._cancelamento,
        )
        strategy.executar()

