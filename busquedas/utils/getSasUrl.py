from azure.storage.blob import BlobServiceClient, generate_container_sas, ContainerSasPermissions
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

# Funcion que genera el token
def get_sas_url():

    try:
        # permisos que va tener el contenedor
        permissions = ContainerSasPermissions(write=True, create=True, add=True)
        # tiempo en el que expira el token
        expiry_time = datetime.utcnow() + timedelta(minutes=10)
        print(account_name)
        sas_token = generate_container_sas(
            # La cuenta usada para generar el SAS
            account_name=account_name,
            # El nombre del containes
            container_name=container_name,
            # Permisos
            permission=permissions,
            # Tiempo cuando el token se vuelve invalido
            expiry=expiry_time,
            # Shared_key o access key
            account_key=account_key
        )

        print(sas_token)
        # genera url + el token sas
        url = f'https://{account_name}.blob.core.windows.net/{container_name}?{sas_token}'
        print(url)
        return url
    except Exception as e:
        print(e)
        return ""