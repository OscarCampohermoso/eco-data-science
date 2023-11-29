import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sqlite3
import requests


def obtener_valor_dolar_observado(fecha):
    """
    Obtiene el valor observado del dólar para una fecha específica.

    :param fecha: Fecha en formato 'YYYY-MM-DD' para la consulta.
    :return: Valor observado del dólar o NaN si no se puede obtener.
    """
    user = '1090208'
    pwd = 'cyTG5VWgjynj'
    serie = 'F073.TCO.PRE.Z.D'

    url = f"https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx?" + \
        f"user={user}&pass={pwd}&lastdate={fecha}&" + \
        f"timeseries={serie}&function=GetSeries"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()["Series"]["Obs"]
        df = pd.DataFrame(data)
        # La fecha de la API viene en formato 'DD-MM-YYYY', convertimos a datetime con ese formato.
        df['indexDate'] = pd.to_datetime(df['indexDateString'], dayfirst=True)

        # Ordenamos por fecha en orden descendente
        df.sort_values(by='indexDate', ascending=False, inplace=True)

        # Buscamos el último valor disponible que no sea NaN
        last_available_value = df.loc[df['value'].notna(), 'value'].iloc[0]
        # print(f"Último valor disponible: {last_available_value}")

        return last_available_value
    else:
        return np.nan


def obtener_ultima_fecha_disponible(conn, fecha_referencia):
    """
    Obtiene la última fecha disponible en la base de datos de precios hasta una fecha de referencia.

    :param conn: Conexión a la base de datos.
    :param fecha_referencia: Fecha de referencia en formato 'YYYY-MM-DD'.
    :return: Última fecha disponible o None si no se encuentra ninguna antes de la fecha de referencia.
    """
    while True:
        query = f"SELECT MAX(fecha) as ultima_fecha FROM PRECIOS WHERE fecha <= '{fecha_referencia}'"
        ultima_fecha = pd.read_sql_query(query, conn)
        if not ultima_fecha.empty and not pd.isna(ultima_fecha['ultima_fecha'].iloc[0]):
            return ultima_fecha['ultima_fecha'].iloc[0]
        fecha_referencia = (pd.to_datetime(fecha_referencia) -
                            pd.Timedelta(days=1)).strftime('%Y-%m-%d')


def obtener_precios(conn, fecha, tickers):
    """
    Obtiene los precios de una lista de tickers en una fecha específica.

    :param conn: Conexión a la base de datos.
    :param fecha: Fecha en formato 'YYYY-MM-DD'.
    :param tickers: Lista de tickers de los instrumentos.
    :return: Diccionario de precios con tickers como clave y valores como valores.
    """
    precios = {}
    for ticker in tickers:
        while True:
            query = f"SELECT valor FROM PRECIOS WHERE ticker = '{ticker}' AND fecha = '{fecha}' LIMIT 1;"
            resultado = pd.read_sql_query(query, conn)
            if not resultado.empty and not pd.isna(resultado['valor'].iloc[0]):
                precios[ticker] = resultado['valor'].iloc[0]
                break
            fecha = (pd.to_datetime(fecha) -
                     pd.Timedelta(days=1)).strftime('%Y-%m-%d')
    return precios


def obtener_ticker(conn, identificador):
    """
    Obtiene el ticker correspondiente a un identificador (nemo o ticker).

    :param conn: Conexión a la base de datos.
    :param identificador: Nemo o ticker del instrumento.
    :return: Ticker del instrumento o None si no se encuentra.
    """
    # Primero, intentamos buscar por nemo
    query_nemo = f"SELECT ticker FROM TICKERNEMO WHERE nemo = '{identificador}' LIMIT 1;"
    resultado_nemo = pd.read_sql_query(query_nemo, conn)
    if not resultado_nemo.empty:
        return resultado_nemo['ticker'].iloc[0]
    else:
        # Si no se encuentra el nemo, buscamos por ticker
        query_ticker = f"SELECT ticker FROM TICKERNEMO WHERE ticker = '{identificador}' LIMIT 1;"
        resultado_ticker = pd.read_sql_query(query_ticker, conn)
        if not resultado_ticker.empty:
            return resultado_ticker['ticker'].iloc[0]
    return None


def calcular_rentabilidad(precio_final, precio_inicial):
    """
    Calcula la rentabilidad entre dos precios.

    :param precio_final: Precio final.
    :param precio_inicial: Precio inicial.
    :return: Rentabilidad en porcentaje o np.nan si no se puede calcular.
    """
    try:
        if precio_final is not None:
            precio_final = float(precio_final)
        else:
            precio_final = np.nan

        if precio_inicial is not None:
            precio_inicial = float(precio_inicial)
        else:
            precio_inicial = np.nan
    except (ValueError, TypeError):
        return np.nan
    if not np.isnan(precio_final) and not np.isnan(precio_inicial):
        return (precio_final / precio_inicial - 1) * 100
    else:
        return np.nan


def anualizar_rentabilidad(rentabilidad, dias):
    """
    Calcula la rentabilidad anualizada a partir de una rentabilidad diaria.

    :param rentabilidad: Rentabilidad diaria en porcentaje.
    :param dias: Número de días de referencia para la rentabilidad diaria.
    :return: Rentabilidad anualizada en porcentaje o np.nan si no se puede calcular.
    """
    if np.isnan(rentabilidad) or dias == 0:
        # Si la rentabilidad no es un número o los días son 0, retorno NaN para evitar errores
        return np.nan

    tasa = rentabilidad / 100  # Convertir la rentabilidad a tasa decimal
    tasa_anualizada = (1 + tasa) ** (365 / dias) - 1
    return tasa_anualizada * 100


def calcular_rentabilidades(conn, fecha_referencia, nemos):
    """
    Calcula las rentabilidades de instrumentos financieros en diferentes plazos.

    :param conn: Conexión a la base de datos.
    :param fecha_referencia: Fecha de referencia en formato 'YYYY-MM-DD'.
    :param nemos: Lista de nemos de instrumentos financieros.
    :return: DataFrame con las rentabilidades calculadas.
    """
    fecha_referencia_dt = datetime.strptime(fecha_referencia, '%Y-%m-%d')
    fecha_inicio_año = datetime(fecha_referencia_dt.year, 1, 1)
    fecha_anterior_dt = fecha_referencia_dt - timedelta(days=1)
    fecha_mes_anterior_dt = fecha_referencia_dt - timedelta(days=30)
    fecha_un_año_anterior = fecha_referencia_dt - timedelta(days=365)
    fecha_cinco_años_anterior = fecha_referencia_dt - timedelta(days=365 * 5)

    df_rentabilidades = pd.DataFrame(columns=['Instrumento', 'Ult. Precio', 'Rent 1d',
                                              'Rent 1m', 'Rent ytd*', 'Rent 1y*', 'Rent 5y*'])

    for nemo in nemos:
        # Obtenemos el ticker correspondiente al nemo
        ticker = obtener_ticker(conn, nemo)
        if ticker:
            precio_final = obtener_precios(conn, fecha_referencia_dt.strftime(
                '%Y-%m-%d'), [ticker]).get(ticker, np.nan)
            precio_inicial = obtener_precios(conn, fecha_anterior_dt.strftime(
                '%Y-%m-%d'), [ticker]).get(ticker, np.nan)
            rent_1d = calcular_rentabilidad(precio_final, precio_inicial)
            precio_inicial_mes = obtener_precios(
                conn, (fecha_referencia_dt - timedelta(days=30)).strftime('%Y-%m-%d'), [ticker]).get(ticker, np.nan)
            rent_1m = calcular_rentabilidad(precio_final, precio_inicial_mes)
            precio_inicial_ytd = obtener_precios(
                conn, fecha_inicio_año.strftime('%Y-%m-%d'), [ticker]).get(ticker, np.nan)
            rent_ytd = calcular_rentabilidad(precio_final, precio_inicial_ytd)
            rent_ytd_anualizada = anualizar_rentabilidad(
                rent_ytd, (fecha_referencia_dt - fecha_inicio_año).days)

            precio_inicial_1y = obtener_precios(conn, (fecha_referencia_dt - timedelta(
                days=365)).strftime('%Y-%m-%d'), [ticker]).get(ticker, np.nan)
            rent_1y = calcular_rentabilidad(precio_final, precio_inicial_1y)
            rent_1y_anualizada = anualizar_rentabilidad(rent_1y, 365)

            precio_inicial_5y = obtener_precios(conn, (fecha_referencia_dt - timedelta(
                days=365*5)).strftime('%Y-%m-%d'), [ticker]).get(ticker, np.nan)
            rent_5y = calcular_rentabilidad(precio_final, precio_inicial_5y)
            rent_5y_anualizada = anualizar_rentabilidad(rent_5y, 365*5)

            df_rentabilidades.loc[len(df_rentabilidades)] = [nemo, precio_final,
                                                             f'{rent_1d:.2f}%', f'{rent_1m:.2f}%',
                                                             f'{rent_ytd_anualizada:.2f}%', f'{rent_1y_anualizada:.2f}%',
                                                             f'{rent_5y_anualizada:.2f}%']

    # IPSA
    precio_ipsa_fecha_referencia = obtener_precios(conn, fecha_referencia_dt.strftime(
        '%Y-%m-%d'), ['IPSA Index']).get('IPSA Index', np.nan)
    rent_ipsa_1d = calcular_rentabilidad(precio_ipsa_fecha_referencia, obtener_precios(
        conn, fecha_anterior_dt.strftime('%Y-%m-%d'), ['IPSA Index']).get('IPSA Index', np.nan))
    rent_ipsa_1m = calcular_rentabilidad(precio_ipsa_fecha_referencia, obtener_precios(
        conn, fecha_mes_anterior_dt.strftime('%Y-%m-%d'), ['IPSA Index']).get('IPSA Index', np.nan))
    rent_ipsa_ytd = calcular_rentabilidad(precio_ipsa_fecha_referencia, obtener_precios(
        conn, fecha_inicio_año.strftime('%Y-%m-%d'), ['IPSA Index']).get('IPSA Index', np.nan))
    rent_ipsa_1y = calcular_rentabilidad(precio_ipsa_fecha_referencia, obtener_precios(
        conn, fecha_un_año_anterior.strftime('%Y-%m-%d'), ['IPSA Index']).get('IPSA Index', np.nan))
    rent_ipsa_5y = calcular_rentabilidad(precio_ipsa_fecha_referencia, obtener_precios(
        conn, fecha_cinco_años_anterior.strftime('%Y-%m-%d'), ['IPSA Index']).get('IPSA Index', np.nan))
    rent_ipsa_1y_anualizada = anualizar_rentabilidad(rent_ipsa_1y, 365)
    rent_ipsa_5y_anualizada = anualizar_rentabilidad(rent_ipsa_5y, 365 * 5)

    df_ipsa = pd.DataFrame({
        'Instrumento': ['IPSA'],
        'Ult. Precio': [precio_ipsa_fecha_referencia],
        'Rent 1d': [f'{rent_ipsa_1d:.2f}%'],
        'Rent 1m': [f'{rent_ipsa_1m:.2f}%'],
        'Rent ytd*': [f'{rent_ipsa_ytd:.2f}%'],
        'Rent 1y*': [f'{rent_ipsa_1y_anualizada:.2f}%'],
        'Rent 5y*': [f'{rent_ipsa_5y_anualizada:.2f}%'],
    })

    # Dólar
    precio_dolar = obtener_valor_dolar_observado(fecha_referencia)
    rent_dolar_1d = calcular_rentabilidad(
        precio_dolar, obtener_valor_dolar_observado(fecha_anterior_dt.strftime('%Y-%m-%d')))
    rent_dolar_1m = calcular_rentabilidad(precio_dolar, obtener_valor_dolar_observado(
        fecha_mes_anterior_dt.strftime('%Y-%m-%d')))
    rent_dolar_ytd = calcular_rentabilidad(
        precio_dolar, obtener_valor_dolar_observado(fecha_inicio_año.strftime('%Y-%m-%d')))
    rent_dolar_1y = calcular_rentabilidad(precio_dolar, obtener_valor_dolar_observado(
        fecha_un_año_anterior.strftime('%Y-%m-%d')))
    rent_dolar_5y = calcular_rentabilidad(precio_dolar, obtener_valor_dolar_observado(
        fecha_cinco_años_anterior.strftime('%Y-%m-%d')))
    rent_dolar_1y_anualizada = anualizar_rentabilidad(rent_dolar_1y, 365)
    rent_dolar_5y_anualizada = anualizar_rentabilidad(rent_dolar_5y, 365 * 5)

    df_dolar = pd.DataFrame({
        'Instrumento': ['Dólar'],
        'Ult. Precio': [precio_dolar],
        'Rent 1d': [f'{rent_dolar_1d:.2f}%'],
        'Rent 1m': [f'{rent_dolar_1m:.2f}%'],
        'Rent ytd*': [f'{rent_dolar_ytd:.2f}%'],
        'Rent 1y*': [f'{rent_dolar_1y_anualizada:.2f}%'],
        'Rent 5y*': [f'{rent_dolar_5y_anualizada:.2f}%'],
    })

    df_fecha_referencia = pd.DataFrame({
        'Instrumento': ['Fecha de referencia:'],
        'Ult. Precio': [fecha_referencia],
        'Rent 1d': [''],
        'Rent 1m': [''],
        'Rent ytd*': [''],
        'Rent 1y*': [''],
        'Rent 5y*': [''],
    })

    # Concatenando los DataFrames
    df_rentabilidades = pd.concat(
        [df_rentabilidades, df_ipsa, df_dolar, df_fecha_referencia], ignore_index=True)

    return df_rentabilidades
