# Requerimiento #3 - Información sobre Bonos

En su tercera semana de trabajo, su jefe le pide ayuda con el proceso de planificación financiera de la empresa, por lo que le solicita información sobre los bonos emitidos por la empresa. Además, le vuelve a hacer uno de los requerimientos del pasado...

## El proceso de planificación financiera
Le explican que, en el contexto de la planificación financiera de la empresa, todos los meses el área de Finanzas y Contabilidad realiza un proceso manual, que les permite analizar los bonos que la empresa ha emitido, para conocer la línea disponible de financiamiento de la empresa a través de posibles nuevas emisiones de bonos.

El procedimiento involucra acceder a la información de las emisiones de bonos vigentes de la empresa (que se encuentra en la web de la CMF), donde se puede conocer las líneas de emisión aprobadas, y también el monto ya colocado para cada línea.

## El Requerimiento

Al partir la siguiente jornada, el equipo de Transformación Digital -donde usted trabaja- recibe un email de su jefe con lo siguiente:
```
Buenos días,
Para el próximo Comité Financiero debemos llevar información sobre las líneas de bonos vigentes. Por favor buscar en la información de la CMF y enviar un Excel con lo siguiente:
- Número de inscripción
- Cantidad de series emitidas para cada inscripción
- Monto original inscrito
- Monto colocado a la fecha
- Saldo / financiamiento disponible (si es negativo, reemplazar por 0)
Por favor presentar los montos en millones de pesos.
Aprovecho de pedirles que preparen respuesta para la CMF, sobre los directores de la empresa al 30 de septiembre de 2023. Recordar el formato que nos pide la CMF.
```
## Los Datos
Uno se sus colegas le comenta que la información de estado de colocaciones y deuda vigente se encuentra en el siguiente link en la CMF:
https://www.cmfchile.cl/portal/estadisticas/617/w3-propertyvalue-20153.html (que en este caso es el archivo .xlsx que te pase)

Asimismo, le da alguna información adicional sobre ese archivo:
- Cada inscripción de bonos tiene asociado un código, en el campo “No Inscripción”. Esta
es la identificación de una línea de bonos.
- Las filas cuyo campo “Tipo Bono Emisión” están identificadas como “Línea”, se refiere a
la línea original inscrita por la empresa.
- Las empresas pueden (o no) realizar emisiones con cargo a una línea, según sean sus
necesidades de financiamiento en el tiempo. Cuando una empresa realiza una emisión,
se le llama “colocación”.
- Asimismo, un bono puede ser emitido en una serie, o en varias series. Esto está
recogido en el campo “Serie”.
- Las colocaciones de bonos pueden tener condiciones diferentes a las líneas
originalmente inscritas. Por ejemplo, un bono podría haberse inscrito en UF, pero las
emisiones pueden ser en UF y en pesos (con distintas series).
- El financiamiento disponible correspondería a la diferencia entre el monto inscrito y el
monto colocado, para cada línea de bonos que la empresa haya inscrito.
- Para este ejercicio, se asumirá que:
- El campo “Monto Inscrito (miles)”, para la fila “Línea”, es el máximo monto a colocar para ese número de inscripción.
- El campo “Valor Nominal Inicial (U.Reaj)”, es el monto efectivamente colocado. Si ese campo no tiene valores, se asumirá que la emisión respectiva no fue colocada.

## El Código
Para responder el requerimiento, le recomienda lo siguiente:
- Al descargar el archivo Excel desde la CMF, se sugiere cambiar el nombre del archivo, para que corresponda a la fecha de la información (por ej, “202308.xlsx”, para agosto 2023).
- Escribir una función que tome como inputs el nombre de una empresa (tal como aparecen en el archivo de colocaciones y deuda vigente), y una fecha (por ej, “agosto 2023”), y le entregue un DataFrame con el formato requerido.
- Esta función debe guardarse en un archivo “auxiliares3.py”
- La función debería poder tomar otras fechas y otros nombres de empresas.
- En caso de que se le solicite una fecha para la cual no se ha descargado la información, la función debería alertar al usuario de la situación y retornar “None”.
- En caso de que una empresa no tenga bonos, la función debería entregar un DataFrame “vacío”, con los mismos nombres de columnas que el caso en que sí tiene bonos.
- Posteriormente, el DataFrame que entregue la función debe exportarse a Excel. Llame a dicho archivo Excel “req3.xlsx”.
- En cuanto al requerimiento de los directores, le recomienda volver a bajar la información de directores históricos, ya que podrían haber modificaciones desde la última revisión. Llame a dicho archivo “req1.txt”, con el mismo formato solicitado anteriormente.
## La Entrega
Fecha de entrega: viernes 20 de octubre (hasta las 23.59hrs).
Entregables:
- Archivo Py: “auxiliares3.py”
- Archivo Excel: “req3.xlsx”
- Archivo txt: “req1.txt”
Todos los entregables deben estar en una sub-carpeta de la carpeta compartida llamada “requerimiento3”.
