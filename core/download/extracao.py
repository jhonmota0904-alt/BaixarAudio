import yt_dlp
import io
import urllib.request
from PIL import Image
from core.logs.log import Logger
from threading import Event

class ExtratorInformacoes:
    def __init__(self):
       self.logging = Logger()

    def extrair(self, url: str, cancelamento: Event | None = None) -> dict | None:
        opcoes = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "noplaylist": True,
        }
        if cancelamento is not None:
            opcoes.update({"socket_timeout": 5, "retries": 1})

        try:
            with yt_dlp.YoutubeDL(opcoes) as ydl:
                info = ydl.extract_info(url, download=False)
        except Exception as erro:
            if cancelamento is not None and cancelamento.is_set():
                return None
            self.logging.exibir(f"falha ao extrair informações de {url} -> {erro}")
            self.logging.erro(f"falha ao extrair informações de {url} -> {erro}")
            return

        if cancelamento is not None and cancelamento.is_set():
            return None

        return self._formatar(info)

    def _formatar(self, info: dict) -> dict:
        formats = info.get("formats", [])
        return {
            "nome": info.get("title", ""),
            "canal": info.get("uploader", ""),
            "data": self._formatar_data(info.get("upload_date", "")),
            "visualizacao": self._formatar_numero(info.get("view_count")),
            "duracao": self._formatar_duracao(info.get("duration")),
            "tamanho": self._estimar_tamanho(info),
            "qualidades_video": self._extrair_alturas(formats),
            "formatos_video": self._extrair_extencao_video(formats),
            "thumbnail": info.get("thumbnail")
        }   

    def _formatar_data(self, data: str | None) -> str:
        if not data or len(data) != 8:
            return "//"
        return f"{data[6:8]}/{data[4:6]}/{data[:4]}" 

    def _formatar_numero(self, numero: int) -> str | None:
        if numero is None:
            return "_"
        if numero >= 1_000_000:
            return f"{numero/1_000_000:.1f}M".replace(",", ".")
        if numero >= 1_000:
            return f"{numero/1_000:.1f}K".replace(",", ".")

        return str(numero)

    def _formatar_duracao(self, duracao: int) -> str | None:
        if duracao is None:
            return "_"

        horas, resto = divmod(duracao, 3600)
        minutos, segundos = divmod(resto, 60)

        return f"{horas}:{minutos:02d}:{segundos:02d}" if horas else f"{minutos:02d}:{segundos:02d}"

    def _estimar_tamanho(self, info: dict) -> str | None:
        formatos = info.get('formats', [])
        candidatos = [
            f.get('filesize') or f.get('filesize_approx') 
            for f in formatos if 
            f.get('filesize') or f.get('filesize_approx')
        ]

        if not candidatos:
            return "_"

        mb = max(candidatos) / (1024 * 1024)
        return f"{mb:.0f} MB"

    def _extrair_alturas(self, formats: list) -> list[str]:
        alturas = set()

        for item in formats:
            if item.get('vcodec') == "none":
                continue
            altura = item.get('height')
            if altura:
                alturas.add(int(altura))
        return [f"{altr}p" for altr in sorted(alturas, reverse=True)]

    def _extrair_extencao_video(self, formats: list) -> list[str]:
        extencoes = set()

        for item in formats:
            if item.get('vcodec') == "none":
                continue

            extencao = item.get('ext')
            if extencao:
                extencoes.add(extencao)
        comuns = {"mp4", "mkv", "webm"}
        return sorted((extencoes | {"mp4", "mkv"}) & comuns)

    def playlist_urls(self, playlist) -> list[dict]:
        with yt_dlp.YoutubeDL({ 
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "extract_flat": True,
            "playlist_items": "1-10"}
        ) as ydl:
            entries = ydl.extract_info(playlist.get("url"), download=False).get("entries") or []

            return [{
                "tipo": playlist["tipo_playlist"],
                "tipo_playlist": "_",
                "qualidade": playlist["qualidade"],
                "formato": playlist["formato"],
                "url": item["url"],
                "destino": playlist["destino"],
            } for item in entries if item.get("url")] 
class ExtratorThumbnail:
    def __init__(self):
        self.logging = Logger()
        
    def carregar_thumbnail(self, url: str) -> Image.Image | None: 
        try:      
            with urllib.request.urlopen(url) as resp:
                dados = resp.read()
            return Image.open(io.BytesIO(dados)).convert("RGB")
          
        except Exception as erro:
            self.logging.exibir(f"Falha ao baixar thumbnail -> {erro}")
            self.logging.erro(f"Falha ao baixar thumbnail -> {erro}")
            return None

