# importing libraries
import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
import matplotlib.pyplot as plt 
import streamlit.components.v1 as components
from streamlit_folium import folium_static
import folium
import requests
from transformers import AutoTokenizer, AutoModelForQuestionAnswering, pipeline

# this is a test
# setting page configuration
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

# reading csv files
Delhi = pd.read_csv('delhi.csv', parse_dates=['time'])
kuala_lumpur = pd.read_csv(
    'kuala_lumpur.csv', parse_dates=['time'])
Singapore = pd.read_csv(
    'singapore.csv', parse_dates=['time'])
Tokyo = pd.read_csv('Tokyo.csv', parse_dates=['time'])

# defining function
def rt_chart(City):
    # creating date,month and year column
    City['date'] = pd.DatetimeIndex(City['time']).day
    City['month'] = pd.DatetimeIndex(City['time']).month
    City['year'] = pd.DatetimeIndex(City['time']).year

    # rainfall analysis
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
            st.dataframe(City[(City['month'] == Month) & (
                City['year'] == Year)], height=350, width=1000)
        with tab2:
            rain_chart = alt.Chart(City[(City['month'] == Month) & (City['year'] == Year)]).mark_line().encode(
                x='date', y='rainfall', tooltip=[alt.Tooltip('date', title="Date"), alt.Tooltip('rainfall', title='Rainfall in mm')], color=alt.value('green')).interactive().properties(height=350, width=750)
            st.altair_chart(rain_chart)

    with col2:
        st.metric("Year", value=Year)
        st.metric('Month', value=Month)
        st.metric("Total Precipitation in mm", value=round(
            City[(City['month'] == Month) & (City['year'] == Year)]['rainfall'].sum(), 1))
    st.markdown('''---''')
    # temperature analysis
    st.header('Temperature over 40 years')

    Year = st.slider('Choose Year', min_value=1980, max_value=2022, key=3)
    st.write('The selected Year is', Year)

    col1, col2 = st.columns([3, 1], gap='large')
    with col1:
        tab1, tab2 = st.tabs(['Table', 'Chart'])
        with tab1:
            st.dataframe(City[City['year'] == Year])
        with tab2:
            temp_chart = alt.Chart(City[City['year'] == Year]).mark_rect().encode(x='date:O', y='month:O', color=alt.Color('avg_temp', scale=alt.Scale(scheme="inferno")), tooltip=[
                alt.Tooltip('date', title="Date"), alt.Tooltip('avg_temp', title='Average Temperature in °C')]).properties(height=450, width=750)
            st.altair_chart(temp_chart)

    with col2:
        st.metric('Year', value=Year)
        st.metric('Maximum tempertature in °C',
                  value=City[City['year'] == Year]['max_temp'].max())
        st.metric('Minimum tempertature in °C',
                  value=City[City['year'] == Year]['min_temp'].min())


# Sidebar
# st.sidebar.title('Climatic Changes')
# image = 'https://www.noaa.gov/sites/default/files/styles/landscape_width_1275/public/2022-03/PHOTO-Climate-Collage-Diagonal-Design-NOAA-Communications-NO-NOAA-Logo.jpg'
# st.sidebar.image(image)
# st.sidebar.markdown('''
# > Climate change refers to long-term shifts in temperatures and weather patterns. It also includes sea level rise, changes in weather patterns like drought and flooding, and much more.
# ---
# ''')
# selected_page = st.sidebar.selectbox(
#     'Select a City:', ('Delhi', 'Kuala Lumpur', 'Singapore', 'Tokyo', 'All Islands', 'Kauaʻi', 'Oʻahu', 'Molokaʻi', 'Lānaʻi', 'Maui', 'Hawaiʻi (Big Island)'))
# st.sidebar.markdown(
#     'Here is an analysis of the weather data for four cities in Asia for 20 years.')


# Sidebar
metric_view = st.sidebar.radio("Select View:", ["Daily", "Monthly"])
st.sidebar.title('Climatic Changes')
image = 'https://www.noaa.gov/sites/default/files/styles/landscape_width_1275/public/2022-03/PHOTO-Climate-Collage-Diagonal-Design-NOAA-Communications-NO-NOAA-Logo.jpg'
st.sidebar.image(image)
st.sidebar.markdown('''
> Climate change refers to long-term shifts in temperatures and weather patterns. It also includes sea level rise, changes in weather patterns like drought and flooding, and much more.
---
''')
# hawaiian_pages = ['All Islands', 'Kauaʻi', 'Oʻahu', 'Molokaʻi', 'Lānaʻi', 'Maui', 'Hawaiʻi (Big Island)']
selected_page = st.sidebar.selectbox('Select a Page:', ('All Islands', 'Kauaʻi', 'Oʻahu', 'Molokaʻi', 'Lānaʻi', 'Maui', 'Hawaiʻi (Big Island)'))
st.sidebar.markdown('Here is an analysis of the weather data for four cities in Asia for 20 years.')


# Default Homepage Map if no selection yet or fallback
if selected_page == 'All Islands':
    st.markdown('''
    # Hawaiian Islands Overview
    > Explore the main islands of Hawaiʻi. Each island is labeled and zooming is limited to the archipelago region.
    ---
    ''')
    bounds = [[18.5, -161.0], [22.25, -154.5]]
    all_map = folium.Map(location=[20.5, -157.0], zoom_start=7, tiles=None, min_zoom=6, max_bounds=True)
    folium.TileLayer('Esri.WorldImagery').add_to(all_map)

    islands_info = {
        'Kauaʻi': [22.1, -159.5],
        'Oʻahu': [21.4389, -158.0],
        'Molokaʻi': [21.1333, -157.0167],
        'Lānaʻi': [20.8333, -156.9167],
        'Maui': [20.8, -156.3],
        'Hawaiʻi (Big Island)': [19.6, -155.5]
    }
    for name, coords in islands_info.items():
        folium.map.Marker(
            location=coords,
            icon=folium.DivIcon(
                html=f'<div style="font-size:16px;color:white;font-weight:bold;text-shadow:1px 1px 2px black;">{name}</div>'
            )
        ).add_to(all_map)

    all_map.fit_bounds(bounds)
    folium_static(all_map)

# Main Dashboard (only new blocks for each island below)
from datetime import datetime

today = datetime.today()
def render_time_selectors(view):
    if view == "Monthly":
        colm1, colm2 = st.columns([1, 1])
        with colm1:
            st.markdown("#### Choose Month")
            st.session_state.selected_month = st.slider("", 1, 12, today.month, key=f"month_{selected_page}")
        with colm2:
            st.markdown("#### Choose Year")
            st.session_state.selected_year = st.slider("", 1990, today.year, today.year, key=f"year_{selected_page}")
    else:
        cold1, cold2, cold3 = st.columns([1, 1, 1])
        with cold1:
            st.markdown("#### Choose Day")
            st.session_state.selected_day = st.slider("", 1, 31, today.day, key=f"day_{selected_page}")
        with cold2:
            st.markdown("#### Choose Month")
            st.session_state.selected_month = st.slider("", 1, 12, today.month, key=f"month_{selected_page}")
        with cold3:
            st.markdown("#### Choose Year")
            st.session_state.selected_year = st.slider("", 1990, today.year, today.year, key=f"year_{selected_page}")


if selected_page == 'Oʻahu':
    st.markdown('''
    # Weather Data Dashboard - ***Oʻahu***
    > Oʻahu, known as "The Gathering Place," is the third-largest of the Hawaiian Islands...
    ---
    ''')
    render_time_selectors(metric_view)

    # Conditional Metrics Based on View
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    if metric_view == "Daily":
        with col1:
            st.metric("Daily Precip", "3.2 mm")
        with col2:
            st.metric("Max Temp", "30.1 °C")
        with col3:
            st.metric("Min Temp", "21.7 °C")
        with col4:
            st.metric("Humidity", "75%")
        with col5:
            st.markdown('<div style="background-color:#34c759;padding:16px 10px;border-radius:10px;text-align:center;color:white;font-weight:bold;font-size:16px;line-height:1.4;">Flood Warning<br><span style="font-size:18px;">No</span></div>', unsafe_allow_html=True)
        with col6:
            st.markdown('<div style="background-color:#ffcc00;padding:10px;border-radius:8px;text-align:center;color:black;font-weight:bold;">Fire Warning<br>Low</div>', unsafe_allow_html=True)
    else:
        with col1:
            st.metric("Monthly Precip", "85 mm")
        with col2:
            st.metric("Avg Max Temp", "29.5 °C")
        with col3:
            st.metric("Avg Min Temp", "22.3 °C")
        with col4:
            st.metric("Avg Humidity", "77%")
        with col5:
            st.markdown('<div style="background-color:#34c759;padding:16px 10px;border-radius:10px;text-align:center;color:white;font-weight:bold;font-size:16px;line-height:1.4;">Flood Warning<br><span style="font-size:18px;">No</span></div>', unsafe_allow_html=True)
        with col6:
            st.markdown('<div style="background-color:#ffcc00;padding:10px;border-radius:8px;text-align:center;color:black;font-weight:bold;">Fire Warning<br>Low</div>', unsafe_allow_html=True)
    st.markdown('''
    # Weather Data Dashboard - ***Oʻahu***
    > Oʻahu, known as "The Gathering Place," is the third-largest of the Hawaiian Islands...
    ---
    ''')

    # Climate Metrics Displayed Horizontally with color indicators
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.metric("Avg Daily Precip", "3.2 mm", "+12%")
    with col2:
        st.metric("Avg Max Temp", "29.5 °C", "-1.2 °C")
    with col3:
        st.metric("Avg Min Temp", "22.3 °C", "+0.5 °C")
    with col4:
        st.metric("Avg Humidity", "77%", "+3%")
    with col5:
        st.markdown('<div style="background-color:#34c759;padding:16px 10px;border-radius:10px;text-align:center;color:white;font-weight:bold;font-size:16px;line-height:1.4;">Flood Warning<br><span style="font-size:18px;">No</span></div>', unsafe_allow_html=True)
    with col6:
        st.markdown('<div style="background-color:#ffcc00;padding:10px;border-radius:8px;text-align:center;color:black;font-weight:bold;">Fire Warning<br>Low</div>', unsafe_allow_html=True)
    oahu_map = folium.Map(location=[21.4389, -158.0], zoom_start=9, tiles=None, min_zoom=6, max_bounds=True)
    folium.TileLayer('Esri.WorldImagery').add_to(oahu_map)
    folium.Marker([21.3069, -157.8583], popup='Honolulu').add_to(oahu_map)
    folium_static(oahu_map)


elif selected_page == 'Kauaʻi':
    st.markdown('''
    # Weather Data Dashboard - ***Kauaʻi***
    > Kauaʻi, also known as the Garden Isle, is the oldest of the main Hawaiian Islands...
    ---
    ''')
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    if metric_view == "Daily":
        col1.metric("Daily Precip", "4.1 mm")
        col2.metric("Max Temp", "29.0 °C")
        col3.metric("Min Temp", "22.0 °C")
        col4.metric("Humidity", "80%")
    else:
        col1.metric("Monthly Precip", "105 mm")
        col2.metric("Avg Max Temp", "28.5 °C")
        col3.metric("Avg Min Temp", "21.8 °C")
        col4.metric("Avg Humidity", "79%")
    col5.markdown('<div style="background-color:#34c759;padding:16px 10px;border-radius:10px;text-align:center;color:white;font-weight:bold;font-size:16px;line-height:1.4;">Flood Warning<br><span style="font-size:18px;">No</span></div>', unsafe_allow_html=True)
    col6.markdown('<div style="background-color:#ffcc00;padding:10px;border-radius:8px;text-align:center;color:black;font-weight:bold;">Fire Warning<br>Low</div>', unsafe_allow_html=True)
    st.markdown('''
    # Weather Data Dashboard - ***Kauaʻi***
    > Kauaʻi, also known as the Garden Isle, is the oldest of the main Hawaiian Islands...
    ---
    ''')
    kauai_map = folium.Map(location=[22.1, -159.5], zoom_start=10, tiles=None, min_zoom=6, max_bounds=True)
    folium.TileLayer('Esri.WorldImagery').add_to(kauai_map)
    folium.Marker([21.9811, -159.3711], popup='Līhuʻe').add_to(kauai_map)
    folium_static(kauai_map)

elif selected_page == 'Molokaʻi':
    st.markdown('''
    # Weather Data Dashboard - ***Molokaʻi***
    > Molokaʻi is known for its high sea cliffs and rural lifestyle...
    ---
    ''')
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    if metric_view == "Daily":
        col1.metric("Daily Precip", "2.7 mm")
        col2.metric("Max Temp", "28.2 °C")
        col3.metric("Min Temp", "21.2 °C")
        col4.metric("Humidity", "74%")
    else:
        col1.metric("Monthly Precip", "90 mm")
        col2.metric("Avg Max Temp", "27.8 °C")
        col3.metric("Avg Min Temp", "21.0 °C")
        col4.metric("Avg Humidity", "73%")
    col5.markdown('<div style="background-color:#34c759;padding:16px 10px;border-radius:10px;text-align:center;color:white;font-weight:bold;font-size:16px;line-height:1.4;">Flood Warning<br><span style="font-size:18px;">No</span></div>', unsafe_allow_html=True)
    col6.markdown('<div style="background-color:#ffcc00;padding:10px;border-radius:8px;text-align:center;color:black;font-weight:bold;">Fire Warning<br>Low</div>', unsafe_allow_html=True)
    st.markdown('''
    # Weather Data Dashboard - ***Molokaʻi***
    > Molokaʻi is known for its high sea cliffs and rural lifestyle...
    ---
    ''')
    molokai_map = folium.Map(location=[21.1333, -157.0167], zoom_start=10, tiles=None, min_zoom=6, max_bounds=True)
    folium.TileLayer('Esri.WorldImagery').add_to(molokai_map)
    folium.Marker([21.0889, -157.0125], popup='Kaunakakai').add_to(molokai_map)
    folium_static(molokai_map)

elif selected_page == 'Lānaʻi':
    st.markdown('''
    # Weather Data Dashboard - ***Lānaʻi***
    > Lānaʻi, the smallest publicly accessible inhabited island in Hawaii...
    ---
    ''')
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    if metric_view == "Daily":
        col1.metric("Daily Precip", "1.9 mm")
        col2.metric("Max Temp", "27.1 °C")
        col3.metric("Min Temp", "20.5 °C")
        col4.metric("Humidity", "70%")
    else:
        col1.metric("Monthly Precip", "65 mm")
        col2.metric("Avg Max Temp", "26.8 °C")
        col3.metric("Avg Min Temp", "20.3 °C")
        col4.metric("Avg Humidity", "69%")
    col5.markdown('<div style="background-color:#34c759;padding:16px 10px;border-radius:10px;text-align:center;color:white;font-weight:bold;font-size:16px;line-height:1.4;">Flood Warning<br><span style="font-size:18px;">No</span></div>', unsafe_allow_html=True)
    col6.markdown('<div style="background-color:#ffcc00;padding:10px;border-radius:8px;text-align:center;color:black;font-weight:bold;">Fire Warning<br>Low</div>', unsafe_allow_html=True)
    st.markdown('''
    # Weather Data Dashboard - ***Lānaʻi***
    > Lānaʻi, the smallest publicly accessible inhabited island in Hawaii...
    ---
    ''')
    lanai_map = folium.Map(location=[20.8333, -156.9167], zoom_start=11, tiles=None, min_zoom=6, max_bounds=True)
    folium.TileLayer('Esri.WorldImagery').add_to(lanai_map)
    folium.Marker([20.8275, -156.9208], popup='Lānaʻi City').add_to(lanai_map)
    folium_static(lanai_map)

elif selected_page == 'Maui':
    st.markdown('''
    # Weather Data Dashboard - ***Maui***
    > Maui is known for its beaches, the sacred ʻĪao Valley, and the scenic Hana Highway...
    ---
    ''')
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    if metric_view == "Daily":
        col1.metric("Daily Precip", "3.4 mm")
        col2.metric("Max Temp", "29.4 °C")
        col3.metric("Min Temp", "22.1 °C")
        col4.metric("Humidity", "76%")
    else:
        col1.metric("Monthly Precip", "92 mm")
        col2.metric("Avg Max Temp", "28.9 °C")
        col3.metric("Avg Min Temp", "21.9 °C")
        col4.metric("Avg Humidity", "75%")
    col5.markdown('<div style="background-color:#34c759;padding:16px 10px;border-radius:10px;text-align:center;color:white;font-weight:bold;font-size:16px;line-height:1.4;">Flood Warning<br><span style="font-size:18px;">No</span></div>', unsafe_allow_html=True)
    col6.markdown('<div style="background-color:#ffcc00;padding:10px;border-radius:8px;text-align:center;color:black;font-weight:bold;">Fire Warning<br>Low</div>', unsafe_allow_html=True)
    st.markdown('''
    # Weather Data Dashboard - ***Maui***
    > Maui is known for its beaches, the sacred ʻĪao Valley, and the scenic Hana Highway...
    ---
    ''')
    maui_map = folium.Map(location=[20.8, -156.3], zoom_start=10, tiles=None, min_zoom=6, max_bounds=True)
    folium.TileLayer('Esri.WorldImagery').add_to(maui_map)
    folium.Marker([20.8895, -156.4729], popup='Kahului').add_to(maui_map)
    folium_static(maui_map)

elif selected_page == 'Hawaiʻi (Big Island)':
    st.markdown('''
    # Weather Data Dashboard - ***Hawaiʻi (Big Island)***
    > The Big Island is the largest in the Hawaiian archipelago and features diverse climates and active volcanoes...
    ---
    ''')
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    if metric_view == "Daily":
        col1.metric("Daily Precip", "4.5 mm")
        col2.metric("Max Temp", "28.8 °C")
        col3.metric("Min Temp", "21.4 °C")
        col4.metric("Humidity", "78%")
    else:
        col1.metric("Monthly Precip", "110 mm")
        col2.metric("Avg Max Temp", "28.1 °C")
        col3.metric("Avg Min Temp", "21.2 °C")
        col4.metric("Avg Humidity", "77%")
    col5.markdown('<div style="background-color:#34c759;padding:16px 10px;border-radius:10px;text-align:center;color:white;font-weight:bold;font-size:16px;line-height:1.4;">Flood Warning<br><span style="font-size:18px;">No</span></div>', unsafe_allow_html=True)
    col6.markdown('<div style="background-color:#ffcc00;padding:10px;border-radius:8px;text-align:center;color:black;font-weight:bold;">Fire Warning<br>Low</div>', unsafe_allow_html=True)
    st.markdown('''
    # Weather Data Dashboard - ***Hawaiʻi (Big Island)***
    > The Big Island is the largest in the Hawaiian archipelago and features diverse climates and active volcanoes...
    ---
    ''')
    bigisland_map = folium.Map(location=[19.6, -155.5], zoom_start=8, tiles=None, min_zoom=6, max_bounds=True)
    folium.TileLayer('Esri.WorldImagery').add_to(bigisland_map)
    folium.Marker([19.7297, -155.09], popup='Hilo').add_to(bigisland_map)
    folium.Marker([19.6406, -155.9956], popup='Kailua-Kona').add_to(bigisland_map)
    folium_static(bigisland_map)




# # Main Dashboard and chatbot
# main_col, chat_col = st.columns([4,1])

# with main_col:
#     # Main Dashboard
#     if selected_page == 'Delhi':
#         st.markdown('''
#         # Weather Dashboard - ***Delhi*** 
#         > Delhi, the capital of India, is one of the most populous and polluted cities in the world. The city has changed a lot over the years with respect to its weather. There have been a number of factors that have contributed to this change, including climate change. Here is a dashboard for the analysis of weather data for 20 years.
#         ---
#         ''')
#         rt_chart(Delhi)
#     elif selected_page == 'Kuala Lumpur':
#         st.markdown('''
#         # Weather Data Dashboard - ***Kuala Lumpur***
#         > Kaula Lumpur, the capital city of Malaysia, home to the iconic Twin Towers. Kuala Lumpur is best known for its affordable luxury hotels, great shopping scene, and even better food. Malaysian capital boasts some of the finest shopping centers in the world, head towards Pavilion KL and Suria KLC for high-end luxurious items, or visit Petaling Street to have a real sense of local shopping. The city has changed a lot over the years with respect to its weather. There have been a number of factors that have contributed to this change, including climate change. Here is a dashboard for the analysis of weather data for 20 years.
#         ---
#         ''')
#         rt_chart(kuala_lumpur)
#     elif selected_page == 'Singapore':
#         st.markdown('''
#         # Weather Data Dashboard - ***Singapore***
#         > Singapore, officially the Republic of Singapore, is a sovereign island country and city-state in maritime Southeast Asia. It is famous for being a global financial center, being among the most densely populated places in the world, having a world-class city airport with a waterfall, and a Botanic Garden that is a World Heritage Site. The city has changed a lot over the years with respect to its weather. There have been a number of factors that have contributed to this change, including climate change. Here is a dashboard for the analysis of weather data for 20 years.
#         ''')
#         rt_chart(Singapore)
#     elif selected_page == 'Tokyo':
#         st.markdown('''
#         # Weather Data Dashboard - ***Tokyo***
#         > Tokyo, Japan’s busy capital, mixes the ultramodern and the traditional...
#         ''')
#         rt_chart(Tokyo)
#     elif selected_page == 'All Islands':
#         st.markdown("""
#         # Weather Data Dashboard - ***All Hawaiian Islands***
#         > Overview of all major islands in the Hawaiian archipelago.
#         ---
#         """)
#         bounds = [[18.5, -161.0], [22.25, -154.5]]
#         all_map = folium.Map(location=[20.5, -157.0], zoom_start=7, tiles=None, min_zoom=6, max_bounds=True)
#         folium.TileLayer('Esri.WorldImagery').add_to(all_map)
#         for name, info in islands_info.items():
#             folium.map.Marker(
#                 location=info['center'],
#                 icon=folium.DivIcon(
#                     html=f'<div style="font-size: 16px; color: white; font-weight: bold; text-shadow: 1px 1px 2px black;">{name}</div>'
#                 )
#             ).add_to(all_map)
#         all_map.fit_bounds(bounds)
#         folium_static(all_map)

#     elif selected_page == 'Oʻahu':
#         st.markdown('''
#         # Weather Data Dashboard - ***Oʻahu***
#         > Oʻahu, known as "The Gathering Place," is the third-largest of the Hawaiian Islands...
#         ---
#         ''')
#         # Climate Metrics Displayed Horizontally with color indicators
#         col1, col2, col3, col4, col5, col6 = st.columns(6)
#         with col1:
#             st.metric("Avg Daily Precip", "3.2 mm", "+12%")
#         with col2:
#             st.metric("Avg Max Temp", "29.5 °C", "-1.2 °C")
#         with col3:
#             st.metric("Avg Min Temp", "22.3 °C", "+0.5 °C")
#         with col4:
#             st.metric("Avg Humidity", "77%", "+3%")
#         with col5:
#             st.markdown('<div style="background-color:#34c759;padding:5px 10px;border-radius:12px;text-align:center;color:white;font-weight:bold;font-size:16px;line-height:1.4;">Flood Warning<br><span style="font-size:18px;">No</span></div>', unsafe_allow_html=True)
#         with col6:
#             st.markdown('<div style="background-color:#ffcc00;padding:10px;border-radius:8px;text-align:center;color:black;font-weight:bold;">Fire Warning<br>Low</div>', unsafe_allow_html=True)
#         # bounds = [[18.5, -161.0], [21.9, -154.5]]
#         oahu_map = folium.Map(location=[21.4389, -158.0], zoom_start=10, tiles=None, min_zoom=6, max_bounds=True)
#         folium.TileLayer('Esri.WorldImagery').add_to(oahu_map)
#         # folium.Marker([21.3069, -157.8583], popup='Honolulu').add_to(oahu_map)
#         folium_static(oahu_map)
        

#     elif selected_page == 'Kauaʻi':
#         st.markdown('''
#         # Weather Data Dashboard - ***Kauaʻi***
#         > Kauaʻi, also known as the Garden Isle, is the oldest of the main Hawaiian Islands...
#         ---
#         ''')
#          # Climate Metrics Displayed Horizontally with color indicators
#         col1, col2, col3, col4, col5, col6 = st.columns(6)
#         with col1:
#             st.metric("Avg Daily Precip", "3.2 mm", "+12%")
#         with col2:
#             st.metric("Avg Max Temp", "29.5 °C", "-1.2 °C")
#         with col3:
#             st.metric("Avg Min Temp", "22.3 °C", "+0.5 °C")
#         with col4:
#             st.metric("Avg Humidity", "77%", "+3%")
#         with col5:
#             st.markdown('<div style="background-color:#34c759;padding:5px 10px;border-radius:12px;text-align:center;color:white;font-weight:bold;font-size:16px;line-height:1.4;">Flood Warning<br><span style="font-size:18px;">No</span></div>', unsafe_allow_html=True)
#         with col6:
#             st.markdown('<div style="background-color:#ffcc00;padding:10px;border-radius:8px;text-align:center;color:black;font-weight:bold;">Fire Warning<br>Low</div>', unsafe_allow_html=True)
        
#         kauai_map = folium.Map(location=[22.1, -159.5], zoom_start=10, tiles=None, min_zoom=6, max_bounds=True)
#         folium.TileLayer('Esri.WorldImagery').add_to(kauai_map)
#         # folium.Marker([21.9811, -159.3711], popup='Līhuʻe').add_to(kauai_map)
#         folium_static(kauai_map)

#     elif selected_page == 'Molokaʻi':
#         st.markdown('''
#         # Weather Data Dashboard - ***Molokaʻi***
#         > Molokaʻi is known for its high sea cliffs and rural lifestyle...
#         ---
#         ''')
#          # Climate Metrics Displayed Horizontally with color indicators
#         col1, col2, col3, col4, col5, col6 = st.columns(6)
#         with col1:
#             st.metric("Avg Daily Precip", "3.2 mm", "+12%")
#         with col2:
#             st.metric("Avg Max Temp", "29.5 °C", "-1.2 °C")
#         with col3:
#             st.metric("Avg Min Temp", "22.3 °C", "+0.5 °C")
#         with col4:
#             st.metric("Avg Humidity", "77%", "+3%")
#         with col5:
#             st.markdown('<div style="background-color:#34c759;padding:5px 10px;border-radius:12px;text-align:center;color:white;font-weight:bold;font-size:16px;line-height:1.4;">Flood Warning<br><span style="font-size:18px;">No</span></div>', unsafe_allow_html=True)
#         with col6:
#             st.markdown('<div style="background-color:#ffcc00;padding:10px;border-radius:8px;text-align:center;color:black;font-weight:bold;">Fire Warning<br>Low</div>', unsafe_allow_html=True)
        
#         molokai_map = folium.Map(location=[21.1333, -157.0167], zoom_start=10, tiles=None, min_zoom=6, max_bounds=True)
#         folium.TileLayer('Esri.WorldImagery').add_to(molokai_map)
#         # folium.Marker([21.0889, -157.0125], popup='Kaunakakai').add_to(molokai_map)
#         folium_static(molokai_map)

#     elif selected_page == 'Lānaʻi':
#         st.markdown('''
#         # Weather Data Dashboard - ***Lānaʻi***
#         > Lānaʻi, the smallest publicly accessible inhabited island in Hawaii...
#         ---
#         ''')
#          # Climate Metrics Displayed Horizontally with color indicators
#         col1, col2, col3, col4, col5, col6 = st.columns(6)
#         with col1:
#             st.metric("Avg Daily Precip", "3.2 mm", "+12%")
#         with col2:
#             st.metric("Avg Max Temp", "29.5 °C", "-1.2 °C")
#         with col3:
#             st.metric("Avg Min Temp", "22.3 °C", "+0.5 °C")
#         with col4:
#             st.metric("Avg Humidity", "77%", "+3%")
#         with col5:
#             st.markdown('<div style="background-color:#34c759;padding:5px 10px;border-radius:12px;text-align:center;color:white;font-weight:bold;font-size:16px;line-height:1.4;">Flood Warning<br><span style="font-size:18px;">No</span></div>', unsafe_allow_html=True)
#         with col6:
#             st.markdown('<div style="background-color:#ffcc00;padding:10px;border-radius:8px;text-align:center;color:black;font-weight:bold;">Fire Warning<br>Low</div>', unsafe_allow_html=True)
        
#         lanai_map = folium.Map(location=[20.8333, -156.9167], zoom_start=11, tiles=None, min_zoom=6, max_bounds=True)
#         folium.TileLayer('Esri.WorldImagery').add_to(lanai_map)
#         # folium.Marker([20.8275, -156.9208], popup='Lānaʻi City').add_to(lanai_map)
#         folium_static(lanai_map)

#     elif selected_page == 'Maui':
#         st.markdown('''
#         # Weather Data Dashboard - ***Maui***
#         > Maui is known for its beaches, the sacred ʻĪao Valley, and the scenic Hana Highway...
#         ---
#         ''')
#          # Climate Metrics Displayed Horizontally with color indicators
#         col1, col2, col3, col4, col5, col6 = st.columns(6)
#         with col1:
#             st.metric("Avg Daily Precip", "3.2 mm", "+12%")
#         with col2:
#             st.metric("Avg Max Temp", "29.5 °C", "-1.2 °C")
#         with col3:
#             st.metric("Avg Min Temp", "22.3 °C", "+0.5 °C")
#         with col4:
#             st.metric("Avg Humidity", "77%", "+3%")
#         with col5:
#             st.markdown('<div style="background-color:#34c759;padding:5px 10px;border-radius:12px;text-align:center;color:white;font-weight:bold;font-size:16px;line-height:1.4;">Flood Warning<br><span style="font-size:18px;">No</span></div>', unsafe_allow_html=True)
#         with col6:
#             st.markdown('<div style="background-color:#ffcc00;padding:10px;border-radius:8px;text-align:center;color:black;font-weight:bold;">Fire Warning<br>Low</div>', unsafe_allow_html=True)
        
#         maui_map = folium.Map(location=[20.8, -156.3], zoom_start=10, tiles=None, min_zoom=6, max_bounds=True)
#         folium.TileLayer('Esri.WorldImagery').add_to(maui_map)
#         # folium.Marker([20.8895, -156.4729], popup='Kahului').add_to(maui_map)
#         folium_static(maui_map)

#     elif selected_page == 'Hawaiʻi (Big Island)':
#         st.markdown('''
#         # Weather Data Dashboard - ***Hawaiʻi (Big Island)***
#         > The Big Island is the largest in the Hawaiian archipelago and features diverse climates and active volcanoes...
#         ---
#         ''')
#          # Climate Metrics Displayed Horizontally with color indicators
#         col1, col2, col3, col4, col5, col6 = st.columns(6)
#         with col1:
#             st.metric("Avg Daily Precip", "3.2 mm", "+12%")
#         with col2:
#             st.metric("Avg Max Temp", "29.5 °C", "-1.2 °C")
#         with col3:
#             st.metric("Avg Min Temp", "22.3 °C", "+0.5 °C")
#         with col4:
#             st.metric("Avg Humidity", "77%", "+3%")
#         with col5:
#             st.markdown('<div style="background-color:#34c759;padding:5px 10px;border-radius:12px;text-align:center;color:white;font-weight:bold;font-size:16px;line-height:1.4;">Flood Warning<br><span style="font-size:18px;">No</span></div>', unsafe_allow_html=True)
#         with col6:
#             st.markdown('<div style="background-color:#ffcc00;padding:10px;border-radius:8px;text-align:center;color:black;font-weight:bold;">Fire Warning<br>Low</div>', unsafe_allow_html=True)
        
#         bigisland_map = folium.Map(location=[19.6, -155.5], zoom_start=8.4, tiles=None, min_zoom=6, max_bounds=True)
#         folium.TileLayer('Esri.WorldImagery').add_to(bigisland_map)
#         # folium.Marker([19.7297, -155.09], popup='Hilo').add_to(bigisland_map)
#         # folium.Marker([19.6406, -155.9956], popup='Kailua-Kona').add_to(bigisland_map)
#         folium_static(bigisland_map)


with chat_col:
    st.markdown("""
    <style>
    /* Positioning the expander fixed to the bottom-right */
    div[data-testid="stExpander"] {
        position: fixed;
        bottom: 0;
        right: 0;
        width: 25%;
        z-index: 1000;
    }

    /* Increasing font size inside expander content */
    div[data-testid="stExpander"] div[data-testid="stMarkdownContainer"] p {
        font-size: 25px !important;
    }

    /* Increasing font size inside input box */
    div[data-testid="stExpander"] input[type="text"] {
        font-size: 18px !important;
    }

    /* Increasing font size for expander header (title) */
    div[data-testid="stExpander"] summary {
        font-size: 20px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.expander("🌐 Kai Climate Helper", expanded=True):
        # Initialize chat history if not present
        chat_history = st.session_state.setdefault("chat_history", [])

        # Set default system message
        if not chat_history:
            chat_history.append({"role": "assistant", "content": "Hi! Ask me anything about Hawaii's climate."})

        # Display chat messages
        for msg in chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # User input
        user_input = st.chat_input("Ask about Hawaii climate")

        # Handle new user input
        if user_input:
            # Add user message to chat
            st.chat_message("user").markdown(user_input)
            chat_history.append({"role": "user", "content": user_input})

            bot_reply = "This is a placeholder answer. Replace with actual model output."

            # Add assistant response to chat
            st.chat_message("assistant").markdown(bot_reply)
            chat_history.append({"role": "assistant", "content": bot_reply})
