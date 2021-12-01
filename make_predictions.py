import requests
url = 'https://ejemplo-mlops-qc5dfzkvdq-ew.a.run.app/forecast'
resp = requests.post(url, params={'return_predicciones': 'True'})
print(resp.content)