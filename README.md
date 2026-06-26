# ClearFlow 🌊 - Accesibilidad Educativa

ClearFlow es una tecnología de asistencia de código abierto desarrollada en Python. Su propósito principal es derribar las barreras de comunicación de los estudiantes sordos en la educación superior mediante la automatización de la toma de apuntes y la reducción de la fatiga cognitiva.

Este proyecto se fundamenta teóricamente en los principios del **Diseño Universal para el Aprendizaje (DUA)**, ofreciendo múltiples canales de representación de la información.

## ✨ Características Principales

- **Subtitulado en Tiempo Real:** Reconocimiento de voz continuo optimizado para aulas ruidosas (calibración automática de ruido ambiental).
- **Gestión Inteligente de Bitácoras:** Organización automática de las clases en carpetas por "Materias" y cálculo correlativo de "Sesiones" (ej. `sesion_1.txt`).
- **Interfaz Gráfica Adaptativa:** Diseño en modo oscuro (Dark Mode), tipografía grande e interlineado ajustado para prevenir la fatiga visual.
- **Tutor de IA Integrado:** Resúmenes y guías de estudio generados automáticamente a partir de las transcripciones de clase, impulsados por Google Gemini 2.5 Flash.

---

## 🛠️ Requisitos Previos (Especial para Windows/WSL)

El proyecto utiliza el gestor de paquetes ultrarrápido `uv`. Si estás utilizando **Ubuntu en WSL**, asegúrate de tener instaladas las siguientes dependencias del sistema operativo para procesar el audio y la interfaz gráfica:

```bash
# Actualizar repositorios e instalar librerías de interfaz, desarrollo y audio
sudo apt update
sudo apt install python3-tk python3-dev python3.12-dev portaudio19-dev libasound2-plugins pulseaudio -y
```

---

## 🚀 Instalación y Configuración

1. **Clonar el repositorio:**
   ```bash
   git clone git@github.com:TU_USUARIO/ClearFlow-.git
   cd ClearFlow-
   ```

2. **Instalar dependencias de Python con `uv`:**
   ```bash
   # uv detectará el pyproject.toml e instalará customtkinter, SpeechRecognition, PyAudio, etc.
   uv sync
   ```

3. **Configurar la Inteligencia Artificial:**
   - Crea un archivo llamado `.env` en la raíz del proyecto.
   - Añade tu clave de API de Google Gemini de la siguiente manera:
     ```env
     GEMINI_API_KEY=tu_clave_api_aqui
     ```

---

## 💻 Uso de la Aplicación

Para lanzar la interfaz de ClearFlow, ejecuta:

```bash
uv run src/clearflow/main.py
```

### Flujo de Trabajo Recomendado:
1. Al abrir la app, selecciona una materia existente en el menú superior o escribe el nombre de una nueva y presiona **Crear**.
2. Presiona **Iniciar Captura**. Guarda silencio durante 2 segundos para que el micrófono calibre el ruido del aula.
3. Puedes **Pausar** y **Reanudar** la captura en cualquier momento.
4. Al finalizar la clase, presiona **Finalizar Sesión**.
5. Abre el **Explorador de Historial e IA** para leer la clase grabada y generar tus guías de estudio automáticas.

---

## 📁 Estructura del Proyecto

```text
ClearFlow-/
├── bitacoras/           # (Ignorado por Git) Archivos .txt de las clases
├── src/clearflow/       # Código fuente principal
│   ├── main.py          # Interfaz gráfica y control de estados
│   ├── utils.py         # Módulo de reconocimiento de voz (Speech-to-Text)
│   └── ia.py            # Integración con Google Generative AI (Gemini)
├── .env                 # (Ignorado por Git) Claves secretas
├── .gitignore           # Archivos locales excluidos
├── pyproject.toml       # Configuración y dependencias del proyecto (uv)
└── README.md            # Documentación
```