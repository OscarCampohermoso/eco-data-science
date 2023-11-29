def etl(carteras, identificacion):
    """
    Procesa información de carteras y identificación, convirtiendo montos a millones de dólares.
    
    :param carteras: objeto lector de líneas para archivo de carteras.
    :param identificacion: objeto lector de líneas para archivo de identificación.
    :return: lista de listas con información procesada.
    
    Note:
        - Se asume que las monedas pueden ser dólares (PROM) o pesos chilenos ($$).
        - Los montos se convierten a millones de dólares.
    """
    # Valores estáticos de monedas
    dolar = 827.84
    #uf = 36049.05
    
    # Leer y procesar la información del archivo identificacion.txt
    monedas_fondos = {}
    identificacion.readline() # Ignorar la primera línea de encabezado
    for linea in identificacion:
        try:
            partes = linea.strip().split(";")
            run_fondo = partes[2]
            moneda = partes[10]
            monedas_fondos[run_fondo] = moneda
        except IndexError:
            print(f"Error al procesar la línea en identificación: {linea}")
    
    carteras.readline()  # Ignorar la primera línea de encabezado
    datos_procesados = []
    for linea in carteras:
        try:
            partes = linea.strip().split(";")
            run_fondo = partes[0]
            moneda_fondo = monedas_fondos.get(run_fondo, "$$")
            monto = float(partes[19])  # Valorización del cierre

            # Convertir a dólares si está en pesos chilenos
            if moneda_fondo == "$$":
                monto = monto / dolar

            # Convertir a millones de dólares
            monto = monto / 1000

            # Reemplazar el monto original con el monto convertido
            partes[19] = str(monto)
            datos_procesados.append(partes)
        except (IndexError, ValueError) as e:
            print(f"Error {e} al procesar la línea en carteras: {linea}")
    
    return datos_procesados


def monto_directo(run, instrumento, datos):
    """"
    Calcula la inversión directa de un fondo mutuo en un instrumento.

    param run: RUN del fondo mutuo.
    param instrumento: Nemotécnico del instrumento.
    param datos: Lista de listas con los datos.
    return: Inversión directa del fondo mutuo en el instrumento.
    """
    # Inicializar el monto total en 0
    monto_total = 0.0
    
    # Iterar sobre los datos para encontrar las inversiones del RUN especificado
    for linea in datos:
        run_fondo = linea[0]
        nemotecnico = linea[2]
        
        # Si encontramos el RUN y el nemotécnico especificados, sumamos el monto al total
        if run_fondo == run and nemotecnico == instrumento:
            # Tomamos el monto desde la posición 19
            monto = float(linea[19])
            monto_total += monto
    
    return monto_total


def total_run(run, datos):
    """
    Calcula el monto total invertido por un fondo mutuo.

    :param run: RUN del fondo mutuo.
    :param datos: Lista de listas con los datos.
    :return: Monto total invertido por el fondo mutuo.
    """
    # Inicializar el monto total en 0
    monto_total = 0.0
    
    # Iterar sobre los datos para encontrar las inversiones del RUN especificado
    for linea in datos:
        run_fondo = linea[0]

        # Si encontramos el RUN y el nemotécnico especificados, sumamos el monto al total
        if run_fondo == run:
            # Tomamos el monto desde la posición 19
            monto = float(linea[19])
            monto_total += monto
    
    return monto_total


def rut_exists_in_data(rut, datos):
    """"
    Verifica si un rut existe en los datos.

    param rut: RUN del fondo mutuo.
    param datos: Lista de listas con los datos.
    return: True si el rut existe en los datos, False en caso contrario.
    """
    for linea in datos:
        run_fondo_invertido = linea[0]
        if run_fondo_invertido  == rut:
            return True
    return False


def monto_total(run, instrumento, datos, runs_visitados=None):
    """
    Calcula la inversión total de un fondo mutuo en un instrumento.

    :param run: RUN del fondo mutuo.
    :param instrumento: Nemotécnico del instrumento.
    :param datos: Lista de listas con los datos.
    :param runs_visitados: Lista de RUNs visitados.
    :return: Inversión total del fondo mutuo en el instrumento.
    """
    if runs_visitados is None:
        runs_visitados = []

    # Si el run ya ha sido visitado, retornamos 0 para evitar la recursión infinita
    if run in runs_visitados:
        return 0

    runs_visitados.append(run)

    monto_directo_total = monto_directo(run, instrumento, datos)
    monto_indirecto_total = 0

    for linea in datos:
        run_actual = linea[0]
        rut = linea[3]
        monto = float(linea[19])
        tipo_inv = linea[6]

        # Si el run actual coincide y el tipo de inversión es 'CMF'
        if run_actual == run and tipo_inv == 'CMF':
            # Verificamos si el rut está en los datos
            if rut_exists_in_data(rut, datos):
                monto_total_rut = total_run(rut, datos)
                if monto_total_rut != 0:
                    factor = monto / monto_total_rut
                    monto_indirecto_total += factor * monto_total(rut, instrumento, datos, runs_visitados)
                    print(f"run: {run}, rut: {rut}, monto: {monto}, monto_total_rut: {monto_total_rut}, factor: {factor}, monto_indirecto_total: {monto_indirecto_total}")
    
    return monto_directo_total + monto_indirecto_total


def hhindex(lista_montos):
    """
    Calcula el índice de Herfindahl-Hirschman (HHI) para una lista de montos.

    :param lista_montos: Lista de montos.
    :return: Índice de Herfindahl-Hirschman (HHI).
    """
    # Primero, calculamos el monto total del mercado
    monto_total = sum(lista_montos)
    
    # Si el monto total es 0, retornamos 0 para evitar división por cero
    if monto_total == 0:
        return 0
    
    # Calculamos las cuotas de mercado para cada monto y las elevamos al cuadrado
    cuotas_cuadradas = [(monto / monto_total) ** 2 for monto in lista_montos]
    
    # Sumamos todas las cuotas al cuadrado para obtener el HHI
    hhi = sum(cuotas_cuadradas)
    
    return hhi
