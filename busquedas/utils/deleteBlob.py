from azure.storage.blob import BlobServiceClient, generate_container_sas, ContainerSasPermissions
from urllib.parse import urlparse
from datetime import datetime, timedelta
from gestion_plagas.settings import env

# Variables para acceder al blob
# Nombre de la cuenta de azure
account_name = env("AZURE_BLOB_NAME")

# Clave para autenticar solicitudes
account_key = env("AZURE_BLOB_KEY")

# Nombre del contenedor
container_name = 'plantstorage'

# genera el cliente
blob_service_client = BlobServiceClient(
    account_url=f"https://{account_name}.blob.core.windows.net",
    credential=account_key
    )

# Funcion que extraer nombre del contenedor y del blob de una URL de Azure Storage
def extract_container_and_blob(url):

    # Descoponer la url
    parsed_url = urlparse(url)

    # Obtener la path sin el / inicial
    path = parsed_url.path.lstrip('/')

    # Obtener lista con nombre del contenedor y blob
    parts = path.split('/', 1)

    #Verifico si en la lista parts hay 2 elementos
    if len(parts) == 2:
        container_name , blob_name = parts
        return container_name, blob_name

# Funcion que elimina un blod del cointainer
def delete_blob(container_name: str, blob_name: str):
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    blob_client.delete_blob()
    return f"Blob '{blob_name}' eliminado exitosamente del contenedor '{container_name}'."