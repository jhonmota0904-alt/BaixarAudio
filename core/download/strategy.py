import imageio_ffmpeg
import yt_dlp
from abc import ABC, abstractmethod
from core.logs.log import Logger
from core.download.arquivo import Arquivo


class DownloadStrategy(ABC): 
    def __init__(self, url: str, destino:str, qualidade:str, formato: str,  ao_progredir=None):
        # Variávies para download
        self.url = url
        self.destino = destino
        self.qualidade = qualidade
        self.formato = formato
        
        # Faz o log
        self.logging = Logger()

        # Ler os arquivos
        self.arquivo = Arquivo()

        # Callabel
        self.ao_progredir = ao_progredir 

    @abstractmethod
    def _opcoes(self) -> dict:
        pass

    def _porcentagem(self, dicionario: dict) -> None:
        if dicionario == None or self.ao_progredir == None:
            return

        status = dicionario.get("status")
        info = dicionario.get("info_dict", {})

        if status == "downloading":
            total = dicionario.get("total_bytes") or dicionario.get("total_bytes_estimate") or 0
            baixado = dicionario.get("downloaded_bytes", 0)
            porcentagem = (baixado / total * 100) if total else 0.0

            video = info.get('vcodec') or "none"
            audio = info.get('acodec') or "none"

            if video == 'none':
                fase = 'Áudio'
            elif audio == 'none':
                fase = 'Vídeo'
            else:
                fase = 'Baixando'

            self.ao_progredir({
                "tipo": "progresso",
                "fase": fase,
                "percentual": porcentagem,
                "velocidade": (dicionario.get('_speed_str') or "").strip( ),
                "eta": (dicionario.get('_eta_str') or "").strip()
            })
        elif status == "finished":
            self.ao_progredir({"tipo": "progresso", "fase": "Finalizando", "percentual": 100.0})

    def executar(self) -> None:
        opcoes = self._opcoes()
        if self.ao_progredir is not None:
            opcoes["progress_hooks"] = [self._porcentagem]

        try:
            with yt_dlp.YoutubeDL(opcoes) as ydl:
                informacoes_url = ydl.extract_info(self.url, download=False)
                self.logging.exibir(f"Iniciando download -> {informacoes_url.get('title')}")
                self.logging.evento(f"Iniciando download -> {informacoes_url.get('title')}")
                ydl.download([self.url]) 
                self.logging.exibir(f"Download concluído -> {informacoes_url.get('title')}")
                self.logging.evento(f"Download concluído -> {informacoes_url.get('title')}")
                self.arquivo.escrever([informacoes_url.get('title'), self.url], "historico.csv")
               
        except Exception as erro:
            self.logging.exibir(f"Download interrompido -> {erro}")
            self.logging.erro(f"Download interrompido -> {erro}")
            raise

class DownloadAudio(DownloadStrategy):
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    def _opcoes(self):
        return {
            "format": "bestaudio/best",
            "outtmpl": f"{self.destino}/%(title)s.%(ext)s",
            "quiet": True,
            "noplaylist": True,
            "ffmpeg_location": self.ffmpeg,
            "postprocessors": [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': self.formato,
                'preferredquality': '192'
            }]
        }

class DownloadVideo(DownloadStrategy):
    def _opcoes(self) -> dict:
        altura = self.qualidade.replace("p", "")
        return {
            "format": f"bestvideo[height<={altura}]+bestaudio/best[height<={altura}]",
            "outtmpl": f"{self.destino}/%(title)s.%(ext)s",
            "quiet": True,
            "noplaylist": True,
            "ffmpeg_location": self.ffmpeg,
            "merge_output_format": self.formato
        }

def criar_strategy(tipo: str, url: str, destino: str, qualidade: str, formato: str, ao_progredir=None) -> DownloadStrategy:
    mapa = {
        "audio": DownloadAudio,
        "video": DownloadVideo
    }

    if tipo not in mapa:
        raise ValueError(f"Tipo inválido: {tipo}")

    return mapa[tipo](url, destino, qualidade, formato, ao_progredir)