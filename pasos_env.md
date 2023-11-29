# Conda environment

Una vez que tenemos el archivo 'environment.yml' con las dependencias de nuestro proyecto, podemos crear un entorno conda con el siguiente comando:

```bash
conda env create -f environment.yml
```

Esto creará un entorno con el nombre que le hayamos dado en el archivo 'environment.yml' (en este caso 'eae253').

Para activar el entorno, ejecutamos el siguiente comando:

```bash
conda activate eae253
```

Para desactivar el entorno, ejecutamos el siguiente comando:

```bash
conda deactivate
```

Para eliminar el entorno, ejecutamos el siguiente comando:

```bash
conda env remove -n pasos_conda_env
```

# Pipenv environment
Cuando tengamos el archivo 'Pipfile' con las dependencias de nuestro proyecto, podemos crear un entorno pipenv con el siguiente comando:

```bash
pipenv install
```

Esto creará un entorno con el nombre que le hayamos dado en el archivo 'Pipfile' (en este caso 'pasos_pipenv_env').

Para activar el entorno, ejecutamos el siguiente comando:

```bash
pipenv shell
```

Para desactivar el entorno, ejecutamos el siguiente comando:

```bash
exit
```

Para eliminar el entorno, ejecutamos el siguiente comando:

```bash
pipenv --rm
```
