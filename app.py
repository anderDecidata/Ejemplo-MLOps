from fastapi import FastAPI


app = FastAPI()

@app.post("/forecast")
def forecast(num_predicciones = 168, return_predictions = True):
    
    import pandas as pd
    import requests
    from datetime import datetime
    from sqlalchemy import create_engine
    from secrets import uri
    import pickle

    # Load Files
    forecaster_rf = pickle.load(open('model.pickle', 'rb'))
    ultima_fecha_entrenamiento = pickle.load(open('ultima_fecha_entrenamiento.pickle', 'rb'))
    ultima_fecha_entrenamiento = datetime.strptime(ultima_fecha_entrenamiento, '%Y-%m-%d %H:%M:%S') 

    # Obtengo los datos Últimos 12 datos
    url = 'https://api.blockchain.info/charts/transactions-per-second?timespan=all&sampled=false&metadata=false&cors=true&format=json'
    resp = requests.get(url)
    data = pd.DataFrame(resp.json()['values'])

    # Pongo bien la fecha
    data['x'] = [datetime.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S') for x in data['x']]
    data['x'] = pd.to_datetime(data['x'])
    
    

    # Leo la última predicción realizada
    engine = create_engine(uri)
    query = engine.execute('SELECT MAX(fecha_prediccion) FROM predicciones;')
    ultima_fecha_prediccion = query.fetchall()[0][0]
    query.close()        

    # Si no hay última fecha en BBDD o entrenamiento > BBDD, leo la última fecha de entrenamiento
    if  (ultima_fecha_prediccion is None) or (ultima_fecha_prediccion > ultima_fecha_entrenamiento):
        
        # Como no hay predicciones, hago predicciones para los próximos días
        predicciones = forecaster_rf.predict(num_predicciones)

        fechas = pd.date_range(
            start = ultima_fecha_entrenamiento.strftime('%Y-%m-%d %H:%M:%S'),
            periods = num_predicciones,
            freq = '1H'
            )

    elif ultima_fecha_prediccion > ultima_fecha_entrenamiento:
        # En este caso hay que tener en cuenta las diferencias entre la última fecha de predicción y sumar la diferencia al número de días a extraer
        dif_seg= ultima_fecha_prediccion - ultima_fecha_entrenamiento
        horas_extraer = num_predicciones + dif_seg.seconds//3600
        predicciones = forecaster_rf.predict(num_predicciones)
        # Me quedo con las últimas predicciones
        predicciones = predicciones[-num_predicciones:]
        
        fechas = pd.date_range(
            start = ultima_fecha_prediccion.strftime('%Y-%m-%d %H:%M:%S'),
            periods = num_predicciones,
            freq = '1H'
            )
    else:
        # Si el último entrenamiento > últimas predicciones
        predicciones = forecaster_rf.predict(num_predicciones)

        fechas = pd.date_range(
            start = ultima_fecha_entrenamiento.strftime('%Y-%m-%d %H:%M:%S'),
            periods = num_predicciones,
            freq = '1H'
            )
    
    upload_data = list(zip([
    datetime.now().strftime('%Y-%m-%d %H:%M:%S')] * num_predicciones,
    [fecha.strftime('%Y-%m-%d %H:%M:%S') for fecha in fechas ],
        predicciones
    ))

    # Hago el insert
    for upload_dia in upload_data:
        timestamp, fecha_pred, pred = upload_dia
        pred = round(pred, 4)

        result = engine.execute(f"INSERT INTO predicciones (timestamp, fecha_prediccion,  prediccion)\
            VALUES('{timestamp}', '{fecha_pred}', '{pred}') \
            ON CONFLICT (fecha_prediccion) DO UPDATE \
            SET timestamp = '{timestamp}', \
                prediccion = '{pred}'\
            ;")
        result.close()
    if return_predictions:
        predicciones
    else:
        return 'Insertados nuevos datos'