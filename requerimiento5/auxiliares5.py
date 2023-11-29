import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def obtener_datos_trimestrales(mm, aa, empresa_busqueda='CENCOSUD S.A.'):
    """
    Obtiene los datos trimestrales de una empresa en un mes y año específicos.
    :param mm: Mes en formato de dos dígitos (03, ..., 12)
    :param aa: Año en formato de cuatro dígitos ('2013', '2014', ..., '2023')
    :param empresa_busqueda: Nombre de la empresa a buscar
    :return: DataFrame con los datos trimestrales de la empresa
    """
    url = f'https://www.cmfchile.cl/institucional/mercados/novedades_envio_sa_ifrs.php?mm_ifrs={mm}&aa_ifrs={aa}'
    headers = {
        "User-Agent": "Mozilla/5.0 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    time.sleep(5)  # Pausa para prevenir bloqueos por hacer peticiones muy seguidas
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    
    datos = []
    # Encuentra todas las filas de la tabla en la página
    for fila in soup.find_all('tr'):
        columnas = fila.find_all('td')
        # Asegurarse de que la fila tiene la cantidad correcta de columnas
        if len(columnas) == 6:
            # Verificar si la etiqueta <a> existe dentro de las celdas
            enlace_primer_envio = columnas[0].find('a')
            enlace_ultimo_envio = columnas[1].find('a')
            enlace_razon_social = columnas[2].find('a')

            # Si alguna etiqueta <a> no existe, continuar con la siguiente fila
            if not (enlace_primer_envio and enlace_ultimo_envio and enlace_razon_social):
                continue

            fecha_primer_envio = enlace_primer_envio.get_text()
            fecha_ultimo_envio = enlace_ultimo_envio.get_text()
            razon_social = enlace_razon_social.get_text(strip=True)
            
            # Si la razón social coincide con la empresa buscada, añadir los datos al DataFrame
            if empresa_busqueda.lower() == razon_social.lower():
                trimestre_financiero = f'{aa}-{mm}-31' if mm in ['03', '12'] else f'{aa}-{mm}-30'
                datos.append({
                    'Trimestre_Estado_Financiero': trimestre_financiero,
                    'Fecha_Primer_envio': fecha_primer_envio,
                    'Fecha_ultimo_envio': fecha_ultimo_envio
                })
    
    return pd.DataFrame(datos)


def guardar_datos(df, nombre_db='datos_eeff.db', nombre_tabla='FECHAS_EEFF'):
    """
    Guarda los datos de un DataFrame en una base de datos SQL.
    :param df: DataFrame con los datos a guardar
    :param nombre_db: Nombre de la base de datos
    :param nombre_tabla: Nombre de la tabla
    """
    # Verifica si el DataFrame está vacío
    if df.empty:
        print("El DataFrame está vacío. No se guardará en la base de datos.")
        return
    
    # Verifica que las columnas necesarias están en el DataFrame
    columnas_necesarias = ['Trimestre_Estado_Financiero', 'Fecha_Primer_envio', 'Fecha_ultimo_envio']
    for columna in columnas_necesarias:
        if columna not in df.columns:
            print(f"Falta la columna necesaria: {columna}")
            return
    
    # Guardar el DataFrame en una base de datos SQL
    conexion = f'sqlite:///{nombre_db}'
    df.to_sql(nombre_tabla, conexion, if_exists='append', index=False)
