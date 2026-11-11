import customtkinter as ctk
from tkinter import filedialog
from PIL import Image
from core.download.arquivo import Arquivo
from core.logs.log import Logger
from core.eventos.observavel import Observavel

class Armazenamento(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, height=120, width=200)
        self.destino_selecionado = ctk.StringVar(value="")

        # Configura o grid interno
        self.grid_propagate(False)
        
        # Cria o frame para exibir o destino
        frame_destino = ctk.CTkFrame(self, height=90, width=200)
        frame_destino.grid(row=0, column=0, sticky='we')
        frame_destino.grid_propagate(False)
        frame_destino.grid_columnconfigure(0, weight=0)
        frame_destino.grid_columnconfigure(1, weight=1)

       # Importa imagem para o programa
        pasta_icon = ctk.CTkImage(light_image=Image.open("gui/widgets/pasta_modo_claro.png"), dark_image=Image.open("gui/widgets/pasta_modo_escuro.png"), size=(15, 15))

        # Exibe a imgem junto do local escolhido
        imagem = ctk.CTkLabel(frame_destino, image=pasta_icon, text="", bg_color="transparent", width=15)
        imagem.grid(row=0, column=0, padx=5, sticky='e')

        self.exibir_destino = ctk.CTkLabel(frame_destino, text=self._exibir_local_destino(), bg_color="transparent", wraplength=150, justify='left', anchor='w')
        self.exibir_destino.grid(row=0, column=1, padx=(0,5), sticky='s')

        # Cria o botão para selecionar o destino
        botao = ctk.CTkButton(self, text="Escolher Destino", command=self._selecionar_pasta, width=200, height=30)
        botao.grid(row=1, column=0, sticky="swe")

    def _exibir_local_destino(self) -> str:
        if not self.destino_selecionado.get():
            return 'Selecionar Destino'
        return self.destino_selecionado.get() 
    
    def obter_local_destino(self) -> str | None:
        return self.destino_selecionado.get() or None
    
    def _atualizar_legenda_destino(self) -> None:
        self.exibir_destino.configure(text=self._exibir_local_destino())

    def _selecionar_pasta(self) -> None:
        pasta =  filedialog.askdirectory(
            title = "Seletor de pastas",
            mustexist = True)

        self.destino_selecionado.set(str(pasta))
        self._atualizar_legenda_destino()
        

class HistoricoFila(ctk.CTkFrame):
    def __init__(self, master, ao_clicar):
        super().__init__(master, height=30, width=200)
        self.estado = ctk.StringVar(value='fila')
        self.ao_clicar = ao_clicar

        # Configura o grid interno
        self.grid_propagate(False)

        # Cria o botão que troca o estado de exibição
        self.botao = ctk.CTkButton(self, text=self._legenda_botao(), command=self._clicar, height=30, width=200)
        self.botao.grid(row=0, column=0, sticky='we')

    def _atualizar_legenda(self) -> None:
        self.botao.configure(text=self._legenda_botao())

    def _legenda_botao(self) -> str:
        if self.obter_estado() == 'fila':
            return "Exibir Histórico"
        return "Exibir Fila de Download"

    def obter_estado(self) -> str:
        return self.estado.get()

    def _trocar_estado(self) -> None:
        if self.obter_estado() == 'fila':
            self.estado.set(value='historico')
        else:
            self.estado.set(value='fila')

        self._atualizar_legenda()

    def _clicar(self) -> None:
        self._atualizar_legenda()
        self._trocar_estado()
        self.ao_clicar(self.obter_estado())


class ExibirHistoricoFila(ctk.CTkFrame):
    def __init__(self, master, estado):
        super().__init__(master, height=300, width=200)

        # Configura o grid interno
        self.grid_propagate(False)

        self.estado = estado
        self.arquivo = Arquivo()
        self.logging = Logger()
        
        # Título
        self.title = ctk.CTkLabel(self, text=self._legenda())
        self.title.grid(row=0, column=0, sticky='we')

        # Frame que vai exibir o histórico de download e a fila de download
        self.frame_titulos = ctk.CTkScrollableFrame(self, width=170)
        self.frame_titulos.grid(row=1, column=0, padx=5, pady=5, sticky='se')

        self.guardar_itens = []
   
    def _legenda(self) -> str:
        return "Fila de Download" if self.estado == 'fila' else "Histórico"

    def _atualizar_legenda(self) -> None:
        self.title.configure(text=self._legenda())

    def _exibir_titulos(self, lista_titulos: list[dict]) -> None:
        lista_titulos = lista_titulos[::-1]
        for index, item in enumerate(lista_titulos):
            texto = f"{index+1} - {item['nome']}"
            linha = ctk.CTkLabel(self.frame_titulos, text=texto, fg_color='transparent', wraplength=170, justify='left', anchor='w')
            linha.grid(row=index+1, column=0, padx=5, pady=5, sticky='w')
            self.guardar_itens.append(linha)

    def _obter_historico_fila(self, caminho: str) -> list[dict]:
        dados = self.arquivo.ler_historico_fila(caminho)
        return dados if dados else [{"nome": "- - -"}]

    def _limpar(self) -> None:
        for item in self.guardar_itens:
            item.destroy()
        self.guardar_itens.clear()

    def exibir(self, tipo: str) -> None:
        if tipo == 'historico':
            dados = self._obter_historico_fila('historico.csv')
        elif tipo == 'fila':
            dados = self._obter_historico_fila('fila.csv')
        else:
            self.logging.exibir(f"Tipo de exibição inválido: {tipo}")
            self.logging.erro(f"Tipo de exibição inválido: {tipo}")
            return
       
        self._limpar()
        self.estado = tipo
        self._atualizar_legenda()
        self._exibir_titulos(dados)

    def atualizar(self, evento: dict) -> None:
        self.after(0, lambda: self._aplicar(evento))

    def _aplicar(self, evento: dict) -> None:
        if evento.get("tipo") in ("iniciado", "concluido", "erro", "todos_concluidos"):
            self.exibir(self.estado)
        
class Agrupar(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, height=450, width=200)

        # Configura o grid inter
        self.grid_propagate(False)

        self.destino = Armazenamento(self)
        self.destino.grid(row=0, column=0, pady=5)

        self.historicoFila = HistoricoFila(self, self.atualizar)
        self.historicoFila.grid(row=1, column=0, pady=5)

        self.exibir_historicoFila = ExibirHistoricoFila(self, self.estado())
        self.exibir_historicoFila.grid(row=2, column=0)

    def obter_destino(self) -> str | None:
        return self.destino.obter_local_destino() or None

    def estado(self) -> str:
        return self.historicoFila.obter_estado()

    def atualizar(self, tipo: str) -> None:
        self.exibir_historicoFila.exibir(tipo)

    def obter_observador(self) -> object:
        return self.exibir_historicoFila
