import customtkinter as ctk
import threading
import os
from clearflow.utils import escuchar_y_transcribir
from clearflow.ia import generar_resumen
from clearflow.preferences import (
    SUBTITLE_BASE,
    BODY_BASE,
    SUBTITLE_WRAP_BASE,
    FONT_SCALES,
    load_preferences,
    save_preferences,
    scaled_font,
    scale_label,
)

ACCENT = "#4A9EFF"
CARD_BG = "#1e1e2e"
HEADER_BG = "#1a1a2e"
CORNER_RADIUS = 12
BTN_HEIGHT = 36


class ClearFlowApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ClearFlow - Accesibilidad Educativa")
        self.geometry("850x420")
        self.attributes("-topmost", True)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.escuchando = False
        self.historial_memoria = []
        self.ventana_bitacora = None
        self.lbls_tamano = []
        self.lbl_ver = None
        self.lbl_ia = None

        self.directorio_base = "bitacoras"
        os.makedirs(self.directorio_base, exist_ok=True)
        self.materia_actual = None
        self.archivo_actual = None

        self.font_scale = load_preferences()["font_scale"]
        self.crear_interfaz()
        self.aplicar_tamano_letra()

    def obtener_materias(self):
        if not os.path.exists(self.directorio_base):
            return ["Sin materias"]
        carpetas = [
            d for d in os.listdir(self.directorio_base)
            if os.path.isdir(os.path.join(self.directorio_base, d))
        ]
        return carpetas if carpetas else ["Sin materias"]

    def obtener_archivos_materia(self):
        ruta_materia = os.path.join(self.directorio_base, self.materia_actual)
        if os.path.exists(ruta_materia):
            archivos = [f for f in os.listdir(ruta_materia) if f.endswith(".txt")]
            archivos.sort(
                key=lambda x: int(x.split("_")[1].split(".")[0])
                if "_" in x and x.split("_")[1].split(".")[0].isdigit()
                else 0
            )
            return archivos
        return []

    def crear_barra_accesibilidad(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(pady=(0, 8))

        btn_menos = ctk.CTkButton(
            frame, text="A−", width=44, height=32,
            command=lambda: self.cambiar_tamano_letra(-1),
        )
        btn_menos.pack(side="left", padx=(0, 8))

        lbl_tamano = ctk.CTkLabel(
            frame, text=f"Tamaño: {scale_label(self.font_scale)}",
            text_color=ACCENT,
        )
        lbl_tamano.pack(side="left", padx=8)
        self.lbls_tamano.append(lbl_tamano)

        btn_mas = ctk.CTkButton(
            frame, text="A+", width=44, height=32,
            command=lambda: self.cambiar_tamano_letra(1),
        )
        btn_mas.pack(side="left", padx=(8, 0))

        return frame

    def cambiar_tamano_letra(self, delta):
        idx = FONT_SCALES.index(self.font_scale)
        new_idx = max(0, min(len(FONT_SCALES) - 1, idx + delta))
        if new_idx == idx:
            return

        self.font_scale = FONT_SCALES[new_idx]
        self.aplicar_tamano_letra()
        save_preferences({"font_scale": self.font_scale})

        etiqueta = f"Tamaño: {scale_label(self.font_scale)}"
        for lbl in self.lbls_tamano:
            if lbl.winfo_exists():
                lbl.configure(text=etiqueta)

    def aplicar_tamano_letra(self):
        self.texto_subtitulos.configure(
            font=scaled_font(SUBTITLE_BASE, bold=True, scale=self.font_scale),
            wraplength=int(SUBTITLE_WRAP_BASE * self.font_scale),
        )

        if self.ventana_bitacora is not None and self.ventana_bitacora.winfo_exists():
            self.texto_historial.configure(
                font=scaled_font(BODY_BASE, scale=self.font_scale)
            )
            self.texto_resumen.configure(
                font=scaled_font(BODY_BASE, scale=self.font_scale)
            )
            if self.lbl_ver is not None:
                self.lbl_ver.configure(
                    font=scaled_font(BODY_BASE, bold=True, scale=self.font_scale),
                    text_color=ACCENT,
                )
            if self.lbl_ia is not None:
                self.lbl_ia.configure(
                    font=scaled_font(BODY_BASE, bold=True, scale=self.font_scale),
                    text_color=ACCENT,
                )

    def crear_interfaz(self):
        # Encabezado
        self.frame_header = ctk.CTkFrame(self, fg_color=HEADER_BG, corner_radius=CORNER_RADIUS)
        self.frame_header.pack(pady=(12, 8), padx=20, fill="x")

        self.lbl_titulo = ctk.CTkLabel(
            self.frame_header, text="ClearFlow",
            font=("Arial", 22, "bold"), text_color=ACCENT,
        )
        self.lbl_titulo.pack(side="left", padx=(16, 8), pady=12)

        self.lbl_subtitulo = ctk.CTkLabel(
            self.frame_header, text="Accesibilidad Educativa",
            font=("Arial", 13), text_color="#888888",
        )
        self.lbl_subtitulo.pack(side="left", padx=(0, 16), pady=12)

        # Panel de materias
        self.frame_materias = ctk.CTkFrame(self, corner_radius=CORNER_RADIUS)
        self.frame_materias.pack(pady=(0, 8), padx=20, fill="x")

        self.lbl_seleccionar = ctk.CTkLabel(self.frame_materias, text="Seleccionar Materia:")
        self.lbl_seleccionar.pack(side="left", padx=(12, 5), pady=12)

        self.combo_materias = ctk.CTkComboBox(
            self.frame_materias, values=self.obtener_materias(), width=180,
        )
        self.combo_materias.pack(side="left", padx=5)

        self.btn_seleccionar = ctk.CTkButton(
            self.frame_materias, text="Cargar", width=80, height=BTN_HEIGHT,
            command=self.cargar_materia,
        )
        self.btn_seleccionar.pack(side="left", padx=5)

        self.lbl_sep = ctk.CTkLabel(
            self.frame_materias, text="|", text_color="#666666",
        )
        self.lbl_sep.pack(side="left", padx=8)

        self.entry_nueva = ctk.CTkEntry(
            self.frame_materias, placeholder_text="Nombre nueva materia", width=180,
        )
        self.entry_nueva.pack(side="left", padx=5)

        self.btn_crear = ctk.CTkButton(
            self.frame_materias, text="Crear", width=80, height=BTN_HEIGHT,
            command=self.crear_materia,
        )
        self.btn_crear.pack(side="left", padx=(5, 12))

        # Barra de accesibilidad
        self.crear_barra_accesibilidad(self)

        # Panel central: subtítulos en tarjeta
        self.frame_subtitulos = ctk.CTkFrame(
            self, fg_color=CARD_BG, corner_radius=CORNER_RADIUS,
        )
        self.frame_subtitulos.pack(pady=(0, 12), padx=20, fill="both", expand=True)

        self.texto_subtitulos = ctk.CTkLabel(
            self.frame_subtitulos,
            text="Selecciona o crea una materia para empezar",
            font=("Arial", SUBTITLE_BASE, "bold"),
            wraplength=SUBTITLE_WRAP_BASE,
        )
        self.texto_subtitulos.pack(padx=24, pady=20, expand=True)

        # Panel inferior: botones de control
        self.frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_botones.pack(side="bottom", pady=12)

        self.btn_iniciar = ctk.CTkButton(
            self.frame_botones, text="Iniciar Captura", height=BTN_HEIGHT,
            command=self.iniciar_captura, state="disabled",
        )
        self.btn_iniciar.pack(side="left", padx=10)

        self.btn_detener = ctk.CTkButton(
            self.frame_botones, text="Pausar", height=BTN_HEIGHT,
            command=self.detener_captura, state="disabled",
            fg_color="#8B0000", hover_color="#5C0000",
        )
        self.btn_detener.pack(side="left", padx=10)

        self.btn_finalizar = ctk.CTkButton(
            self.frame_botones, text="Finalizar Sesión", height=BTN_HEIGHT,
            command=self.finalizar_sesion, state="disabled",
            fg_color="#228B22", hover_color="#006400",
        )
        self.btn_finalizar.pack(side="left", padx=10)

        self.btn_bitacora = ctk.CTkButton(
            self.frame_botones, text="Explorar Historial e IA", height=BTN_HEIGHT,
            command=self.abrir_explorador_bitacoras,
            fg_color="#2B2B2B", hover_color="#404040", state="disabled",
        )
        self.btn_bitacora.pack(side="left", padx=10)

    def preparar_sesion(self, nombre_materia):
        ruta_materia = os.path.join(self.directorio_base, nombre_materia)
        os.makedirs(ruta_materia, exist_ok=True)

        archivos = [
            f for f in os.listdir(ruta_materia)
            if f.startswith("sesion_") and f.endswith(".txt")
        ]
        siguiente_num = len(archivos) + 1

        self.materia_actual = nombre_materia
        self.archivo_actual = os.path.join(ruta_materia, f"sesion_{siguiente_num}.txt")

        self.actualizar_subtitulo(
            f"📌 {nombre_materia} - Sesión {siguiente_num}\n"
            "Presiona 'Iniciar Captura' para empezar."
        )

        self.btn_iniciar.configure(state="normal", text="Iniciar Captura")
        self.btn_bitacora.configure(state="normal")
        self.combo_materias.configure(values=self.obtener_materias())
        self.combo_materias.set(nombre_materia)

    def finalizar_sesion(self):
        self.historial_memoria = []
        self.btn_finalizar.configure(state="disabled")
        self.preparar_sesion(self.materia_actual)

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
            self.entry_nueva.delete(0, "end")

    def actualizar_subtitulo(self, nuevo_texto):
        self.texto_subtitulos.configure(text=nuevo_texto)

    def agregar_a_historial(self, linea):
        self.historial_memoria.append(linea)

        if self.ventana_bitacora is not None and self.ventana_bitacora.winfo_exists():
            archivo_seleccionado = self.combo_sesiones_archivos.get()
            nombre_actual = os.path.basename(self.archivo_actual)

            if archivo_seleccionado == nombre_actual:
                self.texto_historial.configure(state="normal")
                self.texto_historial.insert("end", linea + "\n")
                self.texto_historial.see("end")
                self.texto_historial.configure(state="disabled")

    def abrir_explorador_bitacoras(self):
        if self.ventana_bitacora is None or not self.ventana_bitacora.winfo_exists():
            self.ventana_bitacora = ctk.CTkToplevel(self)
            self.ventana_bitacora.title(
                f"Explorador de Historial Inteligente - {self.materia_actual}"
            )
            self.ventana_bitacora.geometry("1000x580")
            self.ventana_bitacora.attributes("-topmost", True)

            self.crear_barra_accesibilidad(self.ventana_bitacora)

            frame_contenedor = ctk.CTkFrame(
                self.ventana_bitacora, fg_color="transparent",
            )
            frame_contenedor.pack(padx=10, pady=(0, 10), fill="both", expand=True)

            frame_izquierdo = ctk.CTkFrame(
                frame_contenedor, corner_radius=CORNER_RADIUS,
            )
            frame_izquierdo.pack(side="left", fill="both", expand=True, padx=(0, 5))

            self.lbl_ver = ctk.CTkLabel(
                frame_izquierdo, text="Bitácoras de Clase:",
                font=("Arial", BODY_BASE, "bold"), text_color=ACCENT,
            )
            self.lbl_ver.pack(pady=(10, 5), padx=12, anchor="w")

            self.combo_sesiones_archivos = ctk.CTkComboBox(
                frame_izquierdo,
                values=self.obtener_archivos_materia(),
                command=self.cambiar_sesion_visible,
            )
            self.combo_sesiones_archivos.pack(padx=12, pady=5, fill="x")

            self.texto_historial = ctk.CTkTextbox(
                frame_izquierdo, font=("Arial", BODY_BASE), wrap="word",
            )
            self.texto_historial.pack(padx=12, pady=(5, 12), fill="both", expand=True)

            frame_derecho = ctk.CTkFrame(
                frame_contenedor, width=350, corner_radius=CORNER_RADIUS,
            )
            frame_derecho.pack(side="right", fill="both", expand=False, padx=(5, 0))

            self.lbl_ia = ctk.CTkLabel(
                frame_derecho, text="🤖 Resumen con IA",
                font=("Arial", BODY_BASE, "bold"), text_color=ACCENT,
            )
            self.lbl_ia.pack(pady=(12, 8))

            frame_botones_ia = ctk.CTkFrame(frame_derecho, fg_color="transparent")
            frame_botones_ia.pack(fill="x", padx=12, pady=5)

            btn_resumir_sesion = ctk.CTkButton(
                frame_botones_ia, text="Resumir Sesión Actual", height=BTN_HEIGHT,
                command=self.procesar_resumen_sesion,
            )
            btn_resumir_sesion.pack(side="left", padx=2, expand=True)

            btn_resumir_materia = ctk.CTkButton(
                frame_botones_ia, text="Resumir TODA la Materia", height=BTN_HEIGHT,
                fg_color="#4B0082", hover_color="#300052",
                command=self.procesar_resumen_materia,
            )
            btn_resumir_materia.pack(side="right", padx=2, expand=True)

            self.texto_resumen = ctk.CTkTextbox(
                frame_derecho, font=("Arial", BODY_BASE),
                wrap="word", text_color="#F0F0F0",
            )
            self.texto_resumen.pack(padx=12, pady=(5, 12), fill="both", expand=True)
            self.texto_resumen._textbox.configure(spacing1=5, spacing2=4, spacing3=5)

            self.texto_resumen.insert(
                "end",
                "Presiona un botón arriba para generar una guía de estudio automática.",
            )
            self.texto_resumen.configure(state="disabled")

            self.aplicar_tamano_letra()

            nombre_corto_actual = os.path.basename(self.archivo_actual)
            self.combo_sesiones_archivos.set(nombre_corto_actual)
            self.cambiar_sesion_visible(nombre_corto_actual)
        else:
            self.ventana_bitacora.focus()

    def cambiar_sesion_visible(self, nombre_archivo_seleccionado):
        self.texto_historial.configure(state="normal")
        self.texto_historial.delete("1.0", "end")

        ruta_completa = os.path.join(
            self.directorio_base, self.materia_actual, nombre_archivo_seleccionado
        )

        if ruta_completa == self.archivo_actual:
            texto_completo = "\n".join(self.historial_memoria) + "\n"
            self.texto_historial.insert("end", texto_completo)
        else:
            if os.path.exists(ruta_completa):
                with open(ruta_completa, "r", encoding="utf-8") as f:
                    self.texto_historial.insert("end", f.read())

        self.texto_historial.configure(state="disabled")
        self.texto_historial.see("end")

        self.texto_resumen.configure(state="normal")
        self.texto_resumen.delete("1.0", "end")
        self.texto_resumen.insert(
            "end",
            "Presiona 'Resumir Sesión Actual' para generar los puntos clave de este texto.",
        )
        self.texto_resumen.configure(state="disabled")

    def actualizar_panel_ia(self, texto):
        self.texto_resumen.configure(state="normal")
        self.texto_resumen.delete("1.0", "end")
        self.texto_resumen.insert("end", texto)
        self.texto_resumen.configure(state="disabled")

    def procesar_resumen_sesion(self):
        self.actualizar_panel_ia(
            "⏳ Analizando la clase...\n\nGenerando puntos clave e identificando tareas..."
        )
        texto_actual = self.texto_historial.get("1.0", "end-1c")

        def tarea_ia():
            resultado = generar_resumen(texto_actual, alcance="sesion")
            self.actualizar_panel_ia(resultado)

        threading.Thread(target=tarea_ia, daemon=True).start()

    def procesar_resumen_materia(self):
        self.actualizar_panel_ia(
            "⏳ Recopilando TODAS las sesiones de la materia...\n\n"
            "Construyendo la guía de estudio global. Esto puede tardar unos segundos..."
        )

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

    def iniciar_captura(self):
        self.escuchando = True
        self.btn_iniciar.configure(state="disabled")
        self.btn_detener.configure(state="normal", text="Pausar")
        self.btn_finalizar.configure(state="disabled")

        hilo_voz = threading.Thread(
            target=escuchar_y_transcribir, args=(self,), daemon=True,
        )
        hilo_voz.start()

    def detener_captura(self):
        self.escuchando = False
        self.btn_iniciar.configure(state="normal", text="Reanudar")
        self.btn_detener.configure(state="disabled")
        self.btn_finalizar.configure(state="normal")
        self.actualizar_subtitulo(
            "Captura en pausa.\n"
            "¿Deseas reanudar el dictado o Finalizar la Sesión actual?"
        )


def main():
    app = ClearFlowApp()
    app.mainloop()


if __name__ == "__main__":
    main()
