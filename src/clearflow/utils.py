import speech_recognition as sr
import time

def guardar_en_bitacora(texto):
    """Guarda el texto y retorna la línea completa con la hora."""
    timestamp = time.strftime("[%H:%M:%S]")
    linea = f"{timestamp} {texto}"
    
    with open("bitacora_clase.txt", "a", encoding="utf-8") as f:
        f.write(linea + "\n")
        
    return linea # Devolvemos la línea para usarla en la interfaz

def escuchar_y_transcribir(app):
    """
    Se ejecuta en segundo plano. Escucha, transcribe y manda el texto a la ventana principal y al historial.
    """
    r = sr.Recognizer()
    
    with sr.Microphone() as source:
        app.actualizar_subtitulo("Calibrando ruido del aula... (Guarde silencio 2s)")
        r.adjust_for_ambient_noise(source, duration=2)
        r.energy_threshold = 300
        
        app.actualizar_subtitulo("¡Listo! Escuchando al docente...")
        
        while app.escuchando:
            try:
                audio = r.listen(source, phrase_time_limit=5)
                texto = r.recognize_google(audio, language="es-ES")
                
                if texto:
                    app.actualizar_subtitulo(texto)  
                    # Guardamos en el .txt y obtenemos la línea con el tiempo
                    linea_historial = guardar_en_bitacora(texto) 
                    # Enviamos esa línea al módulo de la bitácora visual
                    app.agregar_a_historial(linea_historial)      
                    
            except sr.UnknownValueError:
                pass
            except sr.RequestError:
                app.actualizar_subtitulo("[Error: Revisa tu conexión a Internet]")
            except Exception:
                pass