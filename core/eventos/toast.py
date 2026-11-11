import customtkinter as ctk


class Toast(ctk.CTkToplevel):
    cores = {
        "info": ("#3B8ED0", "#1F6AA5"),
        "sucesso": ("#2FA572", "#106A43"),
        "aviso": ("#D4A017", "#B8860B"),
        "erro": ("#D32F2F", "#B71C1C"),
    }

    def __init__(self, master, mensagem: str, duracao_ms: int = 3000, tipo: str = 'info'):
        super().__init__(master)

        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.0)

        cor_borda, cor_fundo = self.cores.get(tipo, self.cores["info"])

        # Frame que dá o "cartão" do toast
        frame = ctk.CTkFrame(
            self,
            corner_radius=10,
            border_width=2,
            border_color=cor_borda,
            fg_color=cor_fundo,
        )
        frame.pack(fill="both", expand=True)

        # ✅ Label DENTRO do frame
        ctk.CTkLabel(
            frame,
            text=mensagem,
            text_color="white",
            font=("Roboto", 12),
            wraplength=250,
            justify="left",
            fg_color="transparent",
        ).pack(padx=15, pady=10)

        # Dimensões reais requeridas pelo conteúdo
        self.update_idletasks()
        largura = max(self.winfo_reqwidth(), 200)
        altura = self.winfo_reqheight() - 25

        # Referência segura à janela raiz (não assume que master é o Tk)
        topo = master.winfo_toplevel()

        # ✅ Canto superior direito da janela principal
        x = topo.winfo_rootx() + topo.winfo_width() - largura - 75
        y = topo.winfo_rooty() + 10
        self.geometry(f"{largura}x{altura}+{x}+{y}")

        self._fade_in()
        self.after(duracao_ms, self._fade_out)

    def _fade_in(self) -> None:
        alpha = self.attributes("-alpha")
        if alpha < 1.0:
            self.attributes("-alpha", round(alpha + 0.1, 2))
            self.after(20, self._fade_in)

    def _fade_out(self) -> None:
        alpha = self.attributes("-alpha")
        if alpha > 0.0:
            self.attributes("-alpha", round(alpha - 0.1, 2))
            self.after(20, self._fade_out)
        else:
            self.destroy()