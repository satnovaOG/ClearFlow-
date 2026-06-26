import speech_recognition as sr
import time

def guardar_en_bitacora(texto, ruta_archivo):
    """Guarda el texto en la ruta dinámica que se le pase (ej: bitacoras/Redes/sesion_1.txt)"""
    timestamp = time.strftime("[%H:%M:%S]")
    linea = f"{timestamp} {texto}"
    
    # Escribimos en la ruta_archivo que nos pasa main.py
    with open(ruta_archivo, "a", encoding="utf-8") as f:
        f.write(linea + "\n")
        
    return linea

def escuchar_y_transcribir(app):
    r = sr.Recognizer()
    
    with sr.Microphone() as source:
        app.actualizar_subtitulo("Calibrando ruido del aula... (Guarde silencio 2s)")
        r.adjust_for_ambient_noise(source, duration=2)
        r.energy_threshold = 300
        
        app.actualizar_subtitulo(f"¡Listo! Escuchando clase de {app.materia_actual}...")
        
        while app.escuchando:
            try:
                audio = r.listen(source, phrase_time_limit=5)
                texto = r.recognize_google(audio, language="es-ES")
                
                if texto:
                    app.actualizar_subtitulo(texto)  
                    # Le pasamos la ruta del archivo actual a la función de guardado
                    linea_historial = guardar_en_bitacora(texto, app.archivo_actual) 
                    app.agregar_a_historial(linea_historial)      
                    
            except sr.UnknownValueError:
                pass
            except sr.RequestError:
                app.actualizar_subtitulo("[Error: Revisa tu conexión a Internet]")
            except Exception:
                pass