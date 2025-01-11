import os
import json
from django.utils.translation import get_language

# Path del archivo json
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Funcion que carga el archivo de traducciones de espanol json
def load_translation():
    # Obtiene codigo del lenguaje
    language = get_language()
    # Path del archivo de traducciones en el language
    TRANSLATION_PATH = os.path.join(BASE_DIR, 'translations', f"{language}.json")

    try:
        with open(TRANSLATION_PATH, 'r', encoding='utf-8') as file:
            translations = json.load(file)
        return translations
    except FileNotFoundError:
        print("Archivo de traducciones no encontrado")
        return {"error" : "Archivo de traducciones no encontrado"}
    except json.JSONDecodeError:
        print("Error decoding el archivo de traducciones")
        return {"error" : "Error decoding el archivo de traducciones"}

# Funcion que traduce la enfermedad
def illness_translation(key):
    translation_file = load_translation()
    illness = translation_file.get(key, key)
    return  illness