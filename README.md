# 🌴 Hawaiʻi Climate Explorer

A visual, interactive web app for exploring climate data across the Hawaiian Islands, built with [Streamlit](https://streamlit.io/). The app displays daily and monthly temperature and rainfall data from the Hawaiʻi Climate Data Portal (HCDP) using maps, charts, and forecasts. It is designed for educators, researchers, students, and residents interested in climate patterns and trends across the state.

---

## 🚀 Demo: How to Run the App

### 🔧 Requirements

- Python 3.9+
- Install dependencies:

From terminal:
pip install -r requirements.txt


If `requirements.txt` is not available, install manually:

From terminal:
pip install streamlit pandas numpy pydeck  ... (check 'requirements.txt' for a full list)


### ▶️ Launch the app locally

From terminal:
streamlit run main.py


Once the app launches, a browser window will open automatically. You can navigate the sidebar to select an island, time range (Daily/Monthly), and display type (Rainfall, Temperature, Forecasts, etc.).

---

## 📂 Project Structure

- **`main.py`** — The main app file that manages all routing, visualization logic, and user interaction.
- **`data_function.py`** — Contains functions to fetch and preprocess historical rainfall and temperature data from HCDP, including spatial filtering by island boundaries.
- **`temp.py`** — A simplified temperature-focused version of `data_function.py`, used when plotting max temperature from a different access point.
- **`Predictions.py`** — Trains a local machine learning model (Random Forest) on historical data to forecast future rainfall, visualized using Plotly.
- **`Multi Var Chart` (Canvas)** — Streamlit function used to dynamically generate faceted area charts showing rainfall or temperature by time unit.
- **🗺️ Map Visualizations** — Uses `pydeck` HexagonLayer to display spatial patterns in rainfall and temperature over different Hawaiian islands.
- **📊 Bar Charts** — Uses Altair to show aggregate values (median rainfall or max temp) across islands.
- **📈 Forecast Chart** — Displays actual vs predicted rainfall using Plotly, based on latitude/longitude and a user-specified future month.

---

## 🧠 Features

- 🌡️ **Daily & Monthly Data** for each island
- 📍 **Interactive Map Views** (rainfall & temperature)
- 📊 **Island Comparison Bar Charts**
- ⏩ **Rainfall Forecasting** using local ML model
- 📅 **Time Filtering** via sidebar controls
- 💬 **Custom Chat UI** mockup for future climate Q&A integration

---

## 📡 Data Source

All climate data are pulled in real time from the [Hawaiʻi Climate Data Portal API](https://www.hcdp.hawaii.edu/), provided by the University of Hawaiʻi.

---

## 🤝 Acknowledgments

This app was developed as part of the **2025 AI Hackathon** at the University of Hawaiʻi at Mānoa, by a multidisciplinary team of students, including Federica Chiti (Astronomy), Dhvanil Desai (Astronomy), Fahim Yasir (Electrical & Computer Engineering), Gerardo Rivera Tello (Atmospheric Sciences) and Yada Ponpittayalert (Design).

---

## 📬 Contact

For questions or contributions, feel free to open an issue or reach out via [GitHub Discussions](https://github.com/your-repo/discussions).

