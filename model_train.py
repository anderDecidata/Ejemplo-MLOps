import pandas as pd
import pickle
from sklearn.ensemble import RandomForestRegressor

from utils import create_predictors
from skforecast.model_selection import grid_search_forecaster
from skforecast.ForecasterAutoregCustom import ForecasterAutoregCustom

# Datos 
steps = 36
n_datos_entrenar = 200
path_fichero = 'bitcoin.csv'
path_modelo = 'model.pickle'

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
datos = datos.set_index('date')
datos = datos['transactions']

# Split entre train y test
datos_train = datos[ -n_datos_entrenar:-steps]
datos_test  = datos[-steps:]

# Grid search de hiperparámetros
forecaster_rf = ForecasterAutoregCustom(
                    regressor      = RandomForestRegressor(random_state=123),
                    fun_predictors = create_predictors,
                    window_size    = 20
                )

# Hiperparámetros del regresor
param_grid = {'n_estimators': [100, 500],
              'max_depth': [3, 5, 10]}

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

# Guardo el modelo
ultima_fecha_entrenamiento = datos_test.index[-1].strftime('%Y-%m-%d %H:%M:%S')
pickle.dump(ultima_fecha_entrenamiento, open('ultima_fecha_entrenamiento.pickle', 'wb'))
pickle.dump(forecaster_rf, open(path_modelo, 'wb'))