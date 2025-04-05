# importing libraries
import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
import matplotlib.pyplot as plt 
import scipy
import streamlit.components.v1 as components
from streamlit_folium import folium_static
import folium

# setting page configuration
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

# reading csv files
Delhi = pd.read_csv('delhi.csv', parse_dates=['time'])
kuala_lumpur = pd.read_csv('kuala_lumpur.csv', parse_dates=['time'])
Singapore = pd.read_csv('singapore.csv', parse_dates=['time'])
Tokyo = pd.read_csv('Tokyo.csv', parse_dates=['time'])

# defining function
def rt_chart(City):
    City['date'] = pd.DatetimeIndex(City['time']).day
    City['month'] = pd.DatetimeIndex(City['time']).month
    City['year'] = pd.DatetimeIndex(City['time']).year

    st.header('Rainfall over past 40 years')
    col1, col2 = st.columns(2, gap='large')
    with col1:
        Year = st.slider('Choose Year', min_value=1980, max_value=2022, key=1)
        st.write('The selected Year is', Year)
    with col2:
        if Year == 2022:
            Month = st.slider('Choose Month', min_value=1, max_value=10, key=5)
        else:
            Month = st.slider('Choose Month', min_value=1, max_value=12, key=2)
        st.write('The selected Month is', Month)

    col1, col2 = st.columns([3, 1], gap='large')
    with col1:
        tab1, tab2 = st.tabs(['Table', 'Chart'])
        with tab1:
            st.dataframe(City[(City['month'] == Month) & (City['year'] == Year)], height=350, width=1000)
        with tab2:
            rain_chart = alt.Chart(City[(City['month'] == Month) & (City['year'] == Year)]).mark_line().encode(
                x='date', y='rainfall', tooltip=[alt.Tooltip('date', title="Date"), alt.Tooltip('rainfall', title='Rainfall in mm')], color=alt.value('green')).interactive().properties(height=350, width=750)
            st.altair_chart(rain_chart)

    with col2:
        st.metric("Year", value=Year)
        st.metric('Month', value=Month)
        st.metric("Total Precipitation in mm", value=round(City[(City['month'] == Month) & (City['year'] == Year)]['rainfall'].sum(), 1))

    st.markdown('''---''')
    st.header('Temperature over 40 years')

    Year = st.slider('Choose Year', min_value=1980, max_value=2022, key=3)
    st.write('The selected Year is', Year)

    col1, col2 = st.columns([3, 1], gap='large')
    with col1:
        tab1, tab2 = st.tabs(['Table', 'Chart'])
        with tab1:
            st.dataframe(City[City['year'] == Year])
        with tab2:
            temp_chart = alt.Chart(City[City['year'] == Year]).mark_rect().encode(
                x='date:O', y='month:O', color=alt.Color('avg_temp', scale=alt.Scale(scheme="inferno")), 
                tooltip=[alt.Tooltip('date', title="Date"), alt.Tooltip('avg_temp', title='Average Temperature in °C')]).properties(height=450, width=750)
            st.altair_chart(temp_chart)

    with col2:
        st.metric('Year', value=Year)
        st.metric('Maximum tempertature in °C', value=City[City['year'] == Year]['max_temp'].max())
        st.metric('Minimum tempertature in °C', value=City[City['year'] == Year]['min_temp'].min())

# Sidebar
st.sidebar.title('Climatic Changes')
image = 'https://www.noaa.gov/sites/default/files/styles/landscape_width_1275/public/2022-03/PHOTO-Climate-Collage-Diagonal-Design-NOAA-Communications-NO-NOAA-Logo.jpg'
st.sidebar.image(image)
st.sidebar.markdown('''
> Climate change refers to long-term shifts in temperatures and weather patterns. It also includes sea level rise, changes in weather patterns like drought and flooding, and much more.
---
''')
hawaiian_pages = ['All Islands', 'Kauaʻi', 'Oʻahu', 'Molokaʻi', 'Lānaʻi', 'Maui', 'Hawaiʻi (Big Island)']
selected_page = st.sidebar.selectbox(
    'Select a Page:', ('Delhi', 'Kuala Lumpur', 'Singapore', 'Tokyo')+ tuple(hawaiian_pages))
st.sidebar.markdown(
    'Here is an analysis of the weather data for four cities in Asia for 20 years.')

# Island Coordinates and Cities
islands_info = {
    'Kauaʻi': {
        'center': [22.1, -159.5],
        'zoom': 10,
        'cities': {'Līhuʻe': [21.9811, -159.3711]}
    },
    'Oʻahu': {
        'center': [21.4389, -158.0],
        'zoom': 10,
        'cities': {'Honolulu': [21.3069, -157.8583]}
    },
    'Molokaʻi': {
        'center': [21.1333, -157.0167],
        'zoom': 10,
        'cities': {'Kaunakakai': [21.0889, -157.0125]}
    },
    'Lānaʻi': {
        'center': [20.8333, -156.9167],
        'zoom': 11,
        'cities': {'Lānaʻi City': [20.8275, -156.9208]}
    },
    'Maui': {
        'center': [20.8, -156.3],
        'zoom': 10,
        'cities': {'Kahului': [20.8895, -156.4729]}
    },
    'Hawaiʻi (Big Island)': {
        'center': [19.6, -155.5],
        'zoom': 8,
        'cities': {'Hilo': [19.7297, -155.09], 'Kailua-Kona': [19.6406, -155.9956]}
    }
}

# Main Dashboard and chatbot
main_col, chat_col = st.columns([4,1])

with main_col:
    # Main Dashboard
    if selected_page in ['Delhi', 'Kuala Lumpur', 'Singapore', 'Tokyo']:
        st.markdown(f"""
        # Weather Dashboard - ***{selected_page}*** 
        > Climate information and analysis for {selected_page}.
        ---
        """)
        rt_chart(eval(selected_page.lower().replace(" ", "_")))
    elif selected_page == 'All Islands':
        st.markdown("""
        # Weather Data Dashboard - ***All Hawaiian Islands***
        > Overview of all major islands in the Hawaiian archipelago.
        ---
        """)
        bounds = [[18.5, -161.0], [22.25, -154.5]]
        all_map = folium.Map(location=[20.5, -157.0], zoom_start=7, tiles=None, min_zoom=6, max_bounds=True)
        folium.TileLayer('Esri.WorldImagery').add_to(all_map)
        for name, info in islands_info.items():
            folium.map.Marker(
                location=info['center'],
                icon=folium.DivIcon(
                    html=f'<div style="font-size: 16px; color: white; font-weight: bold; text-shadow: 1px 1px 2px black;">{name}</div>'
                )
            ).add_to(all_map)
        all_map.fit_bounds(bounds)
        folium_static(all_map)
    else:
        st.markdown(f"""
        # Weather Data Dashboard - ***{selected_page}***
        > {selected_page}, part of the Hawaiian Islands, showing city locations.
        ---
        """)
        info = islands_info[selected_page]
        island_map = folium.Map(location=info['center'], zoom_start=info['zoom'], tiles=None, min_zoom=6, max_bounds=True)
        folium.TileLayer('Esri.WorldImagery').add_to(island_map)
        for city, loc in info['cities'].items():
            folium.Marker(location=loc, popup=city).add_to(island_map)
        folium_static(island_map)
