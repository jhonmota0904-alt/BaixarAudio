import customtkinter as ctk
from PIL import Image


class Pesquisa(ctk.CTkFrame):
    def __init__(self, master, ao_pesquisar, carregar_video):
        super().__init__(master)

        self.url = ctk.StringVar(value='')
        self.ao_pesquisar = ao_pesquisar
        self.carregar_video = carregar_video

        self.entrada_url = ctk.CTkEntry(
            self, textvariable=self.url, fg_color="gray40", width=635, height=30)
        self.entrada_url.grid(row=0, column=0, padx=(
            5, 0), pady=0, sticky='e')

        lupa_icon = ctk.CTkImage(light_image=Image.open(
            "gui/widgets/lupa.png"), dark_image=Image.open("gui/widgets/lupa.png"), size=(23, 23))
        self.botao_pesquisar = ctk.CTkButton(
            self, image=lupa_icon, text='', command=self._realizar_busca, fg_color="gray40", width=60, height=30)
        self.botao_pesquisar.grid(row=0, column=1, padx=(0, 0), pady=(0, 0))

    def obter_url(self) -> str | None:
        return self.url.get().strip() or None

    def _realizar_busca(self):
        url = self.obter_url()
        self.ao_pesquisar()
        self.carregar_video(url)


class BarraSuperior(ctk.CTkFrame):
    def __init__(self, master, ao_pesquisar, carregar_video):
        super().__init__(master)

        self.columnconfigure((0, 1), weight=1)

        self.pesquisa = Pesquisa(self, ao_pesquisar, carregar_video)
        self.pesquisa.grid(row=0, column=1, pady=(0, 0), sticky='e')

    def obter_url(self) -> str | None:
        return self.pesquisa.obter_url()
