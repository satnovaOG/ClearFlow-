import customtkinter as ctk
import threading
import os
from clearflow.utils import escuchar_y_transcribir 

class ClearFlowApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ClearFlow - Accesibilidad Educativa")
        self.geometry("850x350") 
        self.attributes("-topmost", True) 
        
        ctk.set_appearance_mode("dark") 
        ctk.set_default_color_theme("blue")
        
        self.escuchando = False 
        self.historial_memoria = []  
        self.ventana_bitacora = None 
        
        self.directorio_base = "bitacoras"
        os.makedirs(self.directorio_base, exist_ok=True) 
        self.materia_actual = None
        self.archivo_actual = None

        self.crear_interfaz()

    def obtener_materias(self):
        """Lee las carpetas existentes dentro de /bitacoras"""
        carpetas = [d for d in os.listdir(self.directorio_base) if os.path.isdir(os.path.join(self.directorio_base, d))]
        return carpetas if carpetas else ["Sin materias"]

    def obtener_archivos_materia(self):
        """Obtiene la lista ordenada de sesiones (.txt) de la materia actual"""
        ruta_materia = os.path.join(self.directorio_base, self.materia_actual)
        if os.path.exists(ruta_materia):
            archivos = [f for f in os.listdir(ruta_materia) if f.endswith(".txt")]
            # Ordenamiento inteligente para que sesion_10 no aparezca antes que sesion_2
            archivos.sort(key=lambda x: int(x.split('_')[1].split('.')[0]) if '_' in x and x.split('_')[1].split('.')[0].isdigit() else 0)
            return archivos
        return []

    def crear_interfaz(self):
        # 1. PANEL SUPERIOR: Gestión de Materias
        self.frame_materias = ctk.CTkFrame(self)
        self.frame_materias.pack(pady=10, padx=20, fill="x")
        
        self.lbl_seleccionar = ctk.CTkLabel(self.frame_materias, text="Seleccionar Materia:")
        self.lbl_seleccionar.pack(side="left", padx=(10, 5), pady=10)
        
        self.combo_materias = ctk.CTkComboBox(self.frame_materias, values=self.obtener_materias())
        self.combo_materias.pack(side="left", padx=5)
        
        self.btn_seleccionar = ctk.CTkButton(self.frame_materias, text="Cargar", width=80, command=self.cargar_materia)
        self.btn_seleccionar.pack(side="left", padx=5)
        
        self.lbl_sep = ctk.CTkLabel(self.frame_materias, text="|")
        self.lbl_sep.pack(side="left", padx=5)
        
        self.entry_nueva = ctk.CTkEntry(self.frame_materias, placeholder_text="Nombre nueva materia")
        self.entry_nueva.pack(side="left", padx=5)
        
        self.btn_crear = ctk.CTkButton(self.frame_materias, text="Crear", width=80, command=self.crear_materia)
        self.btn_crear.pack(side="left", padx=(5, 10))

        # 2. ÁREA DE SUBTÍTULOS
        self.texto_subtitulos = ctk.CTkLabel(
            self, text="Selecciona o crea una materia para empezar", font=("Arial", 24, "bold"), wraplength=750      
        )
        self.texto_subtitulos.pack(pady=30, padx=20, expand=True)

        # 3. PANEL INFERIOR: Botones de control
        self.frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_botones.pack(side="bottom", pady=10)

        self.btn_iniciar = ctk.CTkButton(
            self.frame_botones, text="Iniciar Captura", command=self.iniciar_captura, state="disabled"
        )
        self.btn_iniciar.pack(side="left", padx=10)
        
        self.btn_detener = ctk.CTkButton(
            self.frame_botones, text="Pausar", command=self.detener_captura, 
            state="disabled", fg_color="#8B0000", hover_color="#5C0000" 
        )
        self.btn_detener.pack(side="left", padx=10)

        # NUEVO BOTÓN: Finalizar Sesión
        self.btn_finalizar = ctk.CTkButton(
            self.frame_botones, text="Finalizar Sesión", command=self.finalizar_sesion,
            state="disabled", fg_color="#228B22", hover_color="#006400" # Verde bosque
        )
        self.btn_finalizar.pack(side="left", padx=10)

        # BOTÓN ACTUALIZADO: Explorador de bitácoras
        self.btn_bitacora = ctk.CTkButton(
            self.frame_botones, text="Explorar Historial", command=self.abrir_explorador_bitacoras,
            fg_color="#2B2B2B", hover_color="#404040", state="disabled"
        )
        self.btn_bitacora.pack(side="left", padx=10)

    # --- LÓGICA DE CONTROL DE SESIONES ---
    def preparar_sesion(self, nombre_materia):
        ruta_materia = os.path.join(self.directorio_base, nombre_materia)
        os.makedirs(ruta_materia, exist_ok=True)
        
        archivos = [f for f in os.listdir(ruta_materia) if f.startswith("sesion_") and f.endswith(".txt")]
        siguiente_num = len(archivos) + 1
        
        self.materia_actual = nombre_materia
        self.archivo_actual = os.path.join(ruta_materia, f"sesion_{siguiente_num}.txt")
        
        self.actualizar_subtitulo(f"📌 {nombre_materia} - Sesión {siguiente_num}\nPresiona 'Iniciar Captura' para empezar.")
        
        # Habilitamos iniciar y explorar el historial inmediatamente
        self.btn_iniciar.configure(state="normal", text="Iniciar Captura")
        self.btn_bitacora.configure(state="normal")
        self.combo_materias.configure(values=self.obtener_materias())
        self.combo_materias.set(nombre_materia)

    def finalizar_sesion(self):
        """Cierra definitivamente la sesión activa y prepara el entorno para la siguiente"""
        self.historial_memoria = [] # Vaciamos la memoria RAM de transcripción
        self.btn_finalizar.configure(state="disabled")
        
        # Volvemos a ejecutar la preparación de sesión que incrementará el número automáticamente
        self.preparar_sesion(self.materia_actual)
        
        # Si la ventana secundaria está abierta, actualizamos su menú de archivos
        if self.ventana_bitacora is not None and self.ventana_bitacora.winfo_exists():
            nombre_corto_actual = os.path.basename(self.archivo_actual)
            self.combo_sesiones_archivos.configure(values=self.obtener_archivos_materia())
            self.combo_sesiones_archivos.set(nombre_corto_actual)
            self.cambiar_sesion_visible(nombre_corto_actual)

    def cargar_materia(self):
        materia = self.combo_materias.get()
        if materia and materia != "Sin materias":
            self.preparar_sesion(materia)

    def crear_materia(self):
        nueva_materia = self.entry_nueva.get().strip()
        if nueva_materia:
            self.preparar_sesion(nueva_materia)
            self.entry_nueva.delete(0, 'end')

    def actualizar_subtitulo(self, nuevo_texto):
        self.texto_subtitulos.configure(text=nuevo_texto)

    def agregar_a_historial(self, linea):
        self.historial_memoria.append(linea)
        
        # Transmisión en vivo: Solo dibuja si la ventana está abierta Y está visualizando la sesión activa
        if self.ventana_bitacora is not None and self.ventana_bitacora.winfo_exists():
            archivo_seleccionado = self.combo_sesiones_archivos.get()
            nombre_actual = os.path.basename(self.archivo_actual)
            
            if archivo_seleccionado == nombre_actual:
                self.texto_historial.configure(state="normal")
                self.texto_historial.insert("end", linea + "\n")
                self.texto_historial.see("end")
                self.texto_historial.configure(state="disabled")

    # --- NUEVA INTERFAZ: EXPLORADOR SECUNDARIO ---
    def abrir_explorador_bitacoras(self):
        """Abre o enfoca la ventana secundaria con capacidades de navegación de archivos"""
        if self.ventana_bitacora is None or not self.ventana_bitacora.winfo_exists():
            self.ventana_bitacora = ctk.CTkToplevel(self)
            self.ventana_bitacora.title(f"Explorador de Historial - {self.materia_actual}")
            self.ventana_bitacora.geometry("650x450")
            self.ventana_bitacora.attributes("-topmost", True) 

            # Panel de navegación interno
            frame_navegacion = ctk.CTkFrame(self.ventana_bitacora)
            frame_navegacion.pack(pady=10, padx=20, fill="x")
            
            lbl_ver = ctk.CTkLabel(frame_navegacion, text="Seleccionar Archivo de Sesión:")
            lbl_ver.pack(side="left", padx=5, pady=5)
            
            # ComboBox para saltar entre sesiones viejas y la actual
            self.combo_sesiones_archivos = ctk.CTkComboBox(
                frame_navegacion, 
                values=self.obtener_archivos_materia(),
                command=self.cambiar_sesion_visible
            )
            self.combo_sesiones_archivos.pack(side="left", padx=5, expand=True, fill="x")
            
            # Área de lectura
            self.texto_historial = ctk.CTkTextbox(self.ventana_bitacora, font=("Arial", 16), wrap="word")
            self.texto_historial.pack(padx=20, pady=10, fill="both", expand=True)
            
            # Por defecto, abrir la sesión que está corriendo actualmente
            nombre_corto_actual = os.path.basename(self.archivo_actual)
            self.combo_sesiones_archivos.set(nombre_corto_actual)
            self.cambiar_sesion_visible(nombre_corto_actual)
        else:
            self.ventana_bitacora.focus()

    def cambiar_sesion_visible(self, nombre_archivo_seleccionado):
        """Cambia el texto mostrado dependiendo de si es historial de disco o la RAM actual"""
        self.texto_historial.configure(state="normal")
        self.texto_historial.delete("1.0", "end")
        
        ruta_completa = os.path.join(self.directorio_base, self.materia_actual, nombre_archivo_seleccionado)
        
        # Si coincide con el archivo en curso, leemos la memoria RAM para asegurar sincronía total
        if ruta_completa == self.archivo_actual:
            texto_completo = "\n".join(self.historial_memoria) + "\n"
            self.texto_historial.insert("end", texto_completo)
        else:
            # Si es una sesión antigua, abrimos el archivo físico desde el disco duro
            if os.path.exists(ruta_completa):
                with open(ruta_completa, "r", encoding="utf-8") as f:
                    self.texto_historial.insert("end", f.read())
                    
        self.texto_historial.configure(state="disabled")
        self.texto_historial.see("end")

    # --- FLUJO DE LA MÁQUINA DE ESTADOS DE AUDIO ---
    def iniciar_captura(self):
        self.escuchando = True
        self.btn_iniciar.configure(state="disabled")
        self.btn_detener.configure(state="normal", text="Pausar")
        self.btn_finalizar.configure(state="disabled") # No se puede finalizar a mitad de grabación
        
        hilo_voz = threading.Thread(target=escuchar_y_transcribir, args=(self,), daemon=True)
        hilo_voz.start()
        
    def detener_captura(self):
        self.escuchando = False
        self.btn_iniciar.configure(state="normal", text="Reanudar Capture")
        self.btn_detener.configure(state="disabled")
        self.btn_finalizar.configure(state="normal") # Ahora sí habilitamos dar por terminada la clase
        self.actualizar_subtitulo("Captura en pausa.\n¿Deseas reanudar el dictado o Finalizar la Sesión actual?")

def main():
    app = ClearFlowApp()
    app.mainloop()

if __name__ == "__main__":
    main()