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

    # diccionario resultado
    diccionario_resultado = {
        "enfermedad" : enfermedad_id,
        "fecha_inicio" : inicio,
        "fecha_fin": hoy
    }
    
    return diccionario_resultado

def encontrar_moda_ubicacion(data_frame):

    # Crear un data frame con solo los id de las ubicaciones
    ubicaciones_data = {'ubicaciones' : data_frame["ubicacion"].tolist()}

    # Convertir lista de ubicaciones en una serie de pandas
    serie_ubicaciones = pd.Series(ubicaciones_data["ubicaciones"])

    # Sacar conteo de busquedas x ubicaciones 
    conteo_ubicaciones = serie_ubicaciones.value_counts()

    # Sacar busquedas con mas ubicaciones
    top_3 = conteo_ubicaciones.head(3)

    # Convertir top 3 a lista
    top_3_lista = top_3.index.to_list()

    # Filtrar data_frame original y encontrar la enfermedad mas buscada x cada ubicacion del top_3
    data_frame_ubicacion_top = data_frame[data_frame['ubicacion'].isin(top_3_lista)]

    # Contar las enfermedades por ubicacion y cantidad
    conteo = data_frame_ubicacion_top.groupby(['ubicacion', 'enfermedad']).size().reset_index(name='cantidad')

    # Obtener la enfermedad mas buscada en cada ubicacion
    enfermedad_mas_buscada = conteo.loc[conteo.groupby('ubicacion')['cantidad'].idxmax()]

    # Convertir el data frame en un diccionario ubicacion, enfermedad, cantidad 
    
    diccionario_resultado = enfermedad_mas_buscada.to_dict(orient="records")

    return diccionario_resultado