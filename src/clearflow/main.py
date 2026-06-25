import customtkinter as ctk
import threading
import os
from clearflow.utils import escuchar_y_transcribir 
from clearflow.ia import generar_resumen 

class ClearFlowApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración principal de la ventana (Enfoque DUA)
        self.title("ClearFlow - Accesibilidad Educativa")
        self.geometry("850x350") 
        self.attributes("-topmost", True) # Ventana siempre visible (flotante)
        
        ctk.set_appearance_mode("dark") 
        ctk.set_default_color_theme("blue")
        
        # Variables de estado globales
        self.escuchando = False 
        self.historial_memoria = []  # Almacena la transcripción de la sesión en curso
        self.ventana_bitacora = None # Control de la ventana del explorador
        
        # Configuración del almacenamiento local
        self.directorio_base = "bitacoras"
        os.makedirs(self.directorio_base, exist_ok=True) 
        self.materia_actual = None
        self.archivo_actual = None

        self.crear_interfaz()

    def obtener_materias(self):
        """Escanea el disco duro buscando carpetas de materias creadas previamente."""
        if not os.path.exists(self.directorio_base):
            return ["Sin materias"]
        carpetas = [d for d in os.listdir(self.directorio_base) if os.path.isdir(os.path.join(self.directorio_base, d))]
        return carpetas if carpetas else ["Sin materias"]

    def obtener_archivos_materia(self):
        """Obtiene y ordena numéricamente los archivos de sesión de la materia actual."""
        ruta_materia = os.path.join(self.directorio_base, self.materia_actual)
        if os.path.exists(ruta_materia):
            archivos = [f for f in os.listdir(ruta_materia) if f.endswith(".txt")]
            # Ordenamiento por número de sesión para evitar desorden (ej: sesion_2 antes de sesion_10)
            archivos.sort(key=lambda x: int(x.split('_')[1].split('.')[0]) if '_' in x and x.split('_')[1].split('.')[0].isdigit() else 0)
            return archivos
        return []

    def crear_interfaz(self):
        """Dibuja los paneles de la pantalla principal."""
        # 1. PANEL SUPERIOR: Selección y creación de Materias
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

        # 2. PANEL CENTRAL: Subtitulado dinámico
        self.texto_subtitulos = ctk.CTkLabel(
            self, text="Selecciona o crea una materia para empezar", font=("Arial", 24, "bold"), wraplength=750      
        )
        self.texto_subtitulos.pack(pady=30, padx=20, expand=True)

        # 3. PANEL INFERIOR: Botones de control del sistema
        self.frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_botones.pack(side="bottom", pady=10)

        self.btn_iniciar = ctk.CTkButton(self.frame_botones, text="Iniciar Captura", command=self.iniciar_captura, state="disabled")
        self.btn_iniciar.pack(side="left", padx=10)
        
        self.btn_detener = ctk.CTkButton(
            self.frame_botones, text="Pausar", command=self.detener_captura, state="disabled", fg_color="#8B0000", hover_color="#5C0000" 
        )
        self.btn_detener.pack(side="left", padx=10)

        self.btn_finalizar = ctk.CTkButton(
            self.frame_botones, text="Finalizar Sesión", command=self.finalizar_sesion, state="disabled", fg_color="#228B22", hover_color="#006400"
        )
        self.btn_finalizar.pack(side="left", padx=10)

        self.btn_bitacora = ctk.CTkButton(
            self.frame_botones, text="Explorar Historial e IA", command=self.abrir_explorador_bitacoras, fg_color="#2B2B2B", hover_color="#404040", state="disabled"
        )
        self.btn_bitacora.pack(side="left", padx=10)

    # --- GESTIÓN DE ARCHIVOS Y MATERIAS ---
    def preparar_sesion(self, nombre_materia):
        """Determina de forma matemática el número correlativo que corresponde a la nueva sesión."""
        ruta_materia = os.path.join(self.directorio_base, nombre_materia)
        os.makedirs(ruta_materia, exist_ok=True)
        
        archivos = [f for f in os.listdir(ruta_materia) if f.startswith("sesion_") and f.endswith(".txt")]
        siguiente_num = len(archivos) + 1
        
        self.materia_actual = nombre_materia
        self.archivo_actual = os.path.join(ruta_materia, f"sesion_{siguiente_num}.txt")
        
        self.actualizar_subtitulo(f"📌 {nombre_materia} - Sesión {siguiente_num}\nPresiona 'Iniciar Captura' para empezar.")
        
        # Activación de controles de flujo esenciales
        self.btn_iniciar.configure(state="normal", text="Iniciar Captura")
        self.btn_bitacora.configure(state="normal")
        self.combo_materias.configure(values=self.obtener_materias())
        self.combo_materias.set(nombre_materia)

    def finalizar_sesion(self):
        """Cierra la sesión actual, limpia la memoria caché y prepara la sesión consecutiva."""
        self.historial_memoria = [] 
        self.btn_finalizar.configure(state="disabled")
        self.preparar_sesion(self.materia_actual)
        
        # Sincroniza dinámicamente la ventana del historial si se encuentra abierta
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
        """Guarda en RAM y actualiza la UI secundaria si el alumno está viendo la clase en vivo."""
        self.historial_memoria.append(linea)
        
        if self.ventana_bitacora is not None and self.ventana_bitacora.winfo_exists():
            archivo_seleccionado = self.combo_sesiones_archivos.get()
            nombre_actual = os.path.basename(self.archivo_actual)
            
            if archivo_seleccionado == nombre_actual:
                self.texto_historial.configure(state="normal")
                self.texto_historial.insert("end", linea + "\n")
                self.texto_historial.see("end")
                self.texto_historial.configure(state="disabled")

    # --- VENTANA SECUNDARIA: EXPLORADOR INTEGRADOR DE IA ---
    def abrir_explorador_bitacoras(self):
        """Despliega la interfaz de estudio con doble panel (Historial + Guía de IA)."""
        if self.ventana_bitacora is None or not self.ventana_bitacora.winfo_exists():
            self.ventana_bitacora = ctk.CTkToplevel(self)
            self.ventana_bitacora.title(f"Explorador de Historial Inteligente - {self.materia_actual}")
            self.ventana_bitacora.geometry("1000x550")
            self.ventana_bitacora.attributes("-topmost", True) 

            # Contenedor principal horizontal
            frame_contenedor = ctk.CTkFrame(self.ventana_bitacora, fg_color="transparent")
            frame_contenedor.pack(padx=10, pady=10, fill="both", expand=True)

            # PANEL DE LA IZQUIERDA: Lectura de transcripciones
            frame_izquierdo = ctk.CTkFrame(frame_contenedor)
            frame_izquierdo.pack(side="left", fill="both", expand=True, padx=(0, 5))

            lbl_ver = ctk.CTkLabel(frame_izquierdo, text="Bitácoras de Clase:", font=("Arial", 16, "bold"))
            lbl_ver.pack(pady=5, padx=10, anchor="w")

            self.combo_sesiones_archivos = ctk.CTkComboBox(
                frame_izquierdo, values=self.obtener_archivos_materia(), command=self.cambiar_sesion_visible
            )
            self.combo_sesiones_archivos.pack(padx=10, pady=5, fill="x")
            
            self.texto_historial = ctk.CTkTextbox(frame_izquierdo, font=("Arial", 16), wrap="word")
            self.texto_historial.pack(padx=10, pady=10, fill="both", expand=True)

            # PANEL DE LA DERECHA: Resumen pedagógico con IA
            frame_derecho = ctk.CTkFrame(frame_contenedor, width=350)
            frame_derecho.pack(side="right", fill="both", expand=False, padx=(5, 0))

            lbl_ia = ctk.CTkLabel(frame_derecho, text="🤖 Resumen con IA", font=("Arial", 16, "bold"))
            lbl_ia.pack(pady=10)

            frame_botones_ia = ctk.CTkFrame(frame_derecho, fg_color="transparent")
            frame_botones_ia.pack(fill="x", padx=10, pady=5)

            btn_resumir_sesion = ctk.CTkButton(frame_botones_ia, text="Resumir Sesión Actual", command=self.procesar_resumen_sesion)
            btn_resumir_sesion.pack(side="left", padx=2, expand=True)

            btn_resumir_materia = ctk.CTkButton(frame_botones_ia, text="Resumir TODA la Materia", fg_color="#4B0082", hover_color="#300052", command=self.procesar_resumen_materia)
            btn_resumir_materia.pack(side="right", padx=2, expand=True)

            # Elemento de visualización adaptado contra fatiga ocular (DUA)
            self.texto_resumen = ctk.CTkTextbox(frame_derecho, font=("Arial", 16), wrap="word", text_color="#F0F0F0")
            self.texto_resumen.pack(padx=10, pady=10, fill="both", expand=True)
            
            # Formato Ergonómico: Configuración de márgenes e interlineado cómodo para lectura fácil
            self.texto_resumen._textbox.configure(spacing1=5, spacing2=4, spacing3=5)
            
            self.texto_resumen.insert("end", "Presiona un botón arriba para generar una guía de estudio automática.")
            self.texto_resumen.configure(state="disabled")

            # Abre por defecto el archivo en curso
            nombre_corto_actual = os.path.basename(self.archivo_actual)
            self.combo_sesiones_archivos.set(nombre_corto_actual)
            self.cambiar_sesion_visible(nombre_corto_actual)
        else:
            self.ventana_bitacora.focus()

    def cambiar_sesion_visible(self, nombre_archivo_seleccionado):
        """Intercambia el texto en pantalla dependiendo del archivo del historial elegido."""
        self.texto_historial.configure(state="normal")
        self.texto_historial.delete("1.0", "end")
        
        ruta_completa = os.path.join(self.directorio_base, self.materia_actual, nombre_archivo_seleccionado)
        
        if ruta_completa == self.archivo_actual:
            # Si es la sesión activa, lee el flujo dinámico directo de la memoria RAM
            texto_completo = "\n".join(self.historial_memoria) + "\n"
            self.texto_historial.insert("end", texto_completo)
        else:
            # Si es una sesión antigua, lee de forma asíncrona el archivo físico del almacenamiento
            if os.path.exists(ruta_completa):
                with open(ruta_completa, "r", encoding="utf-8") as f:
                    self.texto_historial.insert("end", f.read())
                    
        self.texto_historial.configure(state="disabled")
        self.texto_historial.see("end")
        
        # Limpieza estándar del panel derecho al alternar de archivo
        self.texto_resumen.configure(state="normal")
        self.texto_resumen.delete("1.0", "end")
        self.texto_resumen.insert("end", "Presiona 'Resumir Sesión Actual' para generar los puntos clave de este texto.")
        self.texto_resumen.configure(state="disabled")

    # --- CONTROLADOR ASÍNCRONO DE INTELIGENCIA ARTIFICIAL ---
    def actualizar_panel_ia(self, texto):
        """Inyecta el texto generado de forma segura en la caja gráfica."""
        self.texto_resumen.configure(state="normal")
        self.texto_resumen.delete("1.0", "end")
        self.texto_resumen.insert("end", texto)
        self.texto_resumen.configure(state="disabled")

    def procesar_resumen_sesion(self):
        """Lanza la petición de resumen en un hilo independiente para evitar congelamiento de la ventana."""
        self.actualizar_panel_ia("⏳ Analizando la clase...\n\nGenerando puntos clave e identificando tareas...")
        texto_actual = self.texto_historial.get("1.0", "end-1c")
        
        def tarea_ia():
            resultado = generar_resumen(texto_actual, alcance="sesion")
            self.actualizar_panel_ia(resultado)
            
        threading.Thread(target=tarea_ia, daemon=True).start()

    def procesar_resumen_materia(self):
        """Une el contenido histórico completo de la materia para generar una macro guía de estudio."""
        self.actualizar_panel_ia("⏳ Recopilando TODAS las sesiones de la materia...\n\nConstruyendo la guía de estudio global. Esto puede tardar unos segundos...")
        
        texto_global = ""
        ruta_materia = os.path.join(self.directorio_base, self.materia_actual)
        archivos = self.obtener_archivos_materia()
        
        for arch in archivos:
            ruta_arch = os.path.join(ruta_materia, arch)
            if os.path.exists(ruta_arch):
                with open(ruta_arch, "r", encoding="utf-8") as f:
                    texto_global += f"\n--- CLASE DE LA {arch.upper()} ---\n"
                    texto_global += f.read()

        def tarea_ia():
            resultado = generar_resumen(texto_global, alcance="materia")
            self.actualizar_panel_ia(resultado)
            
        threading.Thread(target=tarea_ia, daemon=True).start()

    # --- FLUJO DE AUDIO CON HILOS PARALELOS ---
    def iniciar_captura(self):
        self.escuchando = True
        self.btn_iniciar.configure(state="disabled")
        self.btn_detener.configure(state="normal", text="Pausar")
        self.btn_finalizar.configure(state="disabled") 
        
        hilo_voz = threading.Thread(target=escuchar_y_transcribir, args=(self,), daemon=True)
        hilo_voz.start()
        
    def detener_captura(self):
        self.escuchando = False
        self.btn_iniciar.configure(state="normal", text="Reanudar")
        self.btn_detener.configure(state="disabled")
        self.btn_finalizar.configure(state="normal") 
        self.actualizar_subtitulo("Captura en pausa.\n¿Deseas reanudar el dictado o Finalizar la Sesión actual?")

def main():
    app = ClearFlowApp()
    app.mainloop()

if __name__ == "__main__":
    main()