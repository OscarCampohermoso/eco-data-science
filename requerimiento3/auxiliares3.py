import pandas as pd

def obtener_info_bonos(empresa, fecha, data_df):
    """
    Procesa información sobre bonos corporativos y determina la línea disponible de financiamiento.

    :param empresa: Nombre de la empresa.
    :param fecha: Fecha límite en formato "mes año".
    :param data_df: DataFrame con los datos de bonos corporativos.
    :return: DataFrame con el formato requerido.

    Note:
        - La fecha proporcionada no debe ser posterior a la última fecha en el archivo.
        - Los montos se presentan en millones de pesos.
    """
    
    try:
        mes_str, año_str = fecha.split()
        mes_numero = {
            "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6, 
            "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
        }
        
        año = int(año_str)
        mes = mes_numero.get(mes_str.lower())
        if mes is None:
            raise ValueError("El mes proporcionado no es válido.")
        
        # Comprobar si la fecha dada es posterior a la última fecha en el DataFrame
        data_df['Año'] = pd.DatetimeIndex(data_df[" Fecha Inscripción"]).year
        data_df['Mes'] = pd.DatetimeIndex(data_df[" Fecha Inscripción"]).month
        maximo_año = data_df['Año'].max()
        maximo_mes = data_df[data_df['Año'] == maximo_año]['Mes'].max()
        
        if año > maximo_año or (año == maximo_año and mes > maximo_mes):
            raise ValueError("La fecha proporcionada es posterior a la última fecha en el archivo. Por favor, proporciona una fecha válida.")
        
        # Filtrar el DataFrame por el nombre de la empresa
        df_empresa = data_df[(data_df["Sociedad"].str.upper() == empresa.upper()) & 
                                (data_df['Año'] <= año) & 
                                ((data_df['Año'] < año) | (data_df['Mes'] <= mes))]
        
        # Si la empresa no tiene bonos en la fecha dada, retornar un DataFrame vacío con las columnas especificadas
        if df_empresa.empty:
            raise ValueError("La empresa proporcionada no tiene bonos en la fecha dada.")
        
        df_lineas = df_empresa[df_empresa["Tipo Bono\n\nEmisión"] == "Línea"]
        lista_dfs = []
        
        for _, linea in df_lineas.iterrows():
            num_inscripcion = int(linea["Nº Inscripción"])
            monto_inscrito = round(float(linea["Monto Inscrito (miles)"] / 1000), 2)
            df_colocaciones = df_empresa[(df_empresa["Nº Inscripción"] == num_inscripcion) & 
                                            (df_empresa["Tipo Bono\n\nEmisión"] != "Línea")]
            monto_colocado = round(float(df_colocaciones["Valor Nominal Vigente \n(U.Reaj)"].sum() / 1_000_000), 2)
            financiamiento_disponible = max(0.0, monto_inscrito - monto_colocado)
            num_series = df_colocaciones["Serie"].nunique()
            
            df_temp = pd.DataFrame({
                "Número de inscripción": [num_inscripcion],
                "Cantidad de series emitidas": [num_series],
                "Monto original inscrito": [monto_inscrito],
                "Monto colocado a la fecha": [monto_colocado],
                "Saldo / financiamiento disponible": [financiamiento_disponible]
            })
            
            lista_dfs.append(df_temp)
        
        resultado_df = pd.concat(lista_dfs, ignore_index=True)
        
        return resultado_df
    
    except ValueError as ve:
        print(f"Error: {ve}")
        return None
    except KeyError as ke:
        print(f"Error: La clave {ke} no existe.")
        return None
    except Exception as e:
        print(f"Error inesperado: {e}")
        return None