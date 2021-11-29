import pandas as pd
import requests
from datetime import datetime
from sqlalchemy import create_engine
import os
uri = os.environ.get('URI')

# Obtengo los datos Últimos 12 datos        
url = 'https://api.blockchain.info/charts/transactions-per-second?timespan=all&sampled=false&metadata=false&cors=true&format=json'
resp = requests.get(url)
data = pd.DataFrame(resp.json()['values'])

# Pongo bien la fecha
data['x'] = [datetime.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S') for x in data['x']]
data['x'] = pd.to_datetime(data['x'])

# Leo la última predicción realizada
engine = create_engine(uri)
query = engine.execute('SELECT MAX(fecha_realidad) FROM realidad;')
ultima_fecha_realidad = query.fetchall()[0][0]
query.close()

# Leo la última predicción realizada
engine = create_engine(uri)
query = engine.execute('SELECT MIN(fecha_prediccion), MAX(fecha_prediccion) FROM predicciones;')
fecha_prediccion = query.fetchall()[0]
query.close()

primera_fecha_prediccion = fecha_prediccion[0]
ultima_fecha_prediccion = fecha_prediccion[1]

if ultima_fecha_realidad is None:
    fecha_extraer = primera_fecha_prediccion

elif  ultima_fecha_realidad <= ultima_fecha_prediccion:
    fecha_extraer = ultima_fecha_realidad

else:
    fecha_extraer = ultima_fecha_realidad

# Reondeo las horas
data['x'] = data['x'].dt.round('H')

# Obtengo nº de transacciones por hora
data_grouped = data\
  .groupby('x')\
  .sum()\
  .reset_index()

# Me quedo con los datos a partir de esa fecha
data_grouped = data_grouped.loc[data_grouped['x'] >= fecha_extraer,:]

# Subo los datos reales a la bbdd
upload_data = list(zip(data_grouped['x'], round(data_grouped['y'],4)))
upload_data[:3]

# Hago el insert
for upload_dia in upload_data:
    timestamp, realidad = upload_dia

    result = engine.execute(f"INSERT INTO realidad (fecha_realidad, realidad)\
        VALUES('{timestamp}', '{realidad}') \
        ON CONFLICT (fecha_realidad) DO UPDATE \
        SET fecha_realidad = '{timestamp}', \
            realidad = '{realidad}'\
        ;")
    result.close()
