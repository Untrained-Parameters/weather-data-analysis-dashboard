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
from datetime import datetime
import pydeck as pdk

# setting page configuration
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

# Top navigation bar with tabs
query_params = st.experimental_get_query_params()
top_tab = query_params.get("tab", [None])[0]

st.markdown(f"""
    <style>
    .top-bar {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 50px;
        background-color: #f8f9fa;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 30px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        z-index: 1001;
        transition: background-color 0.3s ease;
    }}
    .top-bar h1 {{
        font-size: 22px;
        color: #1a2c4a;
        margin: 0;
        font-family: 'Segoe UI', sans-serif;
    }}
    .top-bar .nav-links a {{
        margin-left: 20px;
        text-decoration: none;
        color: #1a2c4a;
        font-weight: 500;
        font-size: 16px;
        font-family: 'Segoe UI', sans-serif;
        transition: color 0.2s;
    }}
    .top-bar .nav-links a:hover {{
        text-decoration: underline;
        color: #205493;
    }}
    .top-bar .nav-links .active {{
        font-weight: bold;
        color: #0b3d91;
        text-decoration: underline;
    }}
    </style>
    <div class="top-bar">
        <h1>HI Climate</h1>
        <div class="nav-links">
            <a class="{'active' if top_tab == 'About' else ''}" href="/?tab=About">About</a>
            <a class="{'active' if top_tab == 'Climate tools' else ''}" href="/?tab=Climate+tools">Climate tools</a>
            <a class="{'active' if top_tab == 'Library' else ''}" href="/?tab=Library">Library</a>
            <a class="{'active' if top_tab == 'Research' else ''}" href="/?tab=Research">Research</a>
            <a class="{'active' if top_tab == 'Cultural Resources' else ''}" href="/?tab=Cultural+Resources">Cultural Resources</a>
        </div>
    </div>
    <div style="margin-top: 60px;"></div>
""", unsafe_allow_html=True)

# Render custom content if a top tab is selected
if top_tab:
    st.set_page_config(layout='wide', initial_sidebar_state='collapsed')
    st.markdown(f"""
        <div class='main'>
            <h1 style='font-family:Segoe UI;'>{top_tab}</h1>
    """, unsafe_allow_html=True)

    if top_tab == "About":
        st.write("""
        Welcome to the **HI Climate** platform. This site provides dynamic climate data visualization across the Hawaiian islands.
        Learn about our mission, collaborators, and the impact of climate analysis on policy and education in Hawaiʻi.
        """)
    elif top_tab == "Climate tools":
        st.write("""
        Explore powerful tools for interacting with climate data, generating custom reports, and visualizing temperature, precipitation, and vegetation trends.
        """)
    elif top_tab == "Library":
        st.write("""
        Browse scientific papers, technical documentation, and public resources related to climate modeling and environmental science in Hawaiʻi.
        """)
    elif top_tab == "Research":
        st.write("""
        Discover active research projects led by our team and collaborators, including field studies, simulations, and machine learning applications.
        """)
    elif top_tab == "Cultural Resources":
        st.write("""
        Learn how traditional Hawaiian knowledge intersects with modern climate science, highlighting local stories and cultural stewardship.
        """)

    st.markdown("""</div>""", unsafe_allow_html=True)
    st.stop()


# Sidebar
st.sidebar.markdown("### Location")
# st.session_state.selected_island = st.sidebar.selectbox("Select Island", ["Kauaʻi", "Oʻahu", "Molokaʻi", "Lānaʻi", "Maui", "Hawaiʻi (Big Island)"])
selected_page = st.sidebar.selectbox('Select a Page:', ('All Islands', 'Kauaʻi', 'Oʻahu', 'Molokaʻi', 'Lānaʻi', 'Maui', 'Hawaiʻi (Big Island)'))

metric_view = st.sidebar.radio("Select View:", ["Daily", "Monthly"])

if metric_view == "Daily":
    st.sidebar.markdown("### Date")
    st.session_state.date_input = st.sidebar.text_input("Enter Date (MM/DD/YYYY)", datetime.today().strftime("%m/%d/%Y"))
else:
    st.sidebar.markdown("### Date")
    st.session_state.date_input = st.sidebar.text_input("Enter Date (MM/YYYY)", datetime.today().strftime("%m/%Y"))

st.sidebar.markdown("### Display Type")
display_type = st.sidebar.radio("Choose Data", ["General Overview", 
    "Rainfall", "Temperature", "Humidity", "NVDI", "Ignition Probability",
    "Future Climate Predictions", "Contemporary Climatology", "Legacy Climatology"])

# Toggle state setup
if "view_toggle" not in st.session_state:
    st.session_state.view_toggle = "Map"

#Main Dashboard
main_col, chat_col = st.columns([4,1])

with main_col:
    
    # Default Homepage Map if no selection yet or fallback
    if selected_page == 'All Islands':
        st.markdown('''
        # Hawaiian Islands Overview
        > Explore climate data in the main islands of Hawaiʻi. 
        ---
        ''')
        bounds = [[18.5, -161.0], [22.25, -154.5]]
        all_map = folium.Map(location=[20.5, -157.0], zoom_start=7, tiles=None, min_zoom=6, max_bounds=True)
        folium.TileLayer('Esri.WorldImagery').add_to(all_map)

        islands_info = {
            "Kauaʻi": [22.1, -159.5],
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
        if st.session_state.view_toggle == "Map":
            folium_static(all_map)
        else:
            chart_data = pd.DataFrame(
                np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
                columns=["lat", "lon"],
            )

            st.pydeck_chart(
                pdk.Deck(
                    map_style=None,
                    initial_view_state=pdk.ViewState(
                        latitude=37.76,
                        longitude=-122.4,
                        zoom=11,
                        pitch=50,
                    ),
                    layers=[
                        pdk.Layer(
                            "HexagonLayer",
                            data=chart_data,
                            get_position="[lon, lat]",
                            radius=200,
                            elevation_scale=4,
                            elevation_range=[0, 1000],
                            pickable=True,
                            extruded=True,
                        ),
                        pdk.Layer(
                            "ScatterplotLayer",
                            data=chart_data,
                            get_position="[lon, lat]",
                            get_color="[200, 30, 0, 160]",
                            get_radius=200,
                        ),
                    ],
                )
            )

    # Main Dashboard (only new blocks for each island below)
    today = datetime.today()
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
        else:
            oahu_map = folium.Map(location=[21.4389, -158.0], zoom_start=9, tiles=None, min_zoom=6, max_bounds=True)
            folium.TileLayer('Esri.WorldImagery').add_to(oahu_map)
            folium_static(oahu_map)

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