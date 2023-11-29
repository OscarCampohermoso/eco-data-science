"""
a. Llame a esa función “directores”.
b. La función debe tomar como input un string, correspondiente a la fecha, en
formato “DD-MM-YYYY”.
c. La función debe entregar como output una lista, con los RUTs de los directores
que estaban vigentes en la fecha dada.
d. Dicha función debe guardarse en un archivo “.py”, para poder ser llamada desde
otros códigos. Llame a dicho archivo “auxiliares1.py”
e. Esta función debe hacerse cargo de la lectura de la base de datos de directores.
f. La función podría ser utilizada por otros miembros del equipo, por lo que debe
procurar que funcione de manera “robusta”. Se recomienda que la función
“alerte” al usuario frente a un uso errado de la misma. Para lo anterior, se
recomienda que en caso de detectar algún error, la función retorne una lista
donde el primer elemento de la lista sea un texto que explique el error.
* No se puede usar librerías externas
"""

def directores(fecha):
    lista = []
    try:
        if not fecha or len(fecha) != 10 or fecha[2] != "-" or fecha[5] != "-" or not fecha[:2].isdigit() or not fecha[3:5].isdigit() or not fecha[6:].isdigit():
            lista.append("Error: Incorrect date format. It should be 'DD-MM-YYYY'.")
            return lista
        dia, mes, anio = map(int, fecha.split("-"))
        with open('directores2.csv', 'r') as file:
            header = True
            for line in file:
                if header:
                    header = False
                    continue

                line = line.strip().split(";")
                dia_ini, mes_ini, anio_ini = map(int, line[3].split('/'))
                anio_ini += 2000
                
                if line[4]:  # Si la fecha término no está vacía
                    dia_fin, mes_fin, anio_fin = map(int, line[4].split('/'))
                    anio_fin += 2000
                else:
                    dia_fin, mes_fin, anio_fin = 31, 12, 9999  # Establecer un valor predeterminado para fechas vacías
                    
                if (anio > anio_ini or (anio == anio_ini and mes > mes_ini) or (anio == anio_ini and mes == mes_ini and dia >= dia_ini)) and \
                    (anio < anio_fin or (anio == anio_fin and mes < mes_fin) or (anio == anio_fin and mes == mes_fin and dia <= dia_fin)):
                    lista.append(formato_rut(line[0]))
            return lista
    except Exception as e:
        lista.append("Error: {}".format(e))
        return lista

def formato_rut(rut):
    try:
        rut = rut.split("-")
        rut = rut[0]
        rut = rut.replace(".", "")
        rut = int(rut)
        return rut
    except Exception as e:
        return "Error: {}".format(e)