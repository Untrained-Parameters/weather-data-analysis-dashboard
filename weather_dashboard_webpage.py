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
st.sidebar.title('Climatic Changes')
image = 'https://www.noaa.gov/sites/default/files/styles/landscape_width_1275/public/2022-03/PHOTO-Climate-Collage-Diagonal-Design-NOAA-Communications-NO-NOAA-Logo.jpg'
st.sidebar.image(image)
st.sidebar.markdown('''
> Climate change refers to long-term shifts in temperatures and weather patterns. It also includes sea level rise, changes in weather patterns like drought and flooding, and much more.
---
''')
selected_page = st.sidebar.selectbox(
    'Select a City:', ('Delhi', 'Kuala Lumpur', 'Singapore', 'Tokyo', 'All Islands', 'Kauaʻi', 'Oʻahu', 'Molokaʻi', 'Lānaʻi', 'Maui', 'Hawaiʻi (Big Island)'))
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
    if selected_page == 'Delhi':
        st.markdown('''
        # Weather Dashboard - ***Delhi*** 
        > Delhi, the capital of India, is one of the most populous and polluted cities in the world. The city has changed a lot over the years with respect to its weather. There have been a number of factors that have contributed to this change, including climate change. Here is a dashboard for the analysis of weather data for 20 years.
        ---
        ''')
        rt_chart(Delhi)
    elif selected_page == 'Kuala Lumpur':
        st.markdown('''
        # Weather Data Dashboard - ***Kuala Lumpur***
        > Kaula Lumpur, the capital city of Malaysia, home to the iconic Twin Towers. Kuala Lumpur is best known for its affordable luxury hotels, great shopping scene, and even better food. Malaysian capital boasts some of the finest shopping centers in the world, head towards Pavilion KL and Suria KLC for high-end luxurious items, or visit Petaling Street to have a real sense of local shopping. The city has changed a lot over the years with respect to its weather. There have been a number of factors that have contributed to this change, including climate change. Here is a dashboard for the analysis of weather data for 20 years.
        ---
        ''')
        rt_chart(kuala_lumpur)
    elif selected_page == 'Singapore':
        st.markdown('''
        # Weather Data Dashboard - ***Singapore***
        > Singapore, officially the Republic of Singapore, is a sovereign island country and city-state in maritime Southeast Asia. It is famous for being a global financial center, being among the most densely populated places in the world, having a world-class city airport with a waterfall, and a Botanic Garden that is a World Heritage Site. The city has changed a lot over the years with respect to its weather. There have been a number of factors that have contributed to this change, including climate change. Here is a dashboard for the analysis of weather data for 20 years.
        ''')
        rt_chart(Singapore)
    elif selected_page == 'Tokyo':
        st.markdown('''
        # Weather Data Dashboard - ***Tokyo***
        > Tokyo, Japan’s busy capital, mixes the ultramodern and the traditional...
        ''')
        rt_chart(Tokyo)
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

    elif selected_page == 'Oʻahu':
        st.markdown('''
        # Weather Data Dashboard - ***Oʻahu***
        > Oʻahu, known as "The Gathering Place," is the third-largest of the Hawaiian Islands...
        ---
        ''')
        bounds = [[18.5, -161.0], [21.9, -154.5]]
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
        bigisland_map = folium.Map(location=[19.6, -155.5], zoom_start=8, tiles=None, min_zoom=6, max_bounds=True)
        folium.TileLayer('Esri.WorldImagery').add_to(bigisland_map)
        folium.Marker([19.7297, -155.09], popup='Hilo').add_to(bigisland_map)
        folium.Marker([19.6406, -155.9956], popup='Kailua-Kona').add_to(bigisland_map)
        folium_static(bigisland_map)




# this is the code that makes a single map of the islands under the tab Oahu
    # elif selected_page == 'Oahu':
    #     st.markdown('''
    #     # Weather Data Dashboard - ***Oahu***
    #     > Oʻahu, known as "The Gathering Place," is the third-largest of the Hawaiian Islands...
    #     ---
    #     ''')
    #     # Define bounding box for Hawaiian Islands
    #     bounds = [[18.5, -161.0], [21.9, -154.5]]
    #     # Create map with Esri tiles
    #     oahu_map = folium.Map(
    #     location=[21.4389, -158.0],
    #     zoom_start=9,
    #     tiles=None,
    #     min_zoom=6,
    #     max_bounds=True)
    #     folium.TileLayer('Esri.WorldImagery').add_to(oahu_map)
    #     folium_static(oahu_map)

    #     # Add island labels
    #     islands = {
    #         'Kauaʻi': [22.1, -159.5],
    #         'Oʻahu': [21.4389, -158.0],
    #         'Molokaʻi': [21.1333, -157.0167],
    #         'Lānaʻi': [20.8333, -156.9167],
    #         'Maui': [20.8, -156.3],
    #         'Hawaiʻi (Big Island)': [19.6, -155.5]
    #         }
    #     for name, coords in islands.items():
    #         folium.map.Marker(
    #             location=coords,
    #             icon=folium.DivIcon(
    #                 html=f'<div style="font-size: 16px; color: white; font-weight: bold; text-shadow: 1px 1px 2px black;">{name}</div>'
    #             )
    #         ).add_to(oahu_map)

    #     # Fit to Hawaiian bounds
    #     oahu_map.fit_bounds(bounds)
    #     folium_static(oahu_map)

    
# with chat_col:
#     st.markdown("""
#                 <style>
#                 .stExpander {
#                     position: fixed;
#                     bottom: 0;
#                     right: 0;
#                     width: 25%;
#                 }
#                 /* Target text inside the expander */
#                 div[data-testid="stExpander"] div[data-testid="stMarkdownContainer"] p {
#                     font-size: 25px !important;
#                 }
#                 /* Target text input inside the expander */
#                 div[data-testid="stExpander"] input {
#                     font-size: 18px !important;
#                 }
#                 </style>
#                 """, unsafe_allow_html=True)
#     with st.expander("🌐 Climate Chatbot", expanded=True):
#         # if 'chat_history' not in st.session_state:
#         #     st.session_state['chat_history'] = []

#         # for chat in st.session_state['chat_history']:
#         #     role = "You" if chat['role'] == 'user' else "Bot"
#         #     st.markdown(f"**{role}:** {chat['content']}")

#         # user_input = st.text_input("Ask about climate:", key="user_input")

#         # def get_bot_response(query):
#         #     # api_url = "https://your-backend-api.com/chat"
#         #     # response = requests.post(api_url, json={'query': query})
#         #     # return response.json().get('answer', 'Error contacting backend.') if response.ok else "Error contacting backend."
#         #     return "This is a placeholder response. Replace with actual API call."

#         # if user_input:
#         #     st.session_state['chat_history'].append({'role': 'user', 'content': user_input})
#         #     bot_response = get_bot_response(user_input)
#         #     st.session_state['chat_history'].append({'role': 'bot', 'content': bot_response})
#         #     st.experimental_rerun()

#         # Model training
#         model_name = "deepset/roberta-base-squad2"

#         # Load model & tokenizer
#         model = AutoModelForQuestionAnswering.from_pretrained(model_name)
#         tokenizer = AutoTokenizer.from_pretrained(model_name)

#         # User input box
#         question = st.text_input("Ask about Hawai`i climate:")

#         # Contextualization
#         context = '''
#                     You are an LLM built to be knowledgeable on a data science project submission to the Rutgers Data Science Fall 23 Datathon 
#                     submitted by Maha, Nikhila, and Nivedha. This is a project about the forecasting. The data set is from GCAG, this is the website 
#                     that has more info on the data: https://www.ncei.noaa.gov/access/monitoring/climate-at-a-glance/national/data-info. 
#                     You are hosted on a Streamlit app. This project is about a forecasting model of global temperatures built using Prophet by Facebook. 
#                     The raw data has Year and Anomaly Column. The anamoly representsanomaly means a departure from a reference value or long-term average. 
#                     A positive anomaly indicates that the observed temperature was warmer than the reference value, while a negative anomaly indicates 
#                     that the observed temperature was cooler than the reference value. The visualizations are built plotly - an interactive python 
#                     plotting library. The github link to the streamlit is: https://github.com/mahakanakala/datathon23_streamlit.
#                     The github link to the model and training of this project is: https://github.com/mahakanakala/datathon23.
#                     The processed data has Year, Anomaly, Month, and Season Column.
#         '''

#         # Intializing deepset/roberta-base-squad2 model and getting answer instances from pipeline
#         if question:
#             nlp = pipeline('question-answering', model=model, tokenizer=tokenizer)
#             QA_input = {
#                 'question': question,
#                 'context': context
#             }
#             answer = nlp(QA_input)
#             st.write("Answer:", answer['answer'])