import requests
url = 'https://ejemplo-mlops-qc5dfzkvdq-ew.a.run.app'
resp = requests.post(url, params={'return_predicciones': 'True'})
print(resp.content)