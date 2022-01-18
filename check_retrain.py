# Objective: check if the model should be retrained or not


import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import requests
import json
import os

user = 'anderDecidata'
repo = 'Ejemplo-MLOps'
event_type = 'execute-retrain'
GITHUB_TOKEN = os.environ.get('TOKEN')
uri = os.environ.get('URI')

# Data
max_mae = 8
n_observations_analyze = 48

# N days to substract
days_subsctract = round(n_observations_analyze/24)

# I create the engine
engine = create_engine(uri)

# I get the largest date
resp = engine.execute('SELECT MAX(fecha) FROM tablon;')
largest_date = resp.fetchall()
resp.close()

# I calculate the initial date
initial_date = largest_date[0][0] - timedelta(days = days_subsctract)

# I get the data from the initial date
resp = engine.execute(f"SELECT * FROM tablon WHERE fecha > '{initial_date}';")
data = resp.fetchall()
colnames = resp.keys()
resp.close()

# Convert it to Data Frame
data = pd.DataFrame(data, columns=colnames)

# I get mean MAE
print(data['mae'].mean())

# If exceed max mae 
if data['mae'].mean() > max_mae:

    # Call Github Actions to retrain the model
    url = f'https://api.github.com/repos/{user}/{repo}/dispatches'

    # I make the request
    resp = requests.post(
        url,
        headers={'Authorization': f'token  {GITHUB_TOKEN}'},
        data = json.dumps({'event_type': event_type})
        )

    
