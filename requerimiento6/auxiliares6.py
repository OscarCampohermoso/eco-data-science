import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime, timedelta
from auxiliares4 import obtener_precios, calcular_rentabilidad, obtener_ticker


def calcular_run_up(r_a, r_b):
    """ 
    Calcula el ratio de run up de la siguiente manera: r_a / r_b.
    
    param r_a: Retorno del precio entre 1 día antes y 30 días antes de la fecha de EEFF.
    param r_b: Retorno del precio entre 2 días después y 30 días antes de la fecha de EEFF.
    return: Ratio de run up.
    """

    try:
        # Si r_b es 0, retornar NaN
        return r_a / r_b if r_b != 0 else np.nan
    except ZeroDivisionError:
        return np.nan


def calcular_retornos(conn, ticker, fecha_eeff):
    """ 
    Calcula el retorno del precio entre 1 día antes y 30 días antes de la fecha de EEFF, y entre 2 días después y 30 días antes de la fecha de EEFF.

    param conn: Conexión a la base de datos.
    param ticker: Ticker de la empresa.
    param fecha_eeff: Fecha de EEFF.
    return: Tupla con los retornos r_a y r_b.
    """

    # Obtener los precios de la empresa 30 días antes, 1 día antes y 2 días después de la fecha de EEFF
    fecha_30_dias_antes = fecha_eeff - timedelta(days=30)
    fecha_1_dia_antes = fecha_eeff - timedelta(days=1)
    fecha_2_dias_despues = fecha_eeff + timedelta(days=2)

    # Obtener los precios de la empresa en las fechas especificadas 
    precio_30_dias_antes = obtener_precios(
        conn, fecha_30_dias_antes.strftime('%Y-%m-%d'), [ticker]).get(ticker)
    precio_1_dia_antes = obtener_precios(
        conn, fecha_1_dia_antes.strftime('%Y-%m-%d'), [ticker]).get(ticker)
    precio_2_dias_despues = obtener_precios(
        conn, fecha_2_dias_despues.strftime('%Y-%m-%d'), [ticker]).get(ticker)

    # Calcular los retornos r_a y r_b
    r_a = calcular_rentabilidad(precio_1_dia_antes, precio_30_dias_antes)
    r_b = calcular_rentabilidad(precio_2_dias_despues, precio_30_dias_antes)

    return r_a, r_b


def analizar_datos_eeff(conn_precios, conn_eeff, ticker):
    """
    Analiza los datos de EEFF y precios de una empresa y calcula el ratio de run up para cada fecha de EEFF.

    :param conn_precios: Conexión a la base de datos de precios.
    :param conn_eeff: Conexión a la base de datos de EEFF.
    :param ticker: Ticker de la empresa.
    :return: DataFrame con los resultados y DataFrame con la fecha de mayor run up.
    """

    # Obtener las fechas de EEFF de la empresa
    df_fechas_eeff = pd.read_sql('SELECT * FROM FECHAS_EEFF', conn_eeff)
    print(df_fechas_eeff)

    # Convertir las fechas a datetime
    df_fechas_eeff['Fecha_Primer_envio'] = pd.to_datetime(
        df_fechas_eeff['Fecha_Primer_envio'], format='%d/%m/%Y %H:%M')

    # Filtrar las fechas de EEFF de los últimos 5 años
    five_years_ago = datetime.now() - timedelta(days=5*365)
    df_fechas_eeff = df_fechas_eeff[df_fechas_eeff['Fecha_Primer_envio']
                                    >= five_years_ago]

    resultados = []

    # Iterar sobre las fechas de EEFF
    for _, fila in df_fechas_eeff.iterrows():
        fecha_eeff = fila['Fecha_Primer_envio']
        año, trimestre, _ = fila['Trimestre_Estado_Financiero'].split('-')
        r_a, r_b = calcular_retornos(conn_precios, obtener_ticker(conn_precios, ticker), fecha_eeff)
        run_up = calcular_run_up(r_a, r_b)
        resultados.append({
            'Fecha_EEFF': fecha_eeff.strftime('%Y-%m-%d'),
            'Retorno_r_a': r_a,
            'Retorno_r_b': r_b,
            'Run_up': run_up,
            'Año': año,
            'Trimestre': trimestre,
        })

    # Crear un DataFrame con los resultados
    df_resultados = pd.DataFrame(resultados)

    # Filtrar los resultados positivos
    df_resultados_positivos = df_resultados[df_resultados['Retorno_r_b'] > 0]

    # Obtener la fecha de mayor run up
    fecha_max_run_up = df_resultados_positivos.loc[df_resultados_positivos['Run_up'].idxmax()]

    # Retornar los resultados y la fecha de mayor run up
    return df_resultados, pd.DataFrame(fecha_max_run_up)
