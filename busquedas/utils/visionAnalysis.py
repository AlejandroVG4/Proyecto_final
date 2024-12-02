from gestion_plagas.settings import env
import requests

#Variables de conexion con ia

endpoint = env("COMP_VISION_ENDPOINT")
key = env("COMP_VISION_KEY")
model_name = env("COMP_VISION_MODELNAME")

# creamos la url para del endpoint con la ia
custom_model_endpoint = f'{endpoint}/computervision/imageanalysis:analyze?model-name={model_name}&api-version=2023-04-01-preview'

# Imagen de prueba
prueba_img = "https://illnessstorage2.blob.core.windows.net/plantstorage/powdery_mildew.jpg"

def analyze_image(imgUrl=prueba_img):
    print("En funcion analisis")
    # encabezados
    headers = {
        "Content-Type":"application/json",
        "Ocp-Apim-Subscription-Key": key
    }

    data = {
        "url" : imgUrl
    }

    try:
        # solicitud post a la ia
        response = requests.post(custom_model_endpoint, headers=headers, json=data)

        #verificar si la solicitud fue exitosa
        if response.status_code == 200:
            response_data = response.json()
            

            #print("ModelVersion", response_data["modelVersion"])
            #print("Metadata:", response_data.["metaData"])

            custom_model_result = response_data['customModelResult']
            print(custom_model_result)

            if "tagsResult" in custom_model_result : 
                print("Condicional tagsResult")
                tags_result = custom_model_result["tagsResult"]

                #TODO Aplicar Logica para devolver el valor mas cercano a 1
                return tags_result
            else:
                print("Sin Resultados")

            return 
        else:
            print(f"Error {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(e)
        return None
