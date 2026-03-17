import customtkinter as ctk
import threading
from clearflow.utils import escuchar_y_transcribir 

class ClearFlowApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ClearFlow - Accesibilidad Educativa")
        self.geometry("800x200")
        self.attributes("-topmost", True) # Mantiene la ventana siempre visible [cite: 72]
        
        ctk.set_appearance_mode("dark") 
        ctk.set_default_color_theme("blue")
        
        self.escuchando = False # Variable para controlar el micrófono

        self.crear_interfaz()

    def crear_interfaz(self):
        self.texto_subtitulos = ctk.CTkLabel(
            self, 
            text="Esperando al docente...", 
            font=("Arial", 28, "bold"), 
            wraplength=750      
        )
        self.texto_subtitulos.pack(pady=40, padx=20, expand=True)

        self.frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_botones.pack(side="bottom", pady=10)

        # Botón Iniciar
        self.btn_iniciar = ctk.CTkButton(
            self.frame_botones, text="Iniciar Captura", command=self.iniciar_captura
        )
        self.btn_iniciar.pack(side="left", padx=10)
        
        # Botón Detener
        self.btn_detener = ctk.CTkButton(
            self.frame_botones, text="Detener", command=self.detener_captura, 
            state="disabled", fg_color="#8B0000", hover_color="#5C0000" # Rojo oscuro
        )
        self.btn_detener.pack(side="left", padx=10)

    def actualizar_subtitulo(self, nuevo_texto):
        """Actualiza el texto en la interfaz gráfica"""
        self.texto_subtitulos.configure(text=nuevo_texto)

    def iniciar_captura(self):
        """Arranca el micrófono en un hilo paralelo"""
        self.escuchando = True
        self.btn_iniciar.configure(state="disabled")
        self.btn_detener.configure(state="normal")
        
        # daemon=True asegura que si cierras la ventana, el micrófono se apague también
        hilo_voz = threading.Thread(target=escuchar_y_transcribir, args=(self,), daemon=True)
        hilo_voz.start()
        
    def detener_captura(self):
        """Pausa la captura de audio"""
        self.escuchando = False
        self.btn_iniciar.configure(state="normal", text="Reanudar")
        self.btn_detener.configure(state="disabled")
        self.actualizar_subtitulo("Captura detenida. Bitácora actualizada.")

def main():
    app = ClearFlowApp()
    app.mainloop()

if __name__ == "__main__":
    main()