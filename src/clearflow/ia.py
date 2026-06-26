import os
import google.generativeai as genai
from dotenv import load_dotenv

# Cargar la clave secreta desde el archivo .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)

def generar_resumen(texto: str, alcance: str = "sesion") -> str:
    """Envía el texto a la IA y devuelve un resumen estructurado."""
    if not api_key:
        return "⚠️ Error: No se encontró la API Key en el archivo .env"
    if not texto.strip():
        return "⚠️ No hay texto suficiente para generar un resumen."

    try:
        # Usamos el modelo flash por su rapidez y gran ventana de contexto
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        if alcance == "sesion":
            prompt = (
                "Actúa como un tutor académico experto. Toma la siguiente transcripción "
                "de una clase universitaria y genera un resumen estructurado.\n\n"
                "REGLA ESTRICTA DE FORMATO: NO uses formato Markdown (PROHIBIDO usar asteriscos **, PROHIBIDO usar numerales #). "
                "Usa exclusivamente texto plano, saltos de línea claros, y MAYÚSCULAS para los títulos.\n\n"
                "Estructura requerida:\n"
                "🎯 TEMA PRINCIPAL:\n"
                "📌 PUNTOS CLAVE (usa viñetas con el símbolo '-'):\n"
                "📝 TAREAS O CONCEPTOS A REPASAR:\n\n"
                f"Texto de la clase:\n{texto}"
            )
        else:
            prompt = (
                "Actúa como un tutor académico experto. A continuación te presento las "
                "transcripciones de TODAS las clases de una materia. Elabora una guía de estudio "
                "general que resuma el progreso del curso.\n\n"
                "REGLA ESTRICTA DE FORMATO: NO uses formato Markdown (PROHIBIDO usar asteriscos **, PROHIBIDO usar numerales #). "
                "Usa exclusivamente texto plano, saltos de línea claros, y MAYÚSCULAS para los títulos.\n\n"
                f"Transcripciones de la materia:\n{texto}"
            )

        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Ocurrió un error con la IA:\n{e}"