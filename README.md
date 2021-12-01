# Ejemplo funcionamiento MLOps
En este repositorio guardo el código para explicar, de forma sencilla, cómo es un proceso de MLOps sencillo. 

Para ello, he creado un modelo de series temporales que intenta predecir el número de transacciones de Bitcoin que hay cada hora. 

El ejercicio de MLOps consiste en: 

1. Crear un modelo de ML de series temporales que prediga el número de transacciones de bitcoin por hora. La creación del modelo se realiza en el fichero `model_train.py`. 

2. Conectar el repositorio con un entorno cloud (Google Cloud) para hacer el deployment contínuo del modeo con cada push del repositorio, a modo de MLOps básico.  

3. Avanzar en nuestro MLOps, para lo cual vamos a: 
    1. Crear una automatización usando Github Actions que nos permita tener los valores reales y así poder calcular el error de las predicciones. 
    
    2. Disponer de una base de datos que permita incluir la información de predicciones y datos reales para así poder visualizar la evolución de la capacidad predictiva del modelo. Esta visualización se ha creado usando `streamlit` y se encuentra en el fichero `app_mae.py`.

## Funcionamiento
 Entrena el modelo predictivo ejecutando el fichero `model_train.py`. Esto generará un nuevo modelo entrenado, llamado `model.pickle`. 

 Una vez se haya creado el modelo, haz el push a Github. Automáticamente el modelo se compilará en una API con el script `app.py` el Dockerfile y será publicado en Google Cloud Run. 
