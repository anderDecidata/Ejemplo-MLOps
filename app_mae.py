import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
import plotly.express as px
from ddbb_secrets import uri

st.write("""
# Evolución del MAE
Visualiza cómo ha evolucionado la capacidad predictiva del modelo. 
""")

# Obtengo los datos
engine = create_engine(uri)

query = 'SELECT * FROM tablon;'
result = engine.execute(query)
datos = result.fetchall()
result.close()

datos = pd.DataFrame(datos, columns = [
    'fecha_prediccion',
    'prediccion',
    'realidad',
    'MAE'
    ])


# Creo indicadores
m1, m2, m3 = st.columns((1,1,1))
m1.metric(label ='Nº transac. medias',value = str(round(datos['realidad'].mean(), 2)))
m1.metric(label ='Nº transac. medias pred',value = str(round(datos['prediccion'].mean(), 2)))
m2.metric(label ='Error Medio (MAE)',value = str(round(datos['MAE'].mean(), 2)))


# Creo el gráfico
fig = px.line(datos, x='fecha_prediccion', y="MAE")

st.plotly_chart(fig, use_container_width=True)