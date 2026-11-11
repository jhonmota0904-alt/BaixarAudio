import customtkinter as ctk
from core.eventos.toast import Toast

class BotaoDownload(ctk.CTkFrame):
    def __init__(self, master, ao_clicar):
        super().__init__(master, height=30, width=700, fg_color='transparent')

        # Configura o grid interno
        self.grid_propagate(False)

        self.ao_clicar = ao_clicar
       
        # Cria o botão
        self.botao = ctk.CTkButton(self, text=f"Iniciar Download", command=self._clicar, height=30, width=690)
        self.botao.grid(row=0, column=0, padx=(5, 5), sticky='we')

    def _clicar(self) -> None:
        self.ao_clicar()

    def atualizar(self, evento: dict) -> None:
            self.after(0, lambda: self._aplicar(evento))
            
    def _aplicar(self, evento: dict) -> None:
        tipo = evento.get("tipo")

        if tipo in ("iniciado", "progresso"):
            self.botao.configure(state="disabled", text="Baixando...")
        elif tipo == "concluido":
            self.botao.configure(state="normal", text="Iniciar Download")
        elif tipo == "erro":
            Toast(self, mensagem="Não foi possível concluir o download", tipo="erro")
            self.botao.configure(state="normal", text="Iniciar Download")
        elif tipo == "todos_concluidos":
            Toast(self, mensagem="Todos os downloads foram concluidos!", tipo="sucesso")


class BarraProgresso(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, height=30, width=700, fg_color='transparent')

        # Configura o grid da barra e deixa ela zerada
        self.barra = ctk.CTkProgressBar(self, height=15, width=680, mode='determinate')
        self.barra.grid(row=0, column=0, padx=5, pady=(7.5, 0), sticky='we')
        self.barra.set(0)

        self.legenda_status = ctk.CTkLabel(self, text='Aguardado...', height=14)
        self.legenda_status.grid(row=1, column=0, padx=5, pady=(0, 2))

    def atualizar(self, evento: dict) -> None:
        self.after(0, lambda: self._aplicar(evento))

    def _aplicar(self, evento: dict) -> None:
        tipo = evento.get("tipo")

        if tipo == "iniciado":
            self.barra.set(0)
            self.legenda_status.configure(text=f"Iniciando: {evento.get('titulo', '')[:60]}")

        elif tipo == "progresso":
            self.barra.set(evento.get("percentual", 0) / 100)
            self.legenda_status.configure(
                text=f"{evento['percentual']:.1f}%".strip()
            )

        elif tipo == "concluido":
            self.barra.set(1)
            self.legenda_status.configure(text="Concluído!")


        elif tipo == "erro":
            self.legenda_status.configure(text=f"Erro: {evento.get('mensagem', '')[:80]}")

    def resetar(self) -> None:
        self.barra.set(0)
        self.legenda_status.configure(text="Aguardando...")
        
    
class BarraInferior(ctk.CTkFrame):
    def __init__(self, master, ao_clicar):
        super().__init__(master, height=70, width=700)

        # Configura o grid interno
        self.grid_propagate(False)

        self.barra_progresso = BarraProgresso(self)
        self.barra_progresso.grid(row=1, column=0, padx=0, pady=0)

        self.botao_download = BotaoDownload(self, ao_clicar)
        self.botao_download.grid(row=0, column=0, padx=0, pady=0)

    def obter_observador(self) -> tuple:
        return (self.barra_progresso, self.botao_download)
