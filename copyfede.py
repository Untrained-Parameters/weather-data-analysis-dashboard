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
from datetime import datetime
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go
import warnings
from streamlit_extras.stylable_container import stylable_container
import data_function
from vega_datasets import data


# setting page configuration
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

# Sidebar

st.sidebar.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@700&family=Inter:wght@400&display=swap');

    .sidebar-title {
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 35px;
        text-align: center;
        margin-bottom: 30px;
    }
    </style>

    <div class="sidebar-title">
        🌴 Hawaiʻi Climate Explorer
    </div>
    """,
    unsafe_allow_html=True
)


st.sidebar.markdown("### Location")
# st.session_state.selected_island = st.sidebar.selectbox("Select Island", ["Kauaʻi", "Oʻahu", "Molokaʻi", "Lānaʻi", "Maui", "Hawaiʻi (Big Island)"])
selected_page = st.sidebar.selectbox('Select a Page:', ('All Islands', 'Kauaʻi', 'Oʻahu', 'Molokaʻi', 'Lānaʻi', 'Maui', 'Hawaiʻi (Big Island)'))

metric_view = st.sidebar.radio("Select View:", ["Daily", "Monthly"])

if metric_view == "Daily":
    st.sidebar.markdown("### Date")
    st.session_state.date_input = st.sidebar.text_input("Enter Date (MM/DD/YYYY)", "01/01/2025")
else:
    st.sidebar.markdown("### Date")
    st.session_state.date_input = st.sidebar.text_input("Enter Date (MM/YYYY)","01/01/2025")

st.sidebar.markdown("### Display Type")
if selected_page != 'All Islands':
    display_type = st.sidebar.radio("Choose Data", ["General Overview", 
        "Rainfall", "Temperature", "Humidity", "NVDI", "Ignition Probability",
        "Future Climate Predictions", "Contemporary Climatology", "Legacy Climatology"])
else:
    display_type = st.sidebar.radio("Choose Data", [ 
        "Rainfall", "Temperature", "Humidity", "NVDI", "Ignition Probability",
        "Future Climate Predictions", "Contemporary Climatology", "Legacy Climatology"])

def plot_chart(date_input=st.session_state.date_input, island_name="Oahu", variable="rainfall"):
    chart_data = data_function.get_station_data_for_period(date_input, island_name, variable)
    if island_name=='Oahu':
        lati = 21.44
        longi = -157.9
        zoom = 9.5
    elif island_name=='Kauai':
        lati = 22.1
        longi = -159.5
        zoom = 10
    elif island_name=='Molokai':
        lati = 21.13
        longi = -157.02
        zoom = 10
    elif island_name=='Maui':
        lati = 20.8
        longi = -156.3
        zoom = 10
    elif island_name=='Lānai':
        lati = 20.83
        longi = -156.92
        zoom = 10
    elif island_name=='Hawaii (Big Island)':
        lati = 18.9
        longi = -156.1
        zoom = 10
    elif island_name=='All':
        lati = 20.5
        longi = -157
        zoom = 7

    
    st.pydeck_chart(
        pdk.Deck(
            map_style='mapbox://styles/mapbox/satellite-v9',
            initial_view_state=pdk.ViewState(
                latitude=lati,
                longitude=longi,
                zoom=zoom,
                pitch=50,
            ),
            layers=[
                pdk.Layer(
                    "HexagonLayer",
                    data=chart_data,
                    get_position="[lon, lat]",
                    auto_highlight=True,
                    radius=300,
                    elevation_scale=100*np.median(chart_data[variable]),
                    get_elevation_weight=variable,
                    elevation_range=[np.min(chart_data[variable]),np.max(chart_data[variable])],
                    coverage=1,
                    pickable=True,
                    extruded=True,
                    # color_range=[
                    #     [1, 152, 189],
                    #     [73, 227, 206],
                    #     [216, 254, 181],
                    #     [254, 237, 177],
                    #     [254, 173, 84],
                    #     [209, 55, 78],
                    # ],
                ),
            ],
            tooltip={
                "text": f"{variable}: {{elevationValue}}",
                "style": {
                    "backgroundColor": "#206af1",
                    "color": "white",
                },
            },
        ),
    )

#Main Dashboard
main_col, chat_col = st.columns([4,1])

# Function to show chart
def get_chart_98185(use_container_width: bool):

    source = data.seattle_weather.url
    step = 20
    overlap = 1

    chart = alt.Chart(source, height=step).transform_timeunit(
        Month='month(date)'
    ).transform_joinaggregate(
        mean_temp='mean(temp_max)', groupby=['Month']
    ).transform_bin(
        ['bin_max', 'bin_min'], 'temp_max'
    ).transform_aggregate(
        value='count()', groupby=['Month', 'mean_temp', 'bin_min', 'bin_max']
    ).transform_impute(
        impute='value', groupby=['Month', 'mean_temp'], key='bin_min', value=0
    ).mark_area(
        interpolate='monotone',
        fillOpacity=0.8,
        stroke='lightgray',
        strokeWidth=0.5
    ).encode(
        alt.X('bin_min:Q', bin='binned', title='Maximum Daily Temperature (C)'),
        alt.Y(
            'value:Q',
            scale=alt.Scale(range=[step, -step * overlap]),
            axis=None
        ),
        alt.Fill(
            'mean_temp:Q',
            legend=None,
            scale=alt.Scale(domain=[30, 5], scheme='redyellowblue')
        )
    ).facet(
        row=alt.Row(
            'Month:T',
            title=None,
            header=alt.Header(labelAngle=0, labelAlign='right', format='%B')
        )
    ).properties(
        title='Seattle Weather',
        bounds='flush'
    ).configure_facet(spacing=0).configure_view(stroke=None).configure_title(anchor='end')

    tab1, tab2 = st.tabs(["Streamlit theme (default)", "Altair native theme"])
    with tab1:
        st.altair_chart(chart, theme="streamlit", use_container_width=use_container_width)
    with tab2:
        st.altair_chart(chart, theme=None, use_container_width=use_container_width)

# Initialize state
if "active_view" not in st.session_state:
    st.session_state.active_view = "map"

with main_col:
    if selected_page == 'All Islands':
        st.markdown('''
        # Hawaiian Islands Overview
        > Explore climate data in the main islands of Hawaiʻi. 
        ---
        ''')

        # Create 3 columns: left button, center message, right button
        left_col, center_col, right_col = st.columns([1, 3, 1])

        with left_col:
            if st.button("📍 Show Map"):
                st.session_state.active_view = "map"

        with center_col:
            st.markdown("<div style='text-align: center; font-size: 26px'>⬅️ &nbsp; <strong>Choose how to visualize the data</strong> &nbsp; ➡️</div>", unsafe_allow_html=True)

        with right_col:
            if st.button("📊 Show Graph"):
                st.session_state.active_view = "graph"


        # Display the appropriate view
        if st.session_state.active_view == "map":
            if display_type=="Rainfall":
                plot_chart(date_input=st.session_state.date_input, island_name="All", variable="rainfall")
            elif display_type=="Temperature":
                plot_chart(date_input=st.session_state.date_input, island_name="All", variable="temperature")
            elif display_type=='General Overview':
                pdk.Deck(
                map_style='mapbox://styles/mapbox/satellite-v9',
                initial_view_state=pdk.ViewState(
                latitude=20.5,
                longitude=-157,
                zoom=7,
                pitch=50,
                ),
            )

        elif st.session_state.active_view == "graph":
            get_chart_98185(use_container_width=True)

        # Continue with the rest of your content
        # if display_type == "General Overview":
        #     plot_chart()
        
# with main_col:
#     # Default Homepage Map if no selection yet or fallback
#     if selected_page == 'All Islands':
#         st.markdown('''
#         # Hawaiian Islands Overview
#         > Explore climate data in the main islands of Hawaiʻi. 
#         ---
#         ''')
#         # bounds = [[18.5, -161.0], [22.25, -154.5]]
#         # all_map = folium.Map(location=[20.5, -157.0], zoom_start=7, tiles=None, min_zoom=6, max_bounds=True)
#         # folium.TileLayer('Esri.WorldImagery').add_to(all_map)

#         # islands_info = {
#         #     "Kauaʻi": [22.1, -159.5],
#         #     'Oʻahu': [21.4389, -158.0],
#         #     'Molokaʻi': [21.1333, -157.0167],
#         #     'Lānaʻi': [20.8333, -156.9167],
#         #     'Maui': [20.8, -156.3],
#         #     'Hawaiʻi (Big Island)': [19.6, -155.5]
#         # }
#         # for name, coords in islands_info.items():
#         #     folium.map.Marker(
#         #         location=coords,
#         #         icon=folium.DivIcon(
#         #             html=f'<div style="font-size:16px;color:white;font-weight:bold;text-shadow:1px 1px 2px black;">{name}</div>'
#         #         )
#         #     ).add_to(all_map)

#         # all_map.fit_bounds(bounds)
#         # folium_static(all_map)

#         if display_type=="General Overview":
#             plot_chart()
#         elif display_type=="Rainfall":
#             plot_chart(weight_column='rainfall')
#         elif display_type=="Temperature":
#             plot_chart(weight_column='avg-temp')

    # Main Dashboard (only new blocks for each island below)
    # today = datetime.today()
    if selected_page == 'Oʻahu':
        page_title = f"Weather Dashboard for Oʻahu" if display_type == "General Overview" else f"{display_type} in Oʻahu"
        st.markdown(f'''
        # {page_title}
        > Oʻahu, known as "The Gathering Place," is the third-largest of the Hawaiian Islands...
        ---
        ''')
        if display_type == "General Overview":
            # Conditional Metrics Based on View
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            if metric_view == "Daily":
                with col1:
                    st.metric("Daily Precip", "3.2 mm","10%")
                with col2:
                    st.metric("Max Temp", "30.1 °C","2%")
                with col3:
                    st.metric("Min Temp", "21.7 °C","-4%")
                with col4:
                    st.metric("Humidity", "75%","12%")
                with col5:
                    st.markdown('<div style="background-color:#34c759;padding:16px 10px;border-radius:10px;text-align:center;color:white;font-weight:bold;font-size:16px;line-height:1.4;">Flood Warning<br><span style="font-size:18px;">No</span></div>', unsafe_allow_html=True)
                with col6:
                    st.markdown('<div style="background-color:#ffcc00;padding:10px;border-radius:8px;text-align:center;color:black;font-weight:bold;">Fire Warning<br>Low</div>', unsafe_allow_html=True)
            else:
                with col1:
                    st.metric("Monthly Precip", "85 mm","13%")
                with col2:
                    st.metric("Avg Max Temp", "29.5 °C","5%")
                with col3:
                    st.metric("Avg Min Temp", "22.3 °C","10%")
                with col4:
                    st.metric("Avg Humidity", "77%","11%")
                with col5:
                    st.markdown('<div style="background-color:#34c759;padding:16px 10px;border-radius:10px;text-align:center;color:white;font-weight:bold;font-size:16px;line-height:1.4;">Flood Warning<br><span style="font-size:18px;">No</span></div>', unsafe_allow_html=True)
                with col6:
                    st.markdown('<div style="background-color:#ffcc00;padding:10px;border-radius:8px;text-align:center;color:black;font-weight:bold;">Fire Warning<br>Low</div>', unsafe_allow_html=True)
            oahu_map = folium.Map(location=[21.4389, -158.0], zoom_start=9, tiles=None, min_zoom=6, max_bounds=True)
            folium.TileLayer('Esri.WorldImagery').add_to(oahu_map)
            folium_static(oahu_map)
        elif display_type=="Rainfall":
            plot_chart(date_input=st.session_state.date_input, island_name="Oahu", variable="rainfall")
        elif display_type=="Temperature":
            plot_chart(date_input=st.session_state.date_input, island_name="Oahu", variable="temperature")


    elif selected_page == "Kauaʻi":
        page_title = f"Weather Dashboard for Kauaʻi" if display_type == "General Overview" else f"{display_type} in Kauaʻi"
        st.markdown(f'''
        # {page_title}
        > Kauaʻi, also known as the Garden Isle, is the oldest of the main Hawaiian Islands...
        ---
        ''')
        if display_type == "General Overview":
            # Conditional Metrics Based on View
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            if metric_view == "Daily":
                with col1:
                    st.metric("Daily Precip", "3.2 mm","10%")
                with col2:
                    st.metric("Max Temp", "30.1 °C","2%")
                with col3:
                    st.metric("Min Temp", "21.7 °C","-4%")
                with col4:
                    st.metric("Humidity", "75%","12%")
                with col5:
                    st.markdown('<div style="background-color:#34c759;padding:16px 10px;border-radius:10px;text-align:center;color:white;font-weight:bold;font-size:16px;line-height:1.4;">Flood Warning<br><span style="font-size:18px;">No</span></div>', unsafe_allow_html=True)
                with col6:
                    st.markdown('<div style="background-color:#ffcc00;padding:10px;border-radius:8px;text-align:center;color:black;font-weight:bold;">Fire Warning<br>Low</div>', unsafe_allow_html=True)
            else:
                with col1:
                    st.metric("Monthly Precip", "85 mm","13%")
                with col2:
                    st.metric("Avg Max Temp", "29.5 °C","5%")
                with col3:
                    st.metric("Avg Min Temp", "22.3 °C","10%")
                with col4:
                    st.metric("Avg Humidity", "77%","11%")
                with col5:
                    st.markdown('<div style="background-color:#34c759;padding:16px 10px;border-radius:10px;text-align:center;color:white;font-weight:bold;font-size:16px;line-height:1.4;">Flood Warning<br><span style="font-size:18px;">No</span></div>', unsafe_allow_html=True)
                with col6:
                    st.markdown('<div style="background-color:#ffcc00;padding:10px;border-radius:8px;text-align:center;color:black;font-weight:bold;">Fire Warning<br>Low</div>', unsafe_allow_html=True)
            kauai_map = folium.Map(location=[22.1, -159.5], zoom_start=10, tiles=None, min_zoom=6, max_bounds=True)
            folium.TileLayer('Esri.WorldImagery').add_to(kauai_map)
            folium_static(kauai_map)
        else:
            kauai_map = folium.Map(location=[22.1, -159.5], zoom_start=10, tiles=None, min_zoom=6, max_bounds=True)
            folium.TileLayer('Esri.WorldImagery').add_to(kauai_map)
            folium_static(kauai_map)

    elif selected_page == 'Molokaʻi':
        page_title = f"Weather Dashboard for Molokaʻi" if display_type == "General Overview" else f"{display_type} in Molokaʻi"
        st.markdown(f'''
        # {page_title}
        > Molokaʻi is known for its high sea cliffs and rural lifestyle...
        ---
        ''')
        if display_type == "General Overview":
            # Conditional Metrics Based on View
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            if metric_view == "Daily":
                with col1:
                    st.metric("Daily Precip", "3.2 mm","10%")
                with col2:
                    st.metric("Max Temp", "30.1 °C","2%")
                with col3:
                    st.metric("Min Temp", "21.7 °C","-4%")
                with col4:
                    st.metric("Humidity", "75%","12%")
                with col5:
                    st.markdown('<div style="background-color:#34c759;padding:16px 10px;border-radius:10px;text-align:center;color:white;font-weight:bold;font-size:16px;line-height:1.4;">Flood Warning<br><span style="font-size:18px;">No</span></div>', unsafe_allow_html=True)
                with col6:
                    st.markdown('<div style="background-color:#ffcc00;padding:10px;border-radius:8px;text-align:center;color:black;font-weight:bold;">Fire Warning<br>Low</div>', unsafe_allow_html=True)
            else:
                with col1:
                    st.metric("Monthly Precip", "85 mm","13%")
                with col2:
                    st.metric("Avg Max Temp", "29.5 °C","5%")
                with col3:
                    st.metric("Avg Min Temp", "22.3 °C","10%")
                with col4:
                    st.metric("Avg Humidity", "77%","11%")
                with col5:
                    st.markdown('<div style="background-color:#34c759;padding:16px 10px;border-radius:10px;text-align:center;color:white;font-weight:bold;font-size:16px;line-height:1.4;">Flood Warning<br><span style="font-size:18px;">No</span></div>', unsafe_allow_html=True)
                with col6:
                    st.markdown('<div style="background-color:#ffcc00;padding:10px;border-radius:8px;text-align:center;color:black;font-weight:bold;">Fire Warning<br>Low</div>', unsafe_allow_html=True)
            molokai_map = folium.Map(location=[21.1333, -157.0167], zoom_start=10, tiles=None, min_zoom=6, max_bounds=True)
            folium.TileLayer('Esri.WorldImagery').add_to(molokai_map)
            folium_static(molokai_map)
        else:
            molokai_map = folium.Map(location=[21.1333, -157.0167], zoom_start=10, tiles=None, min_zoom=6, max_bounds=True)
            folium.TileLayer('Esri.WorldImagery').add_to(molokai_map)
            folium_static(molokai_map)

    elif selected_page == 'Lānaʻi':
        page_title = f"Weather Dashboard for Lānaʻi" if display_type == "General Overview" else f"{display_type} in Lānaʻi"
        st.markdown(f'''
        # {page_title}
        > Lānaʻi, the smallest publicly accessible inhabited island in Hawaii...
        ---
        ''')
        if display_type == "General Overview":
            # Conditional Metrics Based on View
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            if metric_view == "Daily":
                with col1:
                    st.metric("Daily Precip", "3.2 mm","10%")
                with col2:
                    st.metric("Max Temp", "30.1 °C","2%")
                with col3:
                    st.metric("Min Temp", "21.7 °C","-4%")
                with col4:
                    st.metric("Humidity", "75%","12%")
                with col5:
                    st.markdown('<div style="background-color:#34c759;padding:16px 10px;border-radius:10px;text-align:center;color:white;font-weight:bold;font-size:16px;line-height:1.4;">Flood Warning<br><span style="font-size:18px;">No</span></div>', unsafe_allow_html=True)
                with col6:
                    st.markdown('<div style="background-color:#ffcc00;padding:10px;border-radius:8px;text-align:center;color:black;font-weight:bold;">Fire Warning<br>Low</div>', unsafe_allow_html=True)
            else:
                with col1:
                    st.metric("Monthly Precip", "85 mm","13%")
                with col2:
                    st.metric("Avg Max Temp", "29.5 °C","5%")
                with col3:
                    st.metric("Avg Min Temp", "22.3 °C","10%")
                with col4:
                    st.metric("Avg Humidity", "77%","11%")
                with col5:
                    st.markdown('<div style="background-color:#34c759;padding:16px 10px;border-radius:10px;text-align:center;color:white;font-weight:bold;font-size:16px;line-height:1.4;">Flood Warning<br><span style="font-size:18px;">No</span></div>', unsafe_allow_html=True)
                with col6:
                    st.markdown('<div style="background-color:#ffcc00;padding:10px;border-radius:8px;text-align:center;color:black;font-weight:bold;">Fire Warning<br>Low</div>', unsafe_allow_html=True)
            lanai_map = folium.Map(location=[20.8333, -156.9167], zoom_start=11, tiles=None, min_zoom=6, max_bounds=True)
            folium.TileLayer('Esri.WorldImagery').add_to(lanai_map)
            folium_static(lanai_map)
        else:
            lanai_map = folium.Map(location=[20.8333, -156.9167], zoom_start=11, tiles=None, min_zoom=6, max_bounds=True)
            folium.TileLayer('Esri.WorldImagery').add_to(lanai_map)
            folium_static(lanai_map)

    elif selected_page == 'Maui':
        page_title = f"Weather Dashboard for Maui" if display_type == "General Overview" else f"{display_type} in Maui"
        st.markdown(f'''
        # {page_title}
        > Maui is known for its beaches, the sacred ʻĪao Valley, and the scenic Hana Highway...
        ---
        ''')
        if display_type == "General Overview":
            # Conditional Metrics Based on View
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            if metric_view == "Daily":   
                with col1:
                    st.metric("Daily Precip", "3.2 mm","10%")
                with col2:
                    st.metric("Max Temp", "30.1 °C","2%")
                with col3:
                    st.metric("Min Temp", "21.7 °C","-4%")
                with col4:
                    st.metric("Humidity", "75%","12%")
                with col5:
                    st.markdown('<div style="background-color:#34c759;padding:16px 10px;border-radius:10px;text-align:center;color:white;font-weight:bold;font-size:16px;line-height:1.4;">Flood Warning<br><span style="font-size:18px;">No</span></div>', unsafe_allow_html=True)
                with col6:
                    st.markdown('<div style="background-color:#ffcc00;padding:10px;border-radius:8px;text-align:center;color:black;font-weight:bold;">Fire Warning<br>Low</div>', unsafe_allow_html=True)
            else:
                with col1:
                    st.metric("Monthly Precip", "85 mm","13%")
                with col2:
                    st.metric("Avg Max Temp", "29.5 °C","5%")
                with col3:
                    st.metric("Avg Min Temp", "22.3 °C","10%")
                with col4:
                    st.metric("Avg Humidity", "77%","11%")
                with col5:
                    st.markdown('<div style="background-color:#34c759;padding:16px 10px;border-radius:10px;text-align:center;color:white;font-weight:bold;font-size:16px;line-height:1.4;">Flood Warning<br><span style="font-size:18px;">No</span></div>', unsafe_allow_html=True)
                with col6:
                    st.markdown('<div style="background-color:#ffcc00;padding:10px;border-radius:8px;text-align:center;color:black;font-weight:bold;">Fire Warning<br>Low</div>', unsafe_allow_html=True)
            maui_map = folium.Map(location=[20.8, -156.3], zoom_start=10, tiles=None, min_zoom=6, max_bounds=True)
            folium.TileLayer('Esri.WorldImagery').add_to(maui_map)
            folium_static(maui_map)
        else:
            maui_map = folium.Map(location=[20.8, -156.3], zoom_start=10, tiles=None, min_zoom=6, max_bounds=True)
            folium.TileLayer('Esri.WorldImagery').add_to(maui_map)
            folium_static(maui_map)

    elif selected_page == 'Hawaiʻi (Big Island)':
        page_title = f"Weather Dashboard for Hawaiʻi (Big Island)" if display_type == "General Overview" else f"{display_type} in Hawaiʻi (Big Island)"
        st.markdown(f'''
        # {page_title}
        > The Big Island is the largest in the Hawaiian archipelago and features diverse climates and active volcanoes...
        ---
        ''')
        if display_type == "General Overview":
            # Conditional Metrics Based on View
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            if metric_view == "Daily":   
                with col1:
                    st.metric("Daily Precip", "3.2 mm","10%")
                with col2:
                    st.metric("Max Temp", "30.1 °C","2%")
                with col3:
                    st.metric("Min Temp", "21.7 °C","-4%")
                with col4:
                    st.metric("Humidity", "75%","12%")
                with col5:
                    st.markdown('<div style="background-color:#34c759;padding:16px 10px;border-radius:10px;text-align:center;color:white;font-weight:bold;font-size:16px;line-height:1.4;">Flood Warning<br><span style="font-size:18px;">No</span></div>', unsafe_allow_html=True)
                with col6:
                    st.markdown('<div style="background-color:#ffcc00;padding:10px;border-radius:8px;text-align:center;color:black;font-weight:bold;">Fire Warning<br>Low</div>', unsafe_allow_html=True)
            else:
                with col1:
                    st.metric("Monthly Precip", "85 mm","13%")
                with col2:
                    st.metric("Avg Max Temp", "29.5 °C","5%")
                with col3:
                    st.metric("Avg Min Temp", "22.3 °C","10%")
                with col4:
                    st.metric("Avg Humidity", "77%","11%")
                with col5:
                    st.markdown('<div style="background-color:#34c759;padding:16px 10px;border-radius:10px;text-align:center;color:white;font-weight:bold;font-size:16px;line-height:1.4;">Flood Warning<br><span style="font-size:18px;">No</span></div>', unsafe_allow_html=True)
                with col6:
                    st.markdown('<div style="background-color:#ffcc00;padding:10px;border-radius:8px;text-align:center;color:black;font-weight:bold;">Fire Warning<br>Low</div>', unsafe_allow_html=True)
            bigisland_map = folium.Map(location=[19.6, -155.5], zoom_start=8, tiles=None, min_zoom=6, max_bounds=True)
            folium.TileLayer('Esri.WorldImagery').add_to(bigisland_map)
            folium_static(bigisland_map)
        else:
            bigisland_map = folium.Map(location=[19.6, -155.5], zoom_start=8, tiles=None, min_zoom=6, max_bounds=True)
            folium.TileLayer('Esri.WorldImagery').add_to(bigisland_map)
            folium_static(bigisland_map)


with chat_col:
    st.markdown("""
    <style>
    div[data-testid="stExpander"] {
        position: fixed;
        bottom: 10px;
        right: 10px;
        width: 25%;
        z-index: 1000;
        max-height: 90vh;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        background-color: #f8f9fa;
        color: black;
        border-radius: 15px; /* Added border-radius for rounded corners */
    }

    .scrollable-chat-container {
        flex-grow: 1;
        max-height: 60vh;
        overflow-y: auto;
        padding: 0px;
        border: 0px solid #ccc;
        border-radius: 10px;
        background-color: #f8f9fa;
        margin-bottom: 10px;
        display: flex;
        flex-direction: column;
    }

    .chat-bubble-user {
        background-color: #dee2e6;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
        margin-left: 40px;
        text-align: right;
        font-size: 16px;
        color: #000000;
    }

    .chat-bubble-assistant {
        background-color: #206af1;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
        margin-right: 40px;
        text-align: left;
        font-size: 16px;
        color: white;
    }

    div[data-testid="stExpander"] div[data-testid="stMarkdownContainer"] p {
        font-size: 25px !important;
    }

    div[data-testid="stExpander"] input[type="text"] {
        font-size: 18px !important;
    }

    div[data-testid="stExpander"] summary {
        font-size: 20px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.expander("🌐 Kai Climate Helper", expanded=True):
        chat_history = st.session_state.setdefault("chat_history", [])

        if not chat_history:
            chat_history.append({"role": "assistant", "content": "Hi! Ask me anything about Hawaii's climate."})

        user_input = st.chat_input("Ask about Hawaii climate")

        if user_input:
            chat_history.append({"role": "user", "content": user_input})
            bot_reply = "This is a placeholder answer. Replace with actual model output."
            chat_history.append({"role": "assistant", "content": bot_reply})

        # Scrollable chat area
        chat_html = '<div class="scrollable-chat-container" id="chat-box">'
        for msg in chat_history:
            role_class = "chat-bubble-user" if msg["role"] == "user" else "chat-bubble-assistant"
            chat_html += f'<div class="{role_class}">{msg["content"]}</div>'
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)