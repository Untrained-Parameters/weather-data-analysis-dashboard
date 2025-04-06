# importing libraries
import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
import matplotlib.pyplot as plt 
import streamlit.components.v1 as components
# from streamlit_folium import folium_static
# import folium
import requests
from datetime import datetime
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go
import warnings
from streamlit_extras.stylable_container import stylable_container
import data_function
from vega_datasets import data
import Predictions
import temp

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

st.sidebar.markdown("### Display Type")
if selected_page != 'All Islands':
    display_type = st.sidebar.radio("Choose Data", ["General Overview", 
        "Rainfall", "Temperature", "Humidity", "NVDI", "Ignition Probability",
        "Future Climate Predictions", "Contemporary Climatology", "Legacy Climatology"])
else:
    display_type = st.sidebar.radio("Choose Data", [ 
        "Rainfall", "Temperature", "Humidity", "NVDI", "Ignition Probability",
        "Future Climate Predictions", "Contemporary Climatology", "Legacy Climatology"])
    
default_index = 1 if display_type == "Future Climate Predictions" else 0
metric_view = st.sidebar.radio("Select View:", ["Daily", "Monthly"], index=default_index)

if metric_view == "Daily":
    st.sidebar.markdown("### Date")
    st.session_state.date_input = st.sidebar.text_input("Enter Date (MM/DD/YYYY)", "12/01/2016")
    elev_factor = 300
elif metric_view == "Monthly":
    st.sidebar.markdown("### Date")
    st.session_state.date_input = st.sidebar.text_input("Enter Date (MM/YYYY)","12/2016")
    elev_factor = 150

def plot_chart(date_input, island_name, variable):
    if island_name == "All" and variable == 'rainfall':
        chart_data_1 = data_function.get_station_data_for_period(date_input, "Oahu", variable)
        chart_data_2 = data_function.get_station_data_for_period(date_input, "Kauai", variable)
        chart_data_3 = data_function.get_station_data_for_period(date_input, "Molokai", variable)
        chart_data_4 = data_function.get_station_data_for_period(date_input, "Lānai", variable)
        chart_data_5 = data_function.get_station_data_for_period(date_input, "Maui", variable)
        chart_data_6 = data_function.get_station_data_for_period(date_input, "Hawaii (Big Island)", variable)
        # chart_data_7 = data_function.get_station_data_for_period(date_input, "Niihau", variable)
        # chart_data_8 = data_function.get_station_data_for_period(date_input, "Kahoolawe", variable)

        chart_data = pd.concat([chart_data_1, chart_data_2, chart_data_3, chart_data_4, chart_data_5, chart_data_6], ignore_index=True)
    elif island_name != "All" and variable == 'rainfall':
        chart_data = data_function.get_station_data_for_period(date_input, island_name, variable)
    elif island_name == "All" and variable == 'temperature':
        chart_data_1 = temp.get_station_data_for_period_temp(date_input, "Oahu", variable)
        chart_data_2 = temp.get_station_data_for_period_temp(date_input, "Kauai", variable)
        chart_data_3 = temp.get_station_data_for_period_temp(date_input, "Molokai", variable)
        chart_data_4 = temp.get_station_data_for_period_temp(date_input, "Lānai", variable)
        chart_data_5 = temp.get_station_data_for_period_temp(date_input, "Maui", variable)
        chart_data_6 = temp.get_station_data_for_period_temp(date_input, "Hawaii (Big Island)", variable)
        # chart_data_7 = data_function.get_station_data_for_period(date_input, "Niihau", variable)
        # chart_data_8 = data_function.get_station_data_for_period(date_input, "Kahoolawe", variable)

        chart_data = pd.concat([chart_data_1, chart_data_2, chart_data_3, chart_data_4, chart_data_5, chart_data_6], ignore_index=True)
    elif island_name != "All" and variable == 'temperature':
        chart_data = temp.get_station_data_for_period_temp(date_input, island_name, variable)
        chart_data = chart_data.rename(columns={"max-temp": "max_temp"})
        value_column = "max_temp"

    # print('--------------------------')
    # print('--------------------------')
    # print(variable)
    # print(chart_data)
    if island_name=='Oahu':
        lati = 21.44
        longi = -157.9
        zoom = 9.5
    elif island_name=='Kauai':
        lati = 22.1
        longi = -159.5
        zoom = 9.5
    elif island_name=='Molokai':
        lati = 21.13
        longi = -157.02
        zoom = 9.5
    elif island_name=='Maui':
        lati = 20.8
        longi = -156.3
        zoom = 9
    elif island_name=='Lānai':
        lati = 20.83
        longi = -156.92
        zoom = 10
    elif island_name=='Hawaii (Big Island)':
        lati = 19.5
        longi = -155.5
        zoom = 8
    elif island_name=='All':
        lati = 20.5
        longi = -157
        zoom = 6.5

    if variable == "rainfall":
        value_column = "rainfall"
        units = "mm"
        color = [[255, 0, 255]] * 6
    elif variable == "temperature":
        value_column = "max_temp"
        units = "°C"
        color = [[255, 255, 0]] * 6

    # print(np.min(chart_data[value_column]), np.max(chart_data[value_column]))
    # print(chart_data[value_column].dtype)

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
                    radius=500,
                    elevation_scale=elev_factor,
                    get_elevation_weight=value_column,
                    elevation_range=[np.min(chart_data[value_column]), np.max(chart_data[value_column])],
                    coverage=1,
                    pickable=True,
                    extruded=True,
                    color_range=color,
                ),
            ],
            tooltip={
                "text": f"{variable}: {{elevationValue}} {units}",
                "style": {
                    "backgroundColor": "#206af1",
                    "color": "white",
                },
            },
        ),
    )

    

def island_bar_chart(date_input=st.session_state.date_input, variable="rainfall", use_container_width=True):
    # Define islands and retrieve data
    islands = {
        "Oʻahu": "Oahu",
        "Kauaʻi": "Kauai",
        "Molokaʻi": "Molokai",
        "Maui": "Maui",
        "Hawaiʻi (Big Island)": "Hawaii (Big Island)"
    }

    data = []
    for label, name in islands.items():
        df = temp.get_station_data_for_period_temp(date_input, name, variable)
        df = df.rename(columns={"max-temp": "max_temp"})
        if variable == "rainfall":
            df = df.rename(columns={"rainfall": "value"})
            agg_value = df["value"].median()
        else:
            df = df.rename(columns={"max_temp": "value"})
            agg_value = df["value"].max()
        data.append({"Island": label, "value": agg_value})

    df_summary = pd.DataFrame(data)

    bar_chart = (
        alt.Chart(df_summary)
        .mark_bar()
        .encode(
            y=alt.Y("Island:N", sort="-x", title="Island"),
            x=alt.X("value:Q", title="Median Rainfall (mm)" if variable == "rainfall" else "Max Temperature (°C)"),
            color=alt.Color("Island:N", legend=None),
            tooltip=["Island:N", "value:Q"]
        )
        .properties(
            width=600,
            height=400,
            title=f"{'Median Rainfall' if variable == 'rainfall' else 'Max Temperature'} by Island"
        )
        .configure_title(fontSize=25)
        .configure_axis(
            labelFontSize=20,
            titleFontSize=24
        )
        .configure_legend(
            labelFontSize=20,
            titleFontSize=20
        )
    )

    st.altair_chart(bar_chart, theme=None, use_container_width=use_container_width)



#Main Dashboard
main_col, chat_col = st.columns([4,1])

# Initialize state
if "active_view" not in st.session_state:
    st.session_state.active_view = "map"

with main_col:
    if selected_page == 'All Islands':
        if display_type=="Future Climate Predictions":
            metric_view = "Monthly"
            page_title = f"Future Predictions for All Islands"
            st.markdown(f'''
            # {page_title}
            ''')
            month_pred = st.text_input("Enter Prediction Month (MM/YYYY)", "04/2025")
            Predictions.generate_rainfall_forecast_plot(month_pred, 21.31667, -158.06667)
        else:
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
                st.markdown(
                    "<div style='text-align: center; font-size: 24px; color: #808180'>⬅️ &nbsp; <strong>How to visualize data?</strong> &nbsp; ➡️</div>",
                    unsafe_allow_html=True
                )
            with right_col:
                if st.button("📊 Show Graph"):
                    st.session_state.active_view = "graph"


            # Display the appropriate view
            if st.session_state.active_view == "map":
                if display_type=="Rainfall":
                    plot_chart(date_input=st.session_state.date_input, island_name="All", variable="rainfall")
                elif display_type=="Temperature":
                    plot_chart(date_input=st.session_state.date_input, island_name="All", variable="temperature")

            elif st.session_state.active_view == "graph":
                if display_type=="Rainfall":
                    island_bar_chart(use_container_width=True,date_input=st.session_state.date_input,variable="rainfall")
                elif display_type=="Temperature":
                    island_bar_chart(use_container_width=True,date_input=st.session_state.date_input,variable="temperature")


    # Main Dashboard (only new blocks for each island below)
    # today = datetime.today()
    if selected_page == 'Oʻahu':
        if display_type=="Future Climate Predictions":
            metric_view = "Monthly"
            page_title = f"Future Predictions for Oʻahu"
            st.markdown(f'''
            # {page_title}
            ''')
            month_pred = st.text_input("Enter Prediction Month (MM/YYYY)", "04/2025")
            Predictions.generate_rainfall_forecast_plot(month_pred, 21.688333, -157.952500)
        else:
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
                else:# monthly metrics
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
                st.pydeck_chart(
                    pdk.Deck(
                        map_style='mapbox://styles/mapbox/satellite-v9',
                        initial_view_state=pdk.ViewState(
                            latitude=21.44,
                            longitude=-157.9,
                            zoom=9.5,
                            pitch=50,
                            lati = 21.44
                        ),
                    ),
                )
            elif display_type=="Rainfall":
                plot_chart(date_input=st.session_state.date_input, island_name="Oahu", variable="rainfall")
            elif display_type=="Temperature":
                plot_chart(date_input=st.session_state.date_input, island_name="Oahu", variable="temperature")


    elif selected_page == "Kauaʻi":
        if display_type=="Future Climate Predictions":
            metric_view = "Monthly"
            page_title = f"Future Predictions for Kauaʻi"
            st.markdown(f'''
            # {page_title}
            ''')
            month_pred = st.text_input("Enter Prediction Month (MM/YYYY)", "04/2025")
            Predictions.generate_rainfall_forecast_plot(month_pred, 21.981570, -159.342206)
        else:
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
                st.pydeck_chart(
                    pdk.Deck(
                        map_style='mapbox://styles/mapbox/satellite-v9',
                        initial_view_state=pdk.ViewState(
                            latitude=22.1,
                            longitude=-159.5,
                            zoom=9.5,
                            pitch=50,
                        ),
                    ),
                )
            elif display_type=="Rainfall":
                plot_chart(date_input=st.session_state.date_input, island_name="Kauai", variable="rainfall")
            elif display_type=="Temperature":
                plot_chart(date_input=st.session_state.date_input, island_name="Kauai", variable="temperature")

    elif selected_page == 'Molokaʻi':
        if display_type=="Future Climate Predictions":
            metric_view = "Monthly"
            page_title = f"Future Predictions for Molokaʻi"
            st.markdown(f'''
            # {page_title}
            ''')
            month_pred = st.text_input("Enter Prediction Month (MM/YYYY)", "04/2025")
            Predictions.generate_rainfall_forecast_plot(month_pred, 21.31667, -158.06667)
        else:
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
                st.pydeck_chart(
                    pdk.Deck(
                        map_style='mapbox://styles/mapbox/satellite-v9',
                        initial_view_state=pdk.ViewState(
                            latitude=21.13,
                            longitude=-157.02,
                            zoom=9.5,
                            pitch=50, 
                        ),
                    ),
                )
            elif display_type=="Rainfall":
                plot_chart(date_input=st.session_state.date_input, island_name="Molokai", variable="rainfall")
            elif display_type=="Temperature":
                plot_chart(date_input=st.session_state.date_input, island_name="Molokai", variable="temperature")

    elif selected_page == 'Lānaʻi':
        if display_type=="Future Climate Predictions":
            metric_view = "Monthly"
            page_title = f"Future Predictions for Lānaʻi"
            st.markdown(f'''
            # {page_title}
            ''')
            month_pred = st.text_input("Enter Prediction Month (MM/YYYY)", "04/2025")
            Predictions.generate_rainfall_forecast_plot(month_pred, 21.31667, -158.06667)
        else:
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
                st.pydeck_chart(
                    pdk.Deck(
                        map_style='mapbox://styles/mapbox/satellite-v9',
                        initial_view_state=pdk.ViewState(
                            latitude=20.83,
                            longitude=-156.92,
                            zoom=10,
                            pitch=50,
                        ),
                    ),
                )
            elif display_type=="Rainfall":
                plot_chart(date_input=st.session_state.date_input, island_name="Lānai", variable="rainfall")
            elif display_type=="Temperature":
                plot_chart(date_input=st.session_state.date_input, island_name="Lānai", variable="temperature")


    elif selected_page == 'Maui':
        if display_type=="Future Climate Predictions":
            metric_view = "Monthly"
            page_title = f"Future Predictions for Maui"
            st.markdown(f'''
            # {page_title}
            ''')
            month_pred = st.text_input("Enter Prediction Month (MM/YYYY)", "04/2025")
            Predictions.generate_rainfall_forecast_plot(month_pred, 21.31667, -158.06667)
        else:
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
                st.pydeck_chart(
                    pdk.Deck(
                        map_style='mapbox://styles/mapbox/satellite-v9',
                        initial_view_state=pdk.ViewState(
                            latitude=20.8,
                            longitude=-156.3,
                            zoom=9,
                            pitch=50,
                        ),
                    ),
                )
            elif display_type=="Rainfall":
                plot_chart(date_input=st.session_state.date_input, island_name="Maui", variable="rainfall")
            elif display_type=="Temperature":
                plot_chart(date_input=st.session_state.date_input, island_name="Maui", variable="temperature")

    elif selected_page == 'Hawaiʻi (Big Island)':
        if display_type=="Future Climate Predictions":
            metric_view = "Monthly"
            page_title = f"Future Predictions for Hawaiʻi (Big Island)"
            st.markdown(f'''
            # {page_title}
            ''')
            month_pred = st.text_input("Enter Prediction Month (MM/YYYY)", "04/2025")
            Predictions.generate_rainfall_forecast_plot(month_pred, 19.83639, -155.613)
        else:
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
                st.pydeck_chart(
                    pdk.Deck(
                        map_style='mapbox://styles/mapbox/satellite-v9',
                        initial_view_state=pdk.ViewState(
                            latitude=19.5,
                            longitude=-155.5,
                            zoom=8,
                            pitch=50,
                        ),
                    ),
                )
            elif display_type=="Rainfall":
                plot_chart(date_input=st.session_state.date_input, island_name="Hawaii (Big Island)", variable="rainfall")
            elif display_type=="Temperature":
                plot_chart(date_input=st.session_state.date_input, island_name="Hawaii (Big Island)", variable="temperature")


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

    with st.expander("🌐 Kai-Mate", expanded=False):
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