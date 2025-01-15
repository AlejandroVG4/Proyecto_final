from gestion_plagas.settings import env
from .deleteBlob import extract_container_and_blob, delete_blob
import requests

# Variables de conexion con CustomVision PlantDiseaseDetector
endpoint = env("CUSTOM_VISION_ENDPOINT")
key = env("CUSTOM_VISION_KEY")
project_id = env("CUSTOM_VISION_PROJECT_ID")
iteration_name = env("CUSTOM_VISION_ITERATION")

# Variables de conexion con Custom Vision IsPlantDetector
endpoint_is_plant = env("PLANT_DETECTOR_CUSTOM_VISION_ENDPOINT")
key_is_plant = env("PLANT_DETECTOR_CUSTOM_VISION_KEY")
project_id_is_plant = env("PLANT_DETECTOR_CUSTOM_VISION_PROJECT_ID")
iteration_name_is_plant = env("PLANT_DETECTOR_CUSTOM_VISION_ITERATION")

# Endpoint Custom Vision PlantDiseaseDetector
custom_model_endpoint = f'{endpoint}/customvision/v3.0/Prediction/{project_id}/classify/iterations/{iteration_name}/url'

# Endpoint Custom Vision isPlantDetector
custom_model_endpoint_is_plant = f'{endpoint_is_plant}/customvision/v3.0/Prediction/{project_id_is_plant}/classify/iterations/{iteration_name_is_plant}/url'

def analyze_image(imgUrl):
    # encabezados
    headers = {
        "Content-Type":"application/json",
        "Prediction-Key": key
    }

    data = {
        "Url": imgUrl
    }

    try:
        # solicitud post a la ia
        response = requests.post(custom_model_endpoint, headers=headers, json=data)

        #verificar si la solicitud fue exitosa
        if response.status_code == 200:
            response_data = response.json()

            # Imprime el Id del projecto usado para comprobar que se usa PlantDiseaseDetector
            # print(response_data["project"])
            # print("numero de la iteracion", response_data["iteration"])
            # print("nombre de la iteracion", iteration_name)
            # print(response_data["created"])

            # Variable predictions almacena la lista de diccionario con la probabilidad de cada resultado
            predictions = response_data["predictions"]

            if predictions:
                #Funcion que encuentra el mayor valor de los resultados
                closest_to_one = max(predictions, key= lambda x: x["probability"])

                # Extraemos nombre de la enfermedad con el mayor valor
                illness_name = closest_to_one["tagName"]

                return illness_name
            else:
                print("Sin Resultados")

            return
        else:
            print(f"Error {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(e)
        return None

# Funcion que identifica si la imagen es una planta
def check_if_plant(imgUrl):
    headers = {
        "Content-Type":"application/json",
        "Prediction-Key": key_is_plant
    }

    data = {
        "Url": imgUrl
    }

    try:
        response = requests.post(custom_model_endpoint_is_plant, headers=headers, json=data)

        if response.status_code == 200:
            response_data = response.json()

            print(response_data)

            predictions = response_data["predictions"]

            if predictions:
                closest_to_one = max(predictions, key= lambda x: x["probability"])
                if closest_to_one["tagName"] == 'no_plant':
                    parts = extract_container_and_blob(imgUrl)
                    was_deleted = delete_blob(parts[0], parts[1])
                    print(was_deleted)
                    return False
                else:
                    return True
        else:
            print("Sin resultado")

    except Exception as e:
        print(e)
        return None