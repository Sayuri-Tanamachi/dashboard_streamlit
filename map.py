from datetime import datetime
import streamlit as st
import numpy as np
import pandas as pd
import pydeck as pdk
import plotly.express as px

st.title ('Mapa de accidentes vehículares en New York')

DATE_TIME = "date/time"
db = ('./base.csv')

st.markdown ('En este dashbord podras ver los puntos de mayor frecuencia en accidentes vehículares ocurridos desde Julio 2012 hasta Mayo 2021 en la ciudad de New York')

st.markdown( """ <style>
 .map {
 background-color: #FFB333;
}
</style>""", unsafe_allow_html=True )


def load_data (nrows):
    data = pd.read_csv (db, nrows = nrows, parse_dates =[['CRASH_DATE','CRASH_TIME']])
    data.dropna (subset = ['LATITUDE', 'LONGITUDE'], inplace = True)
    def lowercase (x): return str(x).lower()
    data.rename (lowercase, axis= "columns", inplace =True)
    data.rename(columns={'crash_date_crash_time': "date/time"}, inplace=True)
    return data

data = load_data((100000))

st.header ('*¿Dónde hay más personas lesionadas en NYC?*')
personas_heridas  = st.slider ('Número de personas que han tenido un accidente vehícular', min_value=0, max_value=20, value=6, step=1)
st.text ('Desplazate en el mapa')
st.map (data.query ('injured >= @personas_heridas')
    [['latitude', 'longitude']].dropna (how='any'))

st.header ('*¿Cuántos accidentes ocurren durante cada hora del día?*')
hour = st.slider ('Escoje una hora:', min_value=0, max_value=23, value=9, step=1)
data2 = data
data = data[data[DATE_TIME].dt.hour == hour]
st.markdown ('Accidentes Vehiculares entre %i:00 - %i:00' % (hour, (hour + 1) % 24))

midpoint = (np.average(data["latitude"]), np.average(data["longitude"]))
st.write(pdk.Deck(map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={ "latitude": midpoint[0], "longitude": midpoint[1], "zoom": 15, "pitch": 50, },

layers=[pdk.Layer( "HexagonLayer",
            data=data[['date/time', 'latitude', 'longitude']],
            get_position=["longitude", "latitude"],
            auto_highlight=True,
            radius=100,
            extruded=True,
            pickable=True,
            elevation_scale=4,
            elevation_range=[0, 1000],), ], ))

if st.checkbox("Mostrar base de datos", False) :
    st.subheader("Datos desde Julio 2012 hasta Mayo 2021 between %i:00 and %i:00" % (hour, (hour + 1) % 24))
    st.write(data)
    st.subheader("Accidentes por minuto entre %i:00 and %i:00" % (hour, (hour + 1) % 24))
filtered = data[(data[DATE_TIME].dt.hour >= hour) & (data[DATE_TIME].dt.hour < (hour + 1))]
hist = np.histogram(filtered[DATE_TIME].dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({'minute':range(60), 'crashes': hist})

fig = px.bar (chart_data, x='minute', y ='crashes', hover_data=['minute', 'crashes'], height=600, width=780 )
st.write(fig)
