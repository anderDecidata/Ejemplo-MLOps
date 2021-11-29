def create_predictors(y):
    '''
    Crear los primeros 10 lags.
    Calcular la media móvil de los últimos 20 valores.
    '''
    import pandas as pd
    
    X_train = pd.DataFrame({'y':y.copy()})
    for i in range(0, 10):
        X_train[f'lag_{i+1}'] = X_train['y'].shift(i)
        
    X_train['moving_avg'] = X_train['y'].rolling(20).mean()
    
    X_train = X_train.drop(columns='y').tail(1).to_numpy()  
    
    return X_train  
    