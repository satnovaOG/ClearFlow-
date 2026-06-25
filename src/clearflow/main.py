import customtkinter as ctk
import threading
from clearflow.utils import escuchar_y_transcribir 

class ClearFlowApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ClearFlow - Accesibilidad Educativa")
        self.geometry("800x200")
        self.attributes("-topmost", True) 
        
        ctk.set_appearance_mode("dark") 
        ctk.set_default_color_theme("blue")
        
        self.escuchando = False 
        
        # --- NUEVAS VARIABLES PARA EL MÓDULO DE BITÁCORA ---
        self.historial_memoria = []  # Guarda lo dicho en la sesión actual
        self.ventana_bitacora = None # Controla la ventana secundaria

        self.crear_interfaz()

    def crear_interfaz(self):
        self.texto_subtitulos = ctk.CTkLabel(
            self, text="Esperando al docente...", font=("Arial", 28, "bold"), wraplength=750      
        )
        self.texto_subtitulos.pack(pady=40, padx=20, expand=True)

        self.frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_botones.pack(side="bottom", pady=10)

        self.btn_iniciar = ctk.CTkButton(
            self.frame_botones, text="Iniciar Captura", command=self.iniciar_captura
        )
        self.btn_iniciar.pack(side="left", padx=10)
        
        self.btn_detener = ctk.CTkButton(
            self.frame_botones, text="Detener", command=self.detener_captura, 
            state="disabled", fg_color="#8B0000", hover_color="#5C0000" 
        )
        self.btn_detener.pack(side="left", padx=10)

        # --- NUEVO BOTÓN: Ver Bitácora ---
        self.btn_bitacora = ctk.CTkButton(
            self.frame_botones, text="Ver Bitácora", command=self.abrir_bitacora,
            fg_color="#2B2B2B", hover_color="#404040" # Gris oscuro para no distraer
        )
        self.btn_bitacora.pack(side="left", padx=10)

    def actualizar_subtitulo(self, nuevo_texto):
        self.texto_subtitulos.configure(text=nuevo_texto)

    def agregar_a_historial(self, linea):
        """Guarda la línea y actualiza la ventana de bitácora en vivo si está abierta"""
        self.historial_memoria.append(linea)

        # Si la ventana secundaria existe y está abierta, inyectamos el texto
        if self.ventana_bitacora is not None and self.ventana_bitacora.winfo_exists():
            self.texto_historial.configure(state="normal") # Permitir escritura
            self.texto_historial.insert("end", linea + "\n")
            self.texto_historial.see("end")                # Scroll automático hacia abajo
            self.texto_historial.configure(state="disabled") # Bloquear edición de nuevo

    def abrir_bitacora(self):
        """Abre una ventana secundaria para ver todo el historial de la clase"""
        # Si la ventana no existe o fue cerrada, la creamos
        if self.ventana_bitacora is None or not self.ventana_bitacora.winfo_exists():
            self.ventana_bitacora = ctk.CTkToplevel(self)
            self.ventana_bitacora.title("Historial de Clase - ClearFlow")
            self.ventana_bitacora.geometry("600x400")
            
            # Área de texto con scroll (modo lectura fácil)
            self.texto_historial = ctk.CTkTextbox(
                self.ventana_bitacora, font=("Arial", 16), wrap="word"
            )
            self.texto_historial.pack(padx=20, pady=20, fill="both", expand=True)

            # Cargar el historial previo que ya esté en la memoria
            texto_completo = "\n".join(self.historial_memoria) + "\n"
            self.texto_historial.insert("end", texto_completo)
            self.texto_historial.configure(state="disabled") # Modo lectura estricto
        else:
            # Si ya está abierta, la traemos al frente
            self.ventana_bitacora.focus() 

    def iniciar_captura(self):
        self.escuchando = True
        self.btn_iniciar.configure(state="disabled")
        self.btn_detener.configure(state="normal")
        hilo_voz = threading.Thread(target=escuchar_y_transcribir, args=(self,), daemon=True)
        hilo_voz.start()
        
    def detener_captura(self):
        self.escuchando = False
        self.btn_iniciar.configure(state="normal", text="Reanudar")
        self.btn_detener.configure(state="disabled")
        self.actualizar_subtitulo("Captura detenida. Bitácora actualizada.")

def main():
    app = ClearFlowApp()
    app.mainloop()

if __name__ == "__main__":
    main()