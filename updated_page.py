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

# --- Island Mapping Function ---
def show_island_map(island_name, location, zoom):
    """Displays a map of the specified Hawaiian island."""
    island_map = folium.Map(
        location=location,
        zoom_start=zoom,
        tiles=None,
        min_zoom=6,
        max_bounds=True
    )
    folium.TileLayer('Esri.WorldImagery').add_to(island_map)
    folium_static(island_map)
    st.markdown(f"## {island_name}")

# --- All Islands Map Function ---
def show_all_islands_map(islands_data):
    """Displays a map of all Hawaiian Islands with labels."""
    # Define bounding box for Hawaiian Islands
    bounds = [[18.5, -161.0], [21.9, -154.5]]
    all_islands_map = folium.Map(
        location=[20.5, -157.5],  # Approximate center
        zoom_start=6,
        tiles=None,
        min_zoom=6,
        max_bounds=True
    )
    folium.TileLayer('Esri.WorldImagery').add_to(all_islands_map)

    for name, data in islands_data.items():
        folium.map.Marker(
            location=data['coords'],
            icon=folium.DivIcon(
                html=f'<div style="font-size: 20px; color: white; font-weight: bold; text-shadow: 1px 1px 2px black;">{name}</div><div style="font-size: 12px; color: yellow; text-shadow: 1px 1px 2px black;">{", ".join(data["cities"])}</div>'
            )
        ).add_to(all_islands_map)

    all_islands_map.fit_bounds(bounds)
    folium_static(all_islands_map)
    st.markdown("## All Hawaiian Islands")

# --- Island Data ---
islands_data = {
    'Kauaʻi': {'coords': [22.03, -159.5], 'zoom': 8, 'cities': ['Līhuʻe', 'Kapaʻa']},
    'Oʻahu': {'coords': [21.4389, -158.0], 'zoom': 9, 'cities': ['Honolulu', 'Kailua', 'Pearl City']},
    'Molokaʻi': {'coords': [21.1333, -157.0167], 'zoom': 9, 'cities': ['Kaunakakai']},
    'Lānaʻi': {'coords': [20.8333, -156.9167], 'zoom': 10, 'cities': ['Lānaʻi City']},
    'Maui': {'coords': [20.8, -156.3], 'zoom': 8, 'cities': ['Kahului', 'Lahaina', 'Kīhei']},
    'Hawaiʻi (Big Island)': {'coords': [19.6, -155.5], 'zoom': 7, 'cities': ['Hilo', 'Kona']}
}

# Sidebar
st.sidebar.title('Hawaii Climate Data')
image = 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Hawaii_islands_map-en.svg/1280px-Hawaii_islands_map-en.svg.png'
st.sidebar.image(image)
st.sidebar.markdown('''
> Explore climate data for the beautiful Hawaiian Islands.
---
''')
selected_island = st.sidebar.selectbox(
    'Select an Island:', list(islands_data.keys()) + ['All Islands'])
st.sidebar.markdown(
    'Explore interactive maps of the Hawaiian Islands.')
st.sidebar.markdown('''---''')
st.sidebar.title('Other Cities (for comparison)')
other_city = st.sidebar.selectbox(
    'Select a City:', ['Delhi', 'Kuala Lumpur', 'Singapore', 'Tokyo'])
st.sidebar.markdown(
    'Here is an analysis of the weather data for four cities in Asia for 20 years.')


# Main Dashboard and chatbot
main_col, chat_col = st.columns([4,1])

with main_col:
    # Main Dashboard
    if selected_island == 'All Islands':
        st.markdown('''
        # Hawaiian Islands Overview
        > A map showcasing all the main Hawaiian Islands with labels for their names and popular cities.
        ---
        ''')
        show_all_islands_map(islands_data)
    elif selected_island in islands_data:
        island = islands_data[selected_island]
        show_island_map(selected_island, island['coords'], island['zoom'])
    elif other_city == 'Delhi':
        st.markdown('''
        # Weather Dashboard - ***Delhi***
        > Delhi, the capital of India, is one of the most populous and polluted cities in the world. The city has changed a lot over the years with respect to its weather. There have been a number of factors that have contributed to this change, including climate change. Here is a dashboard for the analysis of weather data for 20 years.
        ---
        ''')
        rt_chart(Delhi)
    elif other_city == 'Kuala Lumpur':
        st.markdown('''
        # Weather Data Dashboard - ***Kuala Lumpur***
        > Kaula Lumpur, the capital city of Malaysia, home to the iconic Twin Towers. Kuala Lumpur is best known for its affordable luxury hotels, great shopping scene, and even better food. Malaysian capital boasts some of the finest shopping centers in the world, head towards Pavilion KL and Suria KLC for high-end luxurious items, or visit Petaling Street to have a real sense of local shopping. The city has changed a lot over the years with respect to its weather. There have been a number of factors that have contributed to this change, including climate change. Here is a dashboard for the analysis of weather data for 20 years.
        ---
        ''')
        rt_chart(kuala_lumpur)
    elif other_city == 'Singapore':
        st.markdown('''
        # Weather Data Dashboard - ***Singapore***
        > Singapore, officially the Republic of Singapore, is a sovereign island country and city-state in maritime Southeast Asia. It is famous for being a global financial center, being among the most densely populated places in the world, having a world-class city airport with a waterfall, and a Botanic Garden that is a World Heritage Site. The city has changed a lot over the years with respect to its weather. Here is a dashboard for the analysis of weather data for 20 years.
        ''')
        rt_chart(Singapore)
    elif other_city == 'Tokyo':
        st.markdown('''
        # Weather Data Dashboard - ***Tokyo***
        > Tokyo, Japan’s busy capital, mixes the ultramodern and the traditional...
        ''')
        rt_chart(Tokyo)


with chat_col:
    st.markdown("""<style>
                .stExpander {
                    position: fixed;
                    bottom: 0;
                    right: 0;
                    width: 25%;
                    font-size: 25px;
                }
                </style>""", unsafe_allow_html=True)
    with st.expander("🌐 Climate Chatbot", expanded=True):
        if 'chat_history' not in st.session_state:
            st.session_state['chat_history'] = []

        for chat in st.session_state['chat_history']:
            role = "You" if chat['role'] == 'user' else "Bot"
            st.markdown(f"**{role}:** {chat['content']}")

        user_input = st.text_input("Ask about climate:", key="user_input")

        def get_bot_response(query):
            # api_url = "https://your-backend-api.com/chat"
            # response = requests.post(api_url, json={'query': query})
            # return response.json().get('answer', 'Error contacting backend.') if response.ok else "Error contacting backend."
            return "This is a placeholder response. Replace with actual API call."

        if user_input:
            st.session_state['chat_history'].append({'role': 'user', 'content': user_input})
            bot_response = get_bot_response(user_input)
            st.session_state['chat_history'].append({'role': 'bot', 'content': bot_response})
            st.experimental_rerun()