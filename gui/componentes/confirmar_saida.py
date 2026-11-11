import customtkinter as ctk


class Confirmar(ctk.CTkToplevel):
    def __init__(self, master, mensagem, titulo="Confirmação"):
        super().__init__(master)
        self.result = False

        self.title(titulo)
        self.geometry("420x200")
        self.resizable(False, False)

        self.transient(master)
        self.grab_set()

        self.update_idletasks()
        largura, altura = 420, 200
        x = master.winfo_x() + (master.winfo_width() // 2) - (largura // 2)
        y = master.winfo_y() + (master.winfo_height() // 2) - (altura // 2)
        self.geometry(f"{largura}x{altura}+{x}+{y}")

        label = ctk.CTkLabel(
            self,
            text=mensagem,
            font=ctk.CTkFont(size=15),
            wraplength=380,
            justify="center",
        )
        label.pack(pady=(35, 25), padx=20, expand=True)

        frame_botoes = ctk.CTkFrame(self, fg_color="transparent")
        frame_botoes.pack(pady=(0, 20))

        btn_sim = ctk.CTkButton(
            frame_botoes,
            text="Sim, fechar",
            width=150,
            fg_color="#c0392b",
            hover_color="#a93226",
            command=self._confirmar,
        )
        btn_sim.pack(side="left", padx=10)

        btn_nao = ctk.CTkButton(
            frame_botoes,
            text="Não, continuar",
            width=150,
            command=self._cancelar,
        )
        btn_nao.pack(side="left", padx=10)

        self.protocol("WM_DELETE_WINDOW", self._cancelar)

        self.bind("<Return>", lambda e: self._confirmar())
        self.bind("<Escape>", lambda e: self._cancelar())

 
        btn_nao.focus_set()

    def _confirmar(self):
        self.result = True
        self.destroy()

    def _cancelar(self):
        self.result = False
        self.destroy()


def confirmar(master, mensagem, trabalhando, titulo="Confirmação") -> bool:
    if trabalhando:
        dialog = Confirmar(master, mensagem, titulo)
        master.wait_window(dialog)   
        return dialog.result
    return True