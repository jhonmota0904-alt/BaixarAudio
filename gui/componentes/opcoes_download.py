import customtkinter as ctk
from PIL import Image


class Opcoes(ctk.CTkFrame):
    def __init__(self, master, informacoes_url, nova_info):
        super().__init__(master, width=500, height=215, fg_color="transparent")

        self.info_qualidade = informacoes_url['qualidade']
        self.info_formato = informacoes_url['formato']
        self.nova_info = nova_info

        # Configura o grid interno
        self.propagate(False)

        # Guarda as classes
        self.classe_tipo = OpcoesTipo(self)
        self.classe_qualidade = OpcoesQualidade(self)
        self.classe_formato = OpcoesFormato(self)

        # Executa a criação das opções
        self._criar_opcoes()
        self._exibir_botoes()

        # Exibe as opções criadas
        self._mostrar_qualidade_formato_playlist(None, None)

        # Atualiza a interace 
        self.atualizando = False
        self.classe_tipo.tipo_selecionado.trace_add("write", lambda *_: self.atualizar_botoes())
        self.classe_tipo.tipo_playlist.trace_add("write", lambda *_: self.atualizar_botoes())


    def _mostrar_qualidade_formato_playlist(self, tipo: str | None, tipo_playlist: str | None) -> None:
        if not tipo:
            self.classe_qualidade.grid_remove()
            self.classe_formato.grid_remove()
            self.classe_tipo.frame_playlist.grid_remove()

        elif tipo == 'video':
            self.classe_tipo.frame_playlist.grid_remove()
            self.classe_qualidade.grid(row=0, column=1, sticky='nwe')
            self.classe_formato.grid(row=0, column=2, sticky='nwe')
            self.classe_tipo.tipo_playlist.set('')
        elif tipo == 'audio':
            self.classe_tipo.frame_playlist.grid_remove()
            self.classe_qualidade.grid_remove()
            self.classe_formato.grid(row=0, column=2)
            self.classe_tipo.tipo_playlist.set('')
        elif tipo == 'playlist':
            self.classe_tipo.frame_playlist.grid(row=2, column=0, padx=0, pady=0, sticky='nswe')
            if tipo_playlist == None:
                self.classe_qualidade.grid_remove()
                self.classe_formato.grid_remove()
            elif tipo_playlist == 'audio':
                self.classe_qualidade.grid_remove()
                self.classe_formato.grid(row=0, column=2)
            else:
                self.classe_qualidade.grid(row=0, column=1, sticky='nwe')
                self.classe_formato.grid(row=0, column=2, sticky='nwe')

    def atualizar_botoes(self) -> None:
        if self.atualizando:
            return
        self.atualizando = True

        try:
            tipo, tipo_playlist= self.classe_tipo.tipo_download()
            if not tipo:
                self._mostrar_qualidade_formato_playlist(None, None)
                self.classe_qualidade.atualizar_botoes([])
                self.classe_formato.atualizar_botoes([])
                return

            info = self.nova_info() or {}
            qualidade = []
            formato = []

            if tipo == 'video':
                qualidade = info.get('qualidades_video', [])
                formato = info.get('formatos_video', [])
            elif tipo == 'audio':
                formato = info.get('formatos_audio', [])
            elif tipo == 'playlist':
                if tipo_playlist == 'audio':
                    formato = info.get('formatos_audio', [])
                elif tipo_playlist == 'video':
                    qualidade = info.get('qualidades_video', [])
                    formato = info.get('formatos_video', [])

            self._mostrar_qualidade_formato_playlist(tipo, tipo_playlist)
            self.classe_qualidade.atualizar_botoes(qualidade)
            self.classe_formato.atualizar_botoes(formato)
        finally:
            self.atualizando = False

    def _criar_opcoes(self) -> None:
        self.classe_tipo._criar_botoes()
        self.classe_qualidade._criar_botoes(self.info_qualidade)
        self.classe_formato._criar_botoes(self.info_formato)

    def _exibir_botoes(self) -> None:
        self.classe_tipo.grid(row=0, column=0, sticky='nwe')
        self.classe_qualidade.grid(row=0, column=1, sticky='nwe')
        self.classe_formato.grid(row=0, column=2, sticky='nwe')

    def obter_opcoes(self) -> dict:
        tipo, tipo_playlist = self.classe_tipo.tipo_download()
        qualidade = self.classe_qualidade.qualidade_download()
        formato = self.classe_formato.formato_download()
        return {"tipo": tipo, "tipo_playlist": tipo_playlist, "qualidade": qualidade, "formato": formato}


class OpcoesTipo(ctk.CTkFrame):
    mapa_icones = {
        'audio': ("gui/widgets/audio_modo_claro.png", "gui/widgets/audio_modo_escuro.png"),
        'video': ("gui/widgets/video_modo_claro.png", "gui/widgets/video_modo_escuro.png"),
        'playlist': ("gui/widgets/lista_modo_claro.png", "gui/widgets/lista_modo_escuro.png")
    }
    mapa_tipo = {
        'Áudio': 'audio',
        'Vídeo': 'video',
        'PlayList': 'playlist'
    }

    def __init__(self, master):
        super().__init__(master, width=166, height=215)
        self.tipo_selecionado = ctk.StringVar(value='')
        self.tipo_playlist = ctk.StringVar(value='')

        # Configura grid interno do frame
        self.grid_propagate(False)
        self.columnconfigure((0,1), weight=1)
        
        # Título Tipos
        titulo_tipo = ctk.CTkLabel(self, text="Tipo", fg_color="gray30", corner_radius=6)
        titulo_tipo.grid(row=0, column=0, padx=10, pady=5, sticky='we')

        # Frame do tipo de donload
        self.frame_tipo = ctk.CTkFrame(self, width=166, height=115)
        self.frame_tipo.columnconfigure(0, weight=1)
        self.frame_tipo.grid(row=1, column=0, padx=15, pady=0, sticky='nswe')

        # Frame do tipo da playlist
        self.frame_playlist = ctk.CTkFrame(self, width=166, height=100, fg_color='gray17')
        self.frame_playlist.columnconfigure(0, weight=1)
       
        # Título tipo da playlist
        titulo_plst = ctk.CTkLabel(self.frame_playlist, text="Tipo da PlayList", fg_color="gray30", corner_radius=6)
        titulo_plst.grid(row=0, column=0, padx=5, pady=5, sticky='we')


        # Importa e carrega as imagens
        try:
            self.audio_img = ctk.CTkImage(light_image=Image.open(
                self.mapa_icones["audio"][0]), dark_image=Image.open(self.mapa_icones["audio"][1]), size=(15, 15))
            self.video_img = ctk.CTkImage(light_image=Image.open(
                self.mapa_icones["video"][0]), dark_image=Image.open(self.mapa_icones["video"][1]), size=(15, 15))
            self.playlist_img = ctk.CTkImage(light_image=Image.open(
                self.mapa_icones["playlist"][0]), dark_image=Image.open(self.mapa_icones["playlist"][1]), size=(15, 15))
            self.imgs = [self.audio_img, self.video_img, self.playlist_img]
        except FileNotFoundError:
            self.imgs = [None, None, None]

        # Armazena os botões criados
        self.botoes = []

    
    def _criar_botoes(self) -> None:
        self._botoes_tipo_principal()
        self._botoes_tipo_playlist()

    def _botoes_tipo_playlist(self) -> None:
        # Cria as opções do subtipo 'playlist'
        linha = ctk.CTkFrame(self.frame_playlist, fg_color="gray20")
        linha.grid(row=1, column=0, padx=2, pady=2, sticky='we')
        opcoes_playlist = ["Áudio", "Vídeo"]
        for index, tipo_playlist in enumerate(opcoes_playlist):
            botao = ctk.CTkRadioButton(linha, text=tipo_playlist, value=tipo_playlist, variable=self.tipo_playlist, width=83)
            botao.grid(row=0, column=index+1, padx=2, pady=5, sticky='w')
            self.botoes.append(botao)

    def _botoes_tipo_principal(self) -> None:
        # Cria as opções de tipo para baixar a url
        opcoes = ["Áudio", "Vídeo", "PlayList"]
        for index, opcao in enumerate(opcoes):
            linha = ctk.CTkFrame(self.frame_tipo, fg_color="transparent")
            linha.grid(row=index, column=0, padx=(5,0), pady=2, sticky='w')
            botao = ctk.CTkRadioButton(
                linha, text=opcao, value=opcao, variable=self.tipo_selecionado)
            botao.grid(row=0, column=0, sticky='w')

            # Só adiciona o ícone se a imagem foi carregada com sucesso
            if self.imgs[index] is not None:
                img_botao = ctk.CTkLabel(
                    linha, image=self.imgs[index], text="")
                img_botao.grid(row=0, column=1, padx=5)
            self.botoes.append(botao)
    
    def tipo_download(self) -> tuple:
        tipo = self.mapa_tipo.get(self.tipo_selecionado.get()) or None
        playlist = self.mapa_tipo.get(self.tipo_playlist.get()) or None
        return (tipo, playlist)
       

class OpcoesQualidade(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, width=166, height=215)
        self.qualidade_selecionada = ctk.StringVar(value='')

        # Configura o grid interno do frame
        self.grid_propagate(False)

        # Título
        titulo = ctk.CTkLabel(self, text="Qualidade",
                              fg_color="gray30", corner_radius=6)
        titulo.grid(row=0, column=0, padx=10, pady=10, sticky='we')

        # Frame que rola para exibir as opçoes de qualidade
        self.botoes_frame = ctk.CTkScrollableFrame(
            self, fg_color="transparent", width=150)
        self.botoes_frame.grid(row=1, column=0, sticky='w')

        # Armazena os botões cirados
        self.botoes = []

    def _criar_botoes(self, opcoes: list[str]) -> None:
        for index, opcao in enumerate(opcoes):
            linha = ctk.CTkFrame(self.botoes_frame, fg_color="transparent")
            linha.grid(row=index+1, column=0, padx=10, pady=5, sticky='we')
            linha.grid_columnconfigure(0, weight=1)

            botao = ctk.CTkRadioButton(
                linha, text=opcao, value=opcao, variable=self.qualidade_selecionada)
            botao.grid(row=0, column=0, padx=5, pady=5, sticky="w")
            self.botoes.append(botao)

    def qualidade_download(self) -> str | None:
        return self.qualidade_selecionada.get() or None

    def atualizar_botoes(self, opcoes: list[str]) -> None:
        self._destruir_botoes()
        self.qualidade_selecionada.set("")

        if not opcoes:
            return
        self._criar_botoes(opcoes)

    def _destruir_botoes(self) -> None:
        for linha in self.botoes_frame.winfo_children():
            linha.destroy()
        self.botoes.clear()


class OpcoesFormato(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, width=166, height=215)
        self.formato_selecionado = ctk.StringVar(value='')

        # Configuraa o grid interno
        self.grid_propagate(False)

        # Título
        titulo = ctk.CTkLabel(self, text="Formato",
                              fg_color="gray30", corner_radius=6)
        titulo.grid(row=0, column=0, padx=10, pady=10, sticky='we')

        # Frame que rola para exibir as opçoes de qualidade
        self.botoes_frame = ctk.CTkScrollableFrame(
            self, fg_color="transparent", width=150, height=100)
        self.botoes_frame.grid(row=1, column=0, sticky='w')

        # Armazena os botões cirados
        self.botoes = []

    def _criar_botoes(self, opcoes: list[str]) -> None:
        for index, opcao in enumerate(opcoes):
            linha = ctk.CTkFrame(self.botoes_frame, fg_color="transparent")
            linha.grid(row=index+1, column=0, padx=10, pady=5, sticky='we')
            linha.grid_columnconfigure(0, weight=1)

            botao = ctk.CTkRadioButton(
                linha, text=opcao, value=opcao, variable=self.formato_selecionado)
            botao.grid(row=0, column=0, padx=5, pady=5, sticky="w")
            self.botoes.append(botao)

    def formato_download(self) -> str | None:
        return self.formato_selecionado.get() or None

    def atualizar_botoes(self, opcoes: list[str]) -> None:
        self._destruir_botoes()
        self.formato_selecionado.set("")

        if not opcoes:
            return
        self._criar_botoes(opcoes)

    def _destruir_botoes(self) -> None:
        for linha in self.botoes_frame.winfo_children():
            linha.destroy()
        self.botoes.clear()

