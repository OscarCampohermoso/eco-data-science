SELECT COUNT(*)
FROM NOTAS;

-- numero de notas por curso
SELECT  Curso, COUNT(*) AS NNOTAS
FROM NOTAS
GROUP BY Curso;

-- otra froma de explorar los datos
SELECT DISTINCT Evaluacion 
FROM NOTAS;

-- BASE ANALITICA V1
SELECT 
    Curso, 
    SUM(Nota * Ponderacion)/SUM(Ponderacion) AS NOTA_ACTUAL,
    SUM(Ponderacion) AS PORC_ACUM,
    MAX((4 - (SUM(Nota * Ponderacion)/SUM(Ponderacion) * SUM(Ponderacion)))/(1 - SUM(Ponderacion)), 1) AS NOTA_NECESARIA
FROM NOTAS
GROUP BY Curso;

-- BASE ANALITICA V2
SELECT 
    Curso, 
    ROUND(NOTA_ACTUAL, 2), 
    ROUND(PORC_ACUM, 2), 
    ROUND(MAX(((5.5 - NOTA_ACTUAL * PORC_ACUM) / (1 - PORC_ACUM)), 1), 2) AS "NOTA NECESARIA"
FROM (
    SELECT 
        Curso, 
        SUM(Nota * Ponderacion)/SUM(Ponderacion) AS NOTA_ACTUAL,
        SUM(Ponderacion) AS PORC_ACUM
    FROM NOTAS
    GROUP BY Curso
);


-- BASE ANALITICA V3

WITH INTERMEDIA AS (
	SELECT 
        Curso, 
        SUM(Nota * Ponderacion)/SUM(Ponderacion) AS NOTA_ACTUAL,
        SUM(Ponderacion) AS PORC_ACUM
    FROM NOTAS
    GROUP BY Curso
)
SELECT 
    Curso, 
    ROUND(NOTA_ACTUAL, 2), 
    ROUND(PORC_ACUM, 2), 
    ROUND(MAX(((4 - NOTA_ACTUAL * PORC_ACUM) / (1 - PORC_ACUM)), 1), 2) AS "NOTA NECESARIA"
FROM INTERMEDIA;