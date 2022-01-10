# General
import pandas as pd
import pickle

# Entrenamiento de modelo
from utils import create_predictors
from skforecast.model_selection import grid_search_forecaster
from skforecast.ForecasterAutoregCustom import ForecasterAutoregCustom
from sklearn.ensemble import RandomForestRegressor

# Lectura de Datos
import requests
import pandas as pd
from datetime import datetime

# MLFlow
import mlflow
import os 
from google.cloud import storage


# Datos 
steps = 36
n_datos_entrenar = 200
path_fichero = 'bitcoin.csv'
path_modelo = 'model.pickle'
uri_mlflow = 'http://104.198.136.57:8080/'
experiment_name = "bictoin_transactions"

# Extraigo la info de Bitcoin
url = 'https://api.blockchain.info/charts/transactions-per-second?timespan=all&sampled=false&metadata=false&cors=true&format=json'
resp = requests.get(url)

bitcoin = pd.DataFrame(resp.json()['values'])

# Concierto las fecha UNIX en timestamp
bitcoin['x'] = [datetime.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S') for x in bitcoin['x']]
bitcoin['x'] = pd.to_datetime(bitcoin['x'])

# Doy nombre a las columnas
bitcoin.columns = ['date', 'transactions']

# Guardo el fichero en csv
bitcoin.to_csv(path_fichero, index = False)

# Leo los datos
datos = pd.read_csv(path_fichero)

# Fijo el tipo de datos
datos['date'] = pd.to_datetime(datos['date'])
datos['date'] = datos['date'].dt.round('H')

datos_agrupados = datos\
  .groupby('date')\
  .sum()\
  .reset_index()

# Pongo bien los datos
datos_agrupados = datos_agrupados.set_index('date')
datos_agrupados = datos_agrupados['transactions']

# Split entre train y test
datos_train = datos_agrupados[ -n_datos_entrenar:-steps]
datos_test  = datos_agrupados[-steps:]

# Grid search de hiperparámetros
forecaster_rf = ForecasterAutoregCustom(
                    regressor      = RandomForestRegressor(random_state=123),
                    fun_predictors = create_predictors,
                    window_size    = 20
                )

# Hiperparámetros del regresor
param_grid = {
  'n_estimators': [100, 500],
  'max_depth': [3, 5, 10]
}

resultados_grid = grid_search_forecaster(
                        forecaster  = forecaster_rf,
                        y           = datos_train,
                        param_grid  = param_grid,
                        steps       = 10,
                        method      = 'cv',
                        metric      = 'mean_squared_error',
                        initial_train_size    = int(len(datos_train)*0.5),
                        allow_incomplete_fold = True,
                        return_best = True,
                        verbose     = False
                    )

# Subo los resultados a MLFlow para hacer tracking de 
service_account = 'service_account.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS']='service_account.json'
client = storage.Client

# Me conecto a MLFlow
mlflow.set_tracking_uri(uri_mlflow)  

# Creo el experimento si no está creado y lo fijo
if not mlflow.get_experiment_by_name(experiment_name):
    mlflow.create_experiment(name=experiment_name)

mlflow.set_experiment(experiment_name)

# Haog el log de los parámetros en MLFlow
for i in range(resultados_grid.shape[0]):
   with mlflow.start_run():
      mlflow.log_params(resultados_grid['params'][i])
      mlflow.log_metric('mean_squared_error', resultados_grid['metric'][i])
      
      # Si coincide con el mejor modelo, hago logging del modelo
      if resultados_grid['metric'][i] == resultados_grid['metric'].min():
         fecha = datetime.now().strftime('%Y%m%d%H%M%S')
         mlflow.sklearn.log_model(resultados_grid, f'{fecha}_autoregressive_forecaster')

# Guardo el modelo en local
ultima_fecha_entrenamiento = datos_test.index[-1].strftime('%Y-%m-%d %H:%M:%S')
pickle.dump(ultima_fecha_entrenamiento, open('ultima_fecha_entrenamiento.pickle', 'wb'))
pickle.dump(forecaster_rf, open(path_modelo, 'wb'))