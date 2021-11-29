import requests
import pandas as pd
from datetime import datetime

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
bitcoin.to_csv('bitcoin.csv', index = False)