import speech_recognition as sr
import time

def guardar_en_bitacora(texto):
    """Guarda el texto transcrito en un archivo .txt con la hora exacta."""
    timestamp = time.strftime("[%H:%M:%S]")
    with open("bitacora_clase.txt", "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {texto}\n")

def escuchar_y_transcribir(app):
    """
    Se ejecuta en segundo plano. Escucha, transcribe y manda el texto a la ventana.
    """
    r = sr.Recognizer()
    
    with sr.Microphone() as source:
        # Calibración de ruido para el entorno del aula 
        app.actualizar_subtitulo("Calibrando ruido del aula... (Guarde silencio 2s)")
        r.adjust_for_ambient_noise(source, duration=2)
        r.energy_threshold = 300  # Umbral base recomendado 
        
        app.actualizar_subtitulo("¡Listo! Escuchando al docente...")
        
        # Bucle que se mantiene escuchando mientras la app esté activa
        while app.escuchando:
            try:
                # Escucha fragmentos cortos (phrase_time_limit evita que se quede colgado)
                audio = r.listen(source, phrase_time_limit=5)
                texto = r.recognize_google(audio, language="es-ES")
                
                if texto:
                    app.actualizar_subtitulo(texto)  # Muestra en pantalla
                    guardar_en_bitacora(texto)       # Guarda en el .txt
                    
            except sr.UnknownValueError:
                # Si hay ruido que no es voz, lo ignoramos para no interrumpir
                pass
            except sr.RequestError:
                app.actualizar_subtitulo("[Error: Revisa tu conexión a Internet]")
            except Exception:
                # Captura cualquier otro error sin cerrar el programa
                pass