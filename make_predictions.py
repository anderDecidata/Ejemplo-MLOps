import requests
url = 'https://mlops-qc5dfzkvdq-ew.a.run.app/forecast'
resp = requests.post(url, params={'return_predicciones': 'True'})