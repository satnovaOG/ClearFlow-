import customtkinter as ctk
import threading
import os
from clearflow.utils import escuchar_y_transcribir 

class ClearFlowApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ClearFlow - Accesibilidad Educativa")
        self.geometry("800x350") # Ventana un poco más alta para el nuevo panel
        self.attributes("-topmost", True) 
        
        ctk.set_appearance_mode("dark") 
        ctk.set_default_color_theme("blue")
        
        self.escuchando = False 
        self.historial_memoria = []  
        self.ventana_bitacora = None 
        
        # --- NUEVAS VARIABLES DE GESTIÓN DE ARCHIVOS ---
        self.directorio_base = "bitacoras"
        os.makedirs(self.directorio_base, exist_ok=True) # Crea la carpeta base si no existe
        self.materia_actual = None
        self.archivo_actual = None

        self.crear_interfaz()

    def obtener_materias(self):
        """Lee las carpetas existentes dentro de /bitacoras"""
        carpetas = [d for d in os.listdir(self.directorio_base) if os.path.isdir(os.path.join(self.directorio_base, d))]
        return carpetas if carpetas else ["Sin materias"]

    def crear_interfaz(self):
        # 1. PANEL SUPERIOR: Gestión de Materias
        self.frame_materias = ctk.CTkFrame(self)
        self.frame_materias.pack(pady=10, padx=20, fill="x")
        
        # Etiqueta y ComboBox para seleccionar
        self.lbl_seleccionar = ctk.CTkLabel(self.frame_materias, text="Seleccionar Materia:")
        self.lbl_seleccionar.pack(side="left", padx=(10, 5), pady=10)
        
        self.combo_materias = ctk.CTkComboBox(self.frame_materias, values=self.obtener_materias())
        self.combo_materias.pack(side="left", padx=5)
        
        self.btn_seleccionar = ctk.CTkButton(self.frame_materias, text="Cargar", width=80, command=self.cargar_materia)
        self.btn_seleccionar.pack(side="left", padx=5)
        
        # Separador visual
        self.lbl_sep = ctk.CTkLabel(self.frame_materias, text="|")
        self.lbl_sep.pack(side="left", padx=5)
        
        # Entry para crear materia nueva
        self.entry_nueva = ctk.CTkEntry(self.frame_materias, placeholder_text="Nombre nueva materia")
        self.entry_nueva.pack(side="left", padx=5)
        
        self.btn_crear = ctk.CTkButton(self.frame_materias, text="Crear", width=80, command=self.crear_materia)
        self.btn_crear.pack(side="left", padx=(5, 10))

        # 2. ÁREA DE SUBTÍTULOS
        self.texto_subtitulos = ctk.CTkLabel(
            self, text="Selecciona o crea una materia para empezar", font=("Arial", 28, "bold"), wraplength=750      
        )
        self.texto_subtitulos.pack(pady=30, padx=20, expand=True)

        # 3. PANEL INFERIOR: Botones de control
        self.frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_botones.pack(side="bottom", pady=10)

        # El botón inicia bloqueado hasta que se seleccione una materia
        self.btn_iniciar = ctk.CTkButton(
            self.frame_botones, text="Iniciar Captura", command=self.iniciar_captura, state="disabled"
        )
        self.btn_iniciar.pack(side="left", padx=10)
        
        self.btn_detener = ctk.CTkButton(
            self.frame_botones, text="Detener", command=self.detener_captura, 
            state="disabled", fg_color="#8B0000", hover_color="#5C0000" 
        )
        self.btn_detener.pack(side="left", padx=10)

        self.btn_bitacora = ctk.CTkButton(
            self.frame_botones, text="Ver Sesión Actual", command=self.abrir_bitacora,
            fg_color="#2B2B2B", hover_color="#404040", state="disabled"
        )
        self.btn_bitacora.pack(side="left", padx=10)

    # --- LÓGICA DE MATERIAS Y ARCHIVOS ---
    def preparar_sesion(self, nombre_materia):
        """Calcula el número de sesión y prepara el archivo"""
        ruta_materia = os.path.join(self.directorio_base, nombre_materia)
        os.makedirs(ruta_materia, exist_ok=True)
        
        # Contamos cuántos archivos "sesion_x.txt" existen para saber cuál sigue
        archivos = [f for f in os.listdir(ruta_materia) if f.startswith("sesion_") and f.endswith(".txt")]
        siguiente_num = len(archivos) + 1
        
        self.materia_actual = nombre_materia
        self.archivo_actual = os.path.join(ruta_materia, f"sesion_{siguiente_num}.txt")
        
        # Desbloqueamos la interfaz
        self.actualizar_subtitulo(f"📌 {nombre_materia} - Sesión {siguiente_num}\nPresiona 'Iniciar Captura' para empezar.")
        self.btn_iniciar.configure(state="normal")
        self.combo_materias.configure(values=self.obtener_materias())
        self.combo_materias.set(nombre_materia)

    def cargar_materia(self):
        materia = self.combo_materias.get()
        if materia and materia != "Sin materias":
            self.preparar_sesion(materia)

    def crear_materia(self):
        nueva_materia = self.entry_nueva.get().strip()
        if nueva_materia:
            self.preparar_sesion(nueva_materia)
            self.entry_nueva.delete(0, 'end') # Limpiar el texto

    # --- LÓGICA EXISTENTE ---
    def actualizar_subtitulo(self, nuevo_texto):
        self.texto_subtitulos.configure(text=nuevo_texto)

    def agregar_a_historial(self, linea):
        self.historial_memoria.append(linea)
        if self.ventana_bitacora is not None and self.ventana_bitacora.winfo_exists():
            self.texto_historial.configure(state="normal")
            self.texto_historial.insert("end", linea + "\n")
            self.texto_historial.see("end")
            self.texto_historial.configure(state="disabled")

    def abrir_bitacora(self):
        if self.ventana_bitacora is None or not self.ventana_bitacora.winfo_exists():
            self.ventana_bitacora = ctk.CTkToplevel(self)
            # Mostramos el nombre del archivo en el título de la ventana
            nombre_archivo = os.path.basename(self.archivo_actual)
            self.ventana_bitacora.title(f"Bitácora en Vivo: {self.materia_actual} - {nombre_archivo}")
            self.ventana_bitacora.geometry("600x400")
            
            self.texto_historial = ctk.CTkTextbox(self.ventana_bitacora, font=("Arial", 16), wrap="word")
            self.texto_historial.pack(padx=20, pady=20, fill="both", expand=True)

            texto_completo = "\n".join(self.historial_memoria) + "\n"
            self.texto_historial.insert("end", texto_completo)
            self.texto_historial.configure(state="disabled") 
        else:
            self.ventana_bitacora.focus() 

    def iniciar_captura(self):
        self.escuchando = True
        self.btn_iniciar.configure(state="disabled")
        self.btn_detener.configure(state="normal")
        self.btn_bitacora.configure(state="normal") # Activamos botón de bitácora
        
        hilo_voz = threading.Thread(target=escuchar_y_transcribir, args=(self,), daemon=True)
        hilo_voz.start()
        
    def detener_captura(self):
        self.escuchando = False
        self.btn_iniciar.configure(state="normal", text="Reanudar")
        self.btn_detener.configure(state="disabled")
        self.actualizar_subtitulo("Captura detenida. Bitácora actualizada en la carpeta.")

def main():
    app = ClearFlowApp()
    app.mainloop()

if __name__ == "__main__":
    main()