import pandas as pd

def encontrar_moda(data_frame):

    # Asegurar que la fecha sea de tipo datetime
    data_frame["fecha_creacion"] = pd.to_datetime(data_frame["fecha_creacion"])

    # definir las fechas de inicio y fin con UTC
    hoy = pd.Timestamp.now(tz='UTC')
    inicio = hoy - pd.DateOffset(days=30)

    # filtrar los datos para tener solo los últimos 30 días
    data_filtrado = data_frame[(data_frame["fecha_creacion"] >= inicio) & (data_frame["fecha_creacion"]<= hoy)]

    # Crear un data frame como solo los id de la enfermedad
    enfermedades_data = {'enfermedades': data_filtrado["enfermedad"].tolist()}

    # Convertir en una Serie de pandas
    serie_enfermedades = pd.Series(enfermedades_data["enfermedades"])
        
    # Hallar la moda(s)
    moda = (serie_enfermedades.mode()).tolist()

    # Transformar la moda en una lista
    enfermedad_id = moda[0]

    return [enfermedad_id, inicio, hoy]