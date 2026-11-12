from collections.abc import Callable, Mapping, Sequence
from pathlib import Path

import customtkinter as ctk
from PIL import Image


class Opcoes(ctk.CTkFrame):
    def __init__(
        self,
        master: object,
        informacoes_url: Mapping[str, object],
        nova_info: Callable[[], Mapping[str, object] | None],
    ) -> None:
        super().__init__(master, width=500, height=215, fg_color="transparent")

        self.info_qualidade = self._obter_lista_opcoes(informacoes_url, "qualidade")
        self.info_formato = self._obter_lista_opcoes(informacoes_url, "formato")
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

    @staticmethod
    def _obter_lista_opcoes(
        informacoes: Mapping[str, object], chave: str
    ) -> list[str]:
        opcoes = informacoes.get(chave, ())
        if (
            not isinstance(opcoes, Sequence)
            or isinstance(opcoes, (str, bytes))
            or not all(isinstance(opcao, str) for opcao in opcoes)
        ):
            raise TypeError(f"As opções de '{chave}' devem ser uma sequência de textos.")
        return list(dict.fromkeys(opcoes))

    def _mostrar_qualidade_formato_playlist(self, tipo: str | None, tipo_playlist: str | None) -> None:
        if not tipo:
            self.classe_qualidade.grid_remove()
            self.classe_formato.grid_remove()
            self.classe_tipo.frame_playlist.grid_remove()
        elif tipo == 'video':
            self.classe_tipo.frame_playlist.grid_remove()
            self.classe_qualidade.grid(row=0, column=1, sticky='nwe')
            self.classe_formato.grid(row=0, column=2, sticky='nwe')
        elif tipo == 'audio':
            self.classe_tipo.frame_playlist.grid_remove()
            self.classe_qualidade.grid_remove()
            self.classe_formato.grid(row=0, column=2)
        elif tipo == 'playlist':
            self.classe_tipo.frame_playlist.grid(row=2, column=0, padx=0, pady=0, sticky='nswe')
            if tipo_playlist is None:
                self.classe_qualidade.grid_remove()
                self.classe_formato.grid_remove()
            elif tipo_playlist == 'audio':
                self.classe_qualidade.grid_remove()
                self.classe_formato.grid(row=0, column=2)
            elif tipo_playlist == 'video':
                self.classe_qualidade.grid(row=0, column=1, sticky='nwe')
                self.classe_formato.grid(row=0, column=2, sticky='nwe')

    def atualizar_botoes(self) -> None:
        if self.atualizando:
            return
        self.atualizando = True

        try:
            tipo, tipo_playlist = self.classe_tipo.tipo_download()
            if tipo != 'playlist' and self.classe_tipo.tipo_playlist.get():
                self.classe_tipo.tipo_playlist.set('')

            if not tipo:
                self._mostrar_qualidade_formato_playlist(None, None)
                self.classe_qualidade.atualizar_botoes([])
                self.classe_formato.atualizar_botoes([])
                return

            info = self.nova_info()
            if info is None:
                info = {}
            elif not isinstance(info, Mapping):
                raise TypeError("nova_info deve retornar um mapeamento ou None.")

            qualidade = []
            formato = []

            if tipo == 'video':
                qualidade = self._obter_lista_opcoes(info, 'qualidades_video')
                formato = self._obter_lista_opcoes(info, 'formatos_video')
            elif tipo == 'audio':
                formato = self._obter_lista_opcoes(info, 'formatos_audio')
            elif tipo == 'playlist':
                if tipo_playlist == 'audio':
                    formato = self._obter_lista_opcoes(info, 'formatos_audio')
                elif tipo_playlist == 'video':
                    qualidade = self._obter_lista_opcoes(info, 'qualidades_video')
                    formato = self._obter_lista_opcoes(info, 'formatos_video')

            self._mostrar_qualidade_formato_playlist(tipo, tipo_playlist)
            self.classe_qualidade.atualizar_botoes(qualidade)
            self.classe_formato.atualizar_botoes(formato)
        finally:
            self.atualizando = False

    def _criar_opcoes(self) -> None:
        self.classe_tipo._criar_botoes()
        self.classe_qualidade.atualizar_botoes(self.info_qualidade)
        self.classe_formato.atualizar_botoes(self.info_formato)

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
        'audio': ("audio_modo_claro.png", "audio_modo_escuro.png"),
        'video': ("video_modo_claro.png", "video_modo_escuro.png"),
        'playlist': ("lista_modo_claro.png", "lista_modo_escuro.png")
    }
    opcoes_tipo = (("Áudio", "audio"), ("Vídeo", "video"), ("PlayList", "playlist"))

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

        self.diretorio_icones = Path(__file__).resolve().parent.parent / "widgets"
        self.imgs = {tipo: self._carregar_icone(tipo) for tipo in self.mapa_icones}

        # Armazena os botões criados
        self.botoes = []

    def _carregar_icone(self, tipo: str) -> ctk.CTkImage | None:
        caminhos = self.mapa_icones[tipo]
        imagens = []
        for nome_arquivo in caminhos:
            caminho = self.diretorio_icones / nome_arquivo
            try:
                with Image.open(caminho) as imagem:
                    imagens.append(imagem.copy())
            except FileNotFoundError:
                return None

        return ctk.CTkImage(
            light_image=imagens[0],
            dark_image=imagens[1],
            size=(15, 15),
        )

    def _criar_botoes(self) -> None:
        self._botoes_tipo_principal()
        self._botoes_tipo_playlist()

    def _botoes_tipo_playlist(self) -> None:
        # Cria as opções do subtipo 'playlist'
        linha = ctk.CTkFrame(self.frame_playlist, fg_color="gray20")
        linha.grid(row=1, column=0, padx=2, pady=2, sticky='we')
        opcoes_playlist = (("Áudio", "audio"), ("Vídeo", "video"))
        for index, (rotulo, tipo_playlist) in enumerate(opcoes_playlist):
            botao = ctk.CTkRadioButton(linha, text=rotulo, value=tipo_playlist, variable=self.tipo_playlist, width=83)
            botao.grid(row=0, column=index+1, padx=2, pady=5, sticky='w')
            self.botoes.append(botao)

    def _botoes_tipo_principal(self) -> None:
        # Cria as opções de tipo para baixar a url
        for index, (rotulo, tipo) in enumerate(self.opcoes_tipo):
            linha = ctk.CTkFrame(self.frame_tipo, fg_color="transparent")
            linha.grid(row=index, column=0, padx=(5,0), pady=2, sticky='w')
            botao = ctk.CTkRadioButton(
                linha, text=rotulo, value=tipo, variable=self.tipo_selecionado)
            botao.grid(row=0, column=0, sticky='w')

            # Só adiciona o ícone se a imagem foi carregada com sucesso
            imagem = self.imgs[tipo]
            if imagem is not None:
                img_botao = ctk.CTkLabel(
                    linha, image=imagem, text="")
                img_botao.grid(row=0, column=1, padx=5)
            self.botoes.append(botao)
    
    def tipo_download(self) -> tuple[str | None, str | None]:
        tipo = self.tipo_selecionado.get() or None
        playlist = self.tipo_playlist.get() or None
        return tipo, playlist
       

class _OpcoesSelecao(ctk.CTkFrame):
    def __init__(self, master: object, titulo: str, altura: int | None = None) -> None:
        super().__init__(master, width=166, height=215)
        self.opcao_selecionada = ctk.StringVar(value='')
        self._opcoes: tuple[str, ...] = ()

        # Configura o grid interno do frame
        self.grid_propagate(False)

        titulo_widget = ctk.CTkLabel(self, text=titulo, fg_color="gray30", corner_radius=6)
        titulo_widget.grid(row=0, column=0, padx=10, pady=10, sticky='we')

        # Frame rolável que exibe as opções
        if altura is None:
            self.botoes_frame = ctk.CTkScrollableFrame(
                self, fg_color="transparent", width=150)
        else:
            self.botoes_frame = ctk.CTkScrollableFrame(
                self, fg_color="transparent", width=150, height=altura)
        self.botoes_frame.grid(row=1, column=0, sticky='w')

        self.botoes = []

    def _criar_botoes(self, opcoes: Sequence[str]) -> None:
        for index, opcao in enumerate(opcoes):
            linha = ctk.CTkFrame(self.botoes_frame, fg_color="transparent")
            linha.grid(row=index, column=0, padx=10, pady=5, sticky='we')
            linha.grid_columnconfigure(0, weight=1)

            botao = ctk.CTkRadioButton(
                linha, text=opcao, value=opcao, variable=self.opcao_selecionada)
            botao.grid(row=0, column=0, padx=5, pady=5, sticky="w")
            self.botoes.append(botao)

    def atualizar_botoes(self, opcoes: list[str]) -> None:
        novas_opcoes = tuple(dict.fromkeys(opcoes))
        if novas_opcoes == self._opcoes:
            return

        self._destruir_botoes()
        self._opcoes = novas_opcoes
        self.opcao_selecionada.set("")

        if self._opcoes:
            self._criar_botoes(self._opcoes)

    def _destruir_botoes(self) -> None:
        for linha in self.botoes_frame.winfo_children():
            linha.destroy()
        self.botoes.clear()


class OpcoesQualidade(_OpcoesSelecao):
    def __init__(self, master):
        super().__init__(master, "Qualidade")
        self.qualidade_selecionada = self.opcao_selecionada

    def qualidade_download(self) -> str | None:
        return self.qualidade_selecionada.get() or None


class OpcoesFormato(_OpcoesSelecao):
    def __init__(self, master):
        super().__init__(master, "Formato", altura=100)
        self.formato_selecionado = self.opcao_selecionada

    def formato_download(self) -> str | None:
        return self.formato_selecionado.get() or None

