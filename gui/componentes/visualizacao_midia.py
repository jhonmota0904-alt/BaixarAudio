import customtkinter as ctk
import pyvidplayer2
import tkinter as tk
import tkinter.font as tkfont
from PIL import Image
from core.logs.log import Logger
from core.download.arquivo import Arquivo
from core.download.extracao import ExtratorThumbnail
from core.eventos.toast import Toast



class VideoPlayer(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, width=275, height=225)

        # Configura o grid interno
        self.grid_propagate(False)

        # Conexão com o log
        self.logging = Logger()
        self.extrator = ExtratorThumbnail()
        99
        # Frame do vídeo
        self.player_frame = ctk.CTkFrame(self, width=275, height=175, fg_color='black')
        self.player_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nswe')
        self.player_frame.grid_propagate(False)
        self.player_frame.grid_rowconfigure(0, weight=1)
        self.player_frame.grid_columnconfigure(0, weight=1)

        # Canva para exibir o vídeo
        self.canvas = tk.Canvas(
            self.player_frame, width=275, height=175,
            bg='black', highlightthickness=0)
        self.canvas.grid(row=0, column=0, padx=0, pady=(0,0), sticky='nsew')

        # Thumbnail do vídeo
        self.thumbs_vivas: list[ctk.CTkImage] = []
        self.exibir_thumbnail = ctk.CTkLabel(self.canvas, text='')
        self.thumb_image = None

        # Mensagem de Erro
        self.mensagem_erro = ctk.CTkLabel(
        self.player_frame,
            text="Não foi possível carregar o vídeo!\nVerifique a URL.",
            justify='center')

        # Estado + Vídeo
        self.status = 'inicio'
        self.video = None


        # Frame de botões
        botoes_frame = ctk.CTkFrame(
            self, height=30, width=265, fg_color='transparent', bg_color='transparent')
        botoes_frame.grid(row=1, column=0, sticky='nwe')

        # Botões
        self.botao_play_pause = ctk.CTkButton(
            botoes_frame, text='Play', command=self._play_pause, height=20, width=265)
        self.botao_play_pause.grid(
            row=0, column=0, padx=10, pady=(0, 5), sticky='we')

        
    def carregar_video(self, url: str, thumbnail_url: str | None = None) -> None:
        self._close()
        self._resetar_estado()

        if thumbnail_url:
            self._atualizar_thumbnail(thumbnail_url)
            self._mostrar_thumbnail()

        try:
            self.video = pyvidplayer2.VideoTkinter(url, youtube=True, max_res=720, chunk_size=60)
            self._ajustar_video_ao_canvas()
            self.video.pause() # Inicia com o vídeo pausado
            return True

        except Exception as erro:
            self.status = 'erro'
            self._esconder_thumbnail()
            self._mostrar_erro()
            self.logging.exibir(f"Não foi possível carregar o vídeo -> {erro}")
            self.logging.erro(f"Não foi possível carregar o vídeo -> {erro}")
            return False

    def _ajustar_video_ao_canvas(self) -> None:
        if not self.video:
            return
        largura_canvas, altura_canvas = 275, 175

        try:
            largura_orig, altura_orig = self.video.original_size
        except Exception:

            largura_orig, altura_orig = self.video.current_size
        
        #print(f"Tamanho original: {largura_orig}x{altura_orig}")

        if largura_orig <= 0 or altura_orig <= 0:
            return

        escala = max(largura_canvas / largura_orig, altura_canvas / altura_orig)
        
        nova_largura = max(1, int(largura_orig * escala))
        nova_altura = max(1, int(altura_orig * escala))

        self.video.resize(size=(nova_largura, nova_altura))
        
        # Log para você ver o tamanho final
        self.logging.exibir(f"Novo tamanho: {nova_largura}x{nova_altura}")

    def _resetar_estado(self) -> None:
        self.status = 'inicio'
        self._esconder_thumbnail()
        self._esconder_erro()
        self.canvas.delete('all')
        self.botao_play_pause.configure(text='Play')
        if len(self.thumbs_vivas) >= 2:
            self.thumbs_vivas.pop(0)

    def _play_pause(self) -> None:
        if self.status == 'erro':
            return
        
        if self.status == 'inicio' and self.video:
            self._esconder_thumbnail()
            self.status = 'video'

            if self.video:
                self.video.toggle_pause()
            self.botao_play_pause.configure(text='Pause')
            self._atualizar_frame()
            return

        if self.status == 'video':
            self.video.toggle_pause()
            pausado =  getattr(self.video, 'paused', False)
            self.botao_play_pause.configure(text='Play' if pausado else 'Pause')
        
    def _atualizar_frame(self) -> None:
        if self.status != 'video':
            return
        
        if self.video and self.video.active:
            #centro = (275 // 2, 175 // 2) # Centro do canvas
            centro = (137, 87) 
            self.video.draw(self.canvas, centro)
            self.after(15, self._atualizar_frame)
            
    def _close(self) -> None:
        if self.video:
            try:
                self.video.pause()
                self.video.close()
            except Exception:
                pass
            self.video = None

    def _atualizar_thumbnail(self, thumbnail_url: str) -> None:
        pil_img = self.extrator.carregar_thumbnail(thumbnail_url)
        if pil_img is None:
            return
        nova_thumb = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(275, 175))
        self.thumbs_vivas.append(nova_thumb)
        self.thumb_image = nova_thumb
        self.exibir_thumbnail.configure(image=self.thumb_image, text='')
     
    def _mostrar_thumbnail(self) -> None:
        if self.thumb_image is not None:
            self.exibir_thumbnail.grid(row=0, column=0, sticky='nsew')
            self.exibir_thumbnail.lift()

    def _esconder_thumbnail(self) -> None:
        self.exibir_thumbnail.grid_forget()

    def _mostrar_erro(self) -> None:
        self.mensagem_erro.grid(row=0, column=0, sticky='nswe')
        self.mensagem_erro.lift()

    def _esconder_erro(self) -> None:
        self.mensagem_erro.grid_forget()


class InformacaoVideo(ctk.CTkFrame):
    # Mapa com os caminhos dos ícones
    mapa_icones = {
        "youtube": "gui/widgets/youtube.png",
        "calendario": ("gui/widgets/calendario_modo_claro.png", "gui/widgets/calendario_modo_escuro.png"),
        "olho": ("gui/widgets/olho_modo_claro.png", "gui/widgets/olho_modo_escuro.png"),
        "relogio": ("gui/widgets/relogio_modo_claro.png", "gui/widgets/relogio_modo_escuro.png"),
        "tamanho": ("gui/widgets/tamanho_modo_claro.png", "gui/widgets/tamanho_modo_escuro.png")
    }

    def __init__(self, master, video_info):
        super().__init__(master, width=240, height=190, fg_color='transparent')

        # Configura o grid interno
        self.grid_propagate(False)

        # Importa e carrega as imagens
        try:
            youtube_img = ctk.CTkImage(light_image=Image.open(
                self.mapa_icones["youtube"]), dark_image=Image.open(self.mapa_icones["youtube"]), size=(20, 20))
            calendario_img = ctk.CTkImage(light_image=Image.open(
                self.mapa_icones["calendario"][0]), dark_image=Image.open(self.mapa_icones["calendario"][1]), size=(20, 20))
            olho_img = ctk.CTkImage(light_image=Image.open(
                self.mapa_icones["olho"][0]), dark_image=Image.open(self.mapa_icones["olho"][1]), size=(20, 20))
            relogio_img = ctk.CTkImage(light_image=Image.open(
                self.mapa_icones["relogio"][0]), dark_image=Image.open(self.mapa_icones["relogio"][1]), size=(20, 20))
            tamanho_img = ctk.CTkImage(light_image=Image.open(
                self.mapa_icones["tamanho"][0]), dark_image=Image.open(self.mapa_icones["tamanho"][1]), size=(20, 20))
            self.mapa_imagens = {
                "nome": None,
                "canal": youtube_img,
                "data": calendario_img,
                "visualizacao": olho_img,
                "duracao": relogio_img,
                "tamanho": tamanho_img
            }
        except FileNotFoundError:
            self.mapa_imagens = {
                "nome": None,
                "canal": None,
                "data": None,
                "visualizacao": None,
                "duracao": None,
                "tamanho": None
            }

        # Guarda as informações do vídeo
        self.video_info = video_info

        # Guarda os widgets criados
        self.informacoes = []
        self._exibir_informacoes()

    def _formatar_titulo(self, texto, largura_px) -> str:
        f = tkfont.Font(font=('Roboto', 14, 'bold'))
        if f.measure(texto) <= largura_px:
            return texto

        fim = "..."
        largura_fim = f.measure(fim)
        resultado = ""

        for letra in texto:
            if f.measure(resultado + letra) + largura_fim > largura_px:
                break
            resultado += letra

        return resultado + fim

    def _exibir_informacoes(self) -> None:
        for index, key in enumerate(self.video_info.keys()):
            linha = ctk.CTkFrame(self, fg_color='transparent')
            linha.grid(row=index, column=0, padx=5, pady=1, sticky='w')

            if key == 'thumbnail':
                continue

            if key == 'nome':
                texto = self._formatar_titulo(self.video_info[key], 280)
                info = info = ctk.CTkLabel(linha, text=texto, font=(
                    'Roboto', 14, "bold"), justify='left', anchor='w')
           
            else:
                info = ctk.CTkLabel(linha, text=f" : {self.video_info[key]}") if key != 'nome' else ctk.CTkLabel(linha, text=f" {self.video_info[key]}") 
            info.grid(row=0, column=1, padx=(0, 5), sticky='w')

            if self.mapa_imagens[key]:
                img = ctk.CTkLabel(
                    linha, text='', image=self.mapa_imagens[key], fg_color='transparent')
                img.grid(row=0, column=0, padx=(5, 0), sticky='w')

            self.informacoes.append(linha)

    def atualizar_informacoes(self, novo_info: dict) -> None:
        self.video_info = novo_info
        self._limpar_info()
        self._exibir_informacoes()

    def _limpar_info(self) -> None:
        for info in self.informacoes:
            info.destroy()
        self.informacoes.clear()

    def obter_nome(self) -> str:
        return self.video_info.get('nome') or 'Sem nome!'


class SalvarDownload(ctk.CTkFrame):
    def __init__(self, master, info_download: callable[[], dict], escrever: callable):
        super().__init__(master, height=35, width=240, fg_color='transparent')
        # Configura o grid interno
        self.grid_propagate(False)

        # Conexão com o log
        self.logging = Logger()

        self.arquivo = Arquivo()

        # Dados para fazer download
        self.info_download = info_download
        self.escrever = escrever

        # Botão para salvar a o download
        botao = ctk.CTkButton(
            self, text="Adicionar link a fila de download", command=self.salvar, height=20, width=200, corner_radius=6)
        botao.grid(row=0, column=0, padx=10, pady=(5, 10))

    def salvar(self) -> None:
        informacoes = self.info_download()
        if not informacoes:
            return

        dados = [
            informacoes['tipo'],
            informacoes['tipo_playlist'],
            informacoes['qualidade'],
            informacoes['formato'],
            informacoes['url'],
            informacoes['destino'],
        ]
        for item in dados:
            if not item:
                return
            
        self.escrever(dados, "links_salvos.csv")
        Toast(self, mensagem="Novo Downaload adicionado a fila", tipo="sucesso")

        try:
            nome = informacoes["nome"]
            self.arquivo.escrever([nome], 'fila.csv')
            self.logging.exibir(f"{nome} foi adicionado a fila de download")
        except Exception as erro:
            self.logging.exibir(
                f"Não foi possível escrever o título -> {erro}")


class Midia(ctk.CTkFrame):
    def __init__(self, master, info_download: dict, escrever: callable):
        super().__init__(master, width=500, height=225, fg_color="transparent")

        # Configura o grid interno
        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=1)

        self.player = VideoPlayer(self)
        self.player.grid(row=0, column=0)

        frame = ctk.CTkFrame(self)
        frame.grid(row=0, column=1)

        self.informacoes = InformacaoVideo(frame, self._info_vazia())
        self.informacoes.grid(row=0, column=0)

        self.salvar = SalvarDownload(frame, info_download, escrever)
        self.salvar.grid(row=1, column=0)

    def _info_vazia(self) -> dict:
        return {"nome": "—", "canal": "—", "data": "//", "visualizacao": "—", "duracao": "—", "tamanho": "—"}

    def atualizar_informacoes(self, info: dict) -> None:
        if info:
            self.informacoes.atualizar_informacoes(info)
        else:
            self.informacoes.atualizar_informacoes(self._info_vazia())

