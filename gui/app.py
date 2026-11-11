import customtkinter as ctk
from sys import exit
from core.download.servico import ServicoDownload
from core.download.arquivo import Arquivo
from CTkMessagebox import CTkMessagebox
from core.download.extracao import ExtratorInformacoes
from core.eventos.toast import Toast
from core.logs.log import Logger
from gui.componentes import (
    barra_menu, opcoes_download, visualizacao_midia,
    fila_historico, download_progresso, confirmar_saida
)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.largura = 700
        self.altura = 540
        # Configurações da janela mãe
        self.title("Download de Mídia")
        self.geometry(f"{str(self.largura)}x{str(self.altura)}")
        self.resizable(width=False, height=False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.iconbitmap("gui/widgets/download_icon.ico")

        # Serviços, observadores e extrator
        self.extrator = ExtratorInformacoes()
        self.arquivo = Arquivo()
        self.servico = ServicoDownload()
        self.logging = Logger()

        # Informações iniciais
        self._info_atual = None

        # criando e configurando frames
        frame_superior = ctk.CTkFrame(self, height=30)
        frame_superior.grid(row=0, column=0, padx=0, pady=0, sticky='nwe')

        frame_central = ctk.CTkFrame(self, height=472)
        frame_central.grid(row=1, column=0, padx=0, pady=0, sticky='nswe')

        frame_inferior = ctk.CTkFrame(self, height=60)
        frame_inferior.grid(row=2, column=0, padx=0, pady=0, sticky='swe')

        # Divisão do frame_central em esquerda e direita
        frm_central_esquerda = ctk.CTkFrame(
            frame_central, height=450, width=500)
        frm_central_esquerda.grid(row=0, column=0)

        frm_central_direita = ctk.CTkFrame(
            frame_central, height=450, width=200)
        frm_central_direita.grid(row=0, column=1)

        # (1) Barra superior
        self.barra_superior = barra_menu.BarraSuperior(
            frame_superior, self.pesquisar_url, self.rodar_video)
        self.barra_superior.grid(row=0, column=0, padx=(
            0, 5), pady=(0, 5), sticky='we')

        # (2) Opções
        self.opcoes = opcoes_download.Opcoes(
            frm_central_esquerda, {"qualidade": [], "formato": []}, self._obter_info_atual)
        self.opcoes.grid(row=1, column=0)

        # (3) Destinos, Fila e Histórico
        self.exibir_fila_historico = fila_historico.Agrupar(
            frm_central_direita)
        self.exibir_fila_historico.grid(row=0, column=0, padx=(0,5), sticky='ns')

        # (4) Baarra Inferior
        self.barra_inferior = download_progresso.BarraInferior(
            frame_inferior, ao_clicar=self.iniciar_download)
        self.barra_inferior.grid(row=2, column=0)

        # (5) Visualizar de mídia
        self.midia = visualizacao_midia.Midia(
            frm_central_esquerda, self.agrupar_informacao_download, self.arquivo.escrever)
        self.midia.grid(row=0, column=0)

        # Observados
        barra, botao = self.barra_inferior.obter_observador()
        self.servico.anexar(barra)
        self.servico.anexar(botao)
        self.servico.anexar(self.exibir_fila_historico.obter_observador())
        self.servico.anexar(self)

        # Fechar programa
        self._trabalhando = False
        self.protocol("WM_DELETE_WINDOW", self._fechar)


    def _obter_info_atual(self) -> dict:
        return self._info_atual or {}

    def iniciar_download(self) -> None:
        para_baixar = []
        downloads = self.arquivo.ler("links_salvos.csv")
        if not downloads:
            Toast(self, "Nenhum item na lista de downoad.", tipo='aviso')
            return

        for linha in downloads:
            vazio = [chave for chave, valor in linha.items() if not valor]
            if vazio:
                continue
            para_baixar.append(linha)

        if para_baixar:
            Toast(self, mensagem="Iniciando o Download", duracao_ms=5000, tipo="info")
        self.servico.baixar(para_baixar)
        self.arquivo.limpar("links_salvos.csv")
        self.arquivo.limpar("fila.csv")

    def _verificar(self, info: dict) -> bool:
        vazio = [chave for chave, valor in info.items() if not valor]
        if vazio:
            CTkMessagebox(
                title="Faltando informaçao",
                message=f"Preencha: {', '.join(vazio)}",
                icon="warning",
                option_1='OK'
            )
            self.logging.exibir(
                f"Campos faltando para salvar informações: [{', '.join(vazio)}]")
            self.logging.aviso(
                f"Campos faltando para salvar informações: [{', '.join(vazio)}]")
            return False
        return True

    def agrupar_informacao_download(self) -> dict | None:
        atualizar_layout = self.opcoes.obter_opcoes()
        url = self.barra_superior.obter_url()
        destino = self.exibir_fila_historico.obter_destino()
        nome = self.midia.informacoes.obter_nome()

        dados = {
            "tipo": None,
            "tipo_playlist": None,
            "qualidade": None,
            "formato": None,
            "url": None,
            "destino": None,
            "nome": None
        }

        try:
            if atualizar_layout:
                dados["tipo"] = atualizar_layout["tipo"]
                dados["tipo_playlist"] = atualizar_layout["tipo_playlist"]
                dados["formato"] = atualizar_layout["formato"]

                tipo = dados["tipo"]
                tipo_playlist = dados["tipo_playlist"]


                if tipo == 'playlist':
                    if tipo_playlist == 'audio':
                        dados['qualidade'] = '_'
                    else:
                        dados["qualidade"] = atualizar_layout["qualidade"]
                else:
                    dados["tipo_playlist"] = '_'
                    if dados['tipo'] == 'audio':
                        dados['qualidade'] = '_'
                    else:
                        dados["qualidade"] = atualizar_layout["qualidade"]

            if url:
                dados["url"] = url

            if destino:
                dados["destino"] = destino

            if nome:
                dados["nome"] = nome

        except Exception as erro:
            self.logging.exibir(erro)
            self.logging.erro(erro)

        if not self._verificar(dados):
            return
        return dados

    def pesquisar_url(self) -> dict:
        self._info_atual = None
        url = self.barra_superior.obter_url()
        if not url:
            return

        info = self.extrator.extrair(url)
        if not info:
            #CTkMessagebox(
                #title="Erro", message="Não foi possível obter informações do link.", icon="cancel", option_1="OK")
            Toast(self, mensagem="Nõ foi possível extrair as informações!", duracao_ms=4000, tipo="erro")
            return

        self._info_atual = info
        self._info_atual["url"] = url
        self._info_atual["formatos_audio"] = ["mp3", "m4a"]

        self.midia.atualizar_informacoes({
            "nome": info["nome"],
            "canal": info["canal"],
            "data": info["data"],
            "visualizacao": info["visualizacao"],
            "duracao": info["duracao"],
            "tamanho": info["tamanho"],
            "thumbnail": info["thumbnail"]
        })

        self.opcoes.atualizar_botoes()

    def rodar_video(self, url: str) -> None:
        if not url:
            Toast(self, mensagem="Forneça uma URL", tipo="aviso", duracao_ms=3000)
            return
        thumbnail = (self._info_atual or {}).get("thumbnail")
        self.midia.player.carregar_video(url, thumbnail)

    def alterar_status(self, status: str) -> None:
        if status == 'trabalhando':
            self._trabalhando = True
        else:
            self._trabalhando = False

    def _fechar(self) -> None:
        resposta = confirmar_saida.confirmar(
            self, "Ainda estamos trabalhando. \nQuer mesmo fechar o programa?",
            self._trabalhando)
        if resposta:
            print("Saindo") # <- Remover depois
            # Lógica para parar o download e apagar arquivos desnecessários entra aqui
            # ..........
            # ..........
            
            self.quit()
            exit()

    def _verificar_se_trabalha(self, evento: dict) -> None:
        if evento.get("tipo") == "todos_concluidos":
            self._trabalhando = False

        elif evento.get("tipo") in ("iniciado", "progresso", "concluido", "erro") and not self._trabalhando:
            self._trabalhando = True

        print(f"self._trebalhndo = {self._trabalhando}")

    def atualizar(self, evento: dict) -> None:
        self.after(0, lambda: self._verificar_se_trabalha(evento))