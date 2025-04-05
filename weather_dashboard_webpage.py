# importing libraries
import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
import matplotlib.pyplot as plt 
import streamlit.components.v1 as components
from streamlit_folium import folium_static
import folium

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
selected_city = st.sidebar.selectbox(
    'Select a City:', ('Delhi', 'Kuala Lumpur', 'Singapore', 'Tokyo', 'Oahu'))
st.sidebar.markdown(
    'Here is an analysis of the weather data for four cities in Asia for 20 years.')


# Main Dashboard
if selected_city == 'Delhi':
    st.markdown('''
    # Weather Dashboard - ***Delhi*** 
    > Delhi, the capital of India, is one of the most populous and polluted cities in the world. The city has changed a lot over the years with respect to its weather. There have been a number of factors that have contributed to this change, including climate change. Here is a dashboard for the analysis of weather data for 20 years.
    ---
    ''')
    rt_chart(Delhi)
elif selected_city == 'Kuala Lumpur':
    st.markdown('''
    # Weather Data Dashboard - ***Kuala Lumpur***
    > Kaula Lumpur, the capital city of Malaysia, home to the iconic Twin Towers. Kuala Lumpur is best known for its affordable luxury hotels, great shopping scene, and even better food. Malaysian capital boasts some of the finest shopping centers in the world, head towards Pavilion KL and Suria KLC for high-end luxurious items, or visit Petaling Street to have a real sense of local shopping. The city has changed a lot over the years with respect to its weather. There have been a number of factors that have contributed to this change, including climate change. Here is a dashboard for the analysis of weather data for 20 years.
    ---
    ''')
    rt_chart(kuala_lumpur)
elif selected_city == 'Singapore':
    st.markdown('''
    # Weather Data Dashboard - ***Singapore***
    > Singapore, officially the Republic of Singapore, is a sovereign island country and city-state in maritime Southeast Asia. It is famous for being a global financial center, being among the most densely populated places in the world, having a world-class city airport with a waterfall, and a Botanic Garden that is a World Heritage Site. The city has changed a lot over the years with respect to its weather. There have been a number of factors that have contributed to this change, including climate change. Here is a dashboard for the analysis of weather data for 20 years.
    ''')
    rt_chart(Singapore)
elif selected_city == 'Tokyo':
    st.markdown('''
    # Weather Data Dashboard - ***Tokyo***
    > Tokyo, Japan’s busy capital, mixes the ultramodern and the traditional...
    ''')
    rt_chart(Tokyo)
elif selected_city == 'Oahu':
    st.markdown('''
    # Weather Data Dashboard - ***Oahu***
    > Oʻahu, known as "The Gathering Place," is the third-largest of the Hawaiian Islands...
    ---
    ''')
    # Define bounding box for Hawaiian Islands
    bounds = [[18.5, -161.0], [21.9, -154.5]]
    # Create interactive satellite map with Esri tiles, constrained to Hawaii
    oahu_map = folium.Map(
        location=[20.5, -157.0],
        zoom_start=7,
        tiles=None,
        min_zoom=6,
        max_bounds=True
    )
    folium.TileLayer('Esri.WorldImagery').add_to(oahu_map)
    oahu_map.fit_bounds(bounds)
    folium_static(oahu_map)

    

# --- Floating Chatbox HTML/CSS/JS ---
# This injects the UI and the JavaScript to interact with a *separate* backend API.
chatbox_html = """
<style>
    #chat-bubble {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 60px;
        height: 60px;
        background-color: #6a1b9a; /* Purple color */
        color: white;
        border-radius: 50%;
        text-align: center;
        line-height: 60px; /* Vertically center icon/text */
        font-size: 24px;
        cursor: pointer;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
        z-index: 1000;
        transition: transform 0.2s ease-in-out;
    }
    #chat-bubble:hover {
        transform: scale(1.1);
        background-color: #4a148c; /* Darker purple on hover */
    }
    #chat-window {
        position: fixed;
        bottom: 90px; /* Position above the bubble */
        right: 20px;
        width: 320px; /* Slightly wider */
        height: 450px; /* Slightly taller */
        background-color: #ffffff;
        border: 1px solid #e0e0e0; /* Lighter border */
        border-radius: 12px; /* More rounded corners */
        box-shadow: 0 4px 12px rgba(0,0,0,0.15); /* Softer shadow */
        display: none; /* Hidden by default */
        flex-direction: column;
        overflow: hidden;
        z-index: 999;
    }
    #chat-window.open {
        display: flex;
        z-index: 1001;
    }
    #chat-header {
        background: linear-gradient(to right, #7b1fa2, #6a1b9a); /* Gradient header */
        color: white;
        padding: 12px 15px; /* More padding */
        font-weight: bold;
        border-top-left-radius: 12px; /* Match window rounding */
        border-top-right-radius: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
     #chat-header span {
        font-size: 1.1em;
     }
     #close-chat {
        background: none;
        border: none;
        color: white;
        font-size: 20px;
        cursor: pointer;
        padding: 0 5px;
     }
    #chat-messages {
        flex-grow: 1;
        padding: 15px; /* More padding */
        overflow-y: auto;
        background-color: #f5f5f5; /* Light grey background */
        border-bottom: 1px solid #e0e0e0;
    }
    #chat-input-area {
        display: flex;
        padding: 12px;
        background-color: #ffffff;
        border-top: 1px solid #e0e0e0;
    }
    #chat-input {
        flex-grow: 1;
        border: 1px solid #bdbdbd; /* Grey border */
        border-radius: 20px; /* Pill shape */
        padding: 10px 15px; /* Adjust padding */
        margin-right: 10px;
        font-size: 0.95em;
        outline: none; /* Remove focus outline */
    }
    #chat-input:focus {
        border-color: #6a1b9a; /* Highlight border on focus */
        box-shadow: 0 0 0 2px rgba(106, 27, 154, 0.2); /* Subtle glow on focus */
    }
    #send-button {
        padding: 10px 15px;
        background-color: #6a1b9a; /* Match theme */
        color: white;
        border: none;
        border-radius: 20px; /* Pill shape */
        cursor: pointer;
        font-size: 0.95em;
        transition: background-color 0.2s ease;
    }
    #send-button:hover {
        background-color: #4a148c; /* Darker shade on hover */
    }
    /* Message Styling */
    .message {
        margin-bottom: 10px; /* More space between messages */
        padding: 8px 12px;
        border-radius: 15px; /* Rounded messages */
        max-width: 80%; /* Prevent messages from being too wide */
        word-wrap: break-word; /* Handle long words */
        font-size: 0.95em;
        line-height: 1.4;
    }
    .user-message {
        background-color: #e1bee7; /* Light purple for user */
        color: #333;
        margin-left: auto; /* Align to right */
        border-bottom-right-radius: 5px; /* Slightly different shape */
    }
    .bot-message {
        background-color: #eeeeee; /* Light grey for bot */
        color: #333;
        margin-right: auto; /* Align to left */
        border-bottom-left-radius: 5px; /* Slightly different shape */
    }
    .error-message {
        background-color: #ffcdd2; /* Light red for errors */
        color: #b71c1c;
        margin-right: auto;
        border-bottom-left-radius: 5px;
    }
    .typing-indicator {
        display: none; /* Hidden by default */
        padding: 5px 12px;
        color: #757575;
        font-style: italic;
        font-size: 0.9em;
    }
</style>

<div id="chat-bubble">💬</div>
<div id="chat-window">
    <div id="chat-header">
        <span>AI Assistant</span>
        <button id="close-chat" title="Close Chat">&times;</button>
    </div>
    <div id="chat-messages">
        <div class="message bot-message">Hello! How can I assist you today?</div>
    </div>
    <div class="typing-indicator" id="typing-indicator">AI is typing...</div>
    <div id="chat-input-area">
        <input type="text" id="chat-input" placeholder="Ask something...">
        <button id="send-button">Send</button>
    </div>
</div>

<script>
    const chatBubble = document.getElementById('chat-bubble');
    const chatWindow = document.getElementById('chat-window');
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    const messagesContainer = document.getElementById('chat-messages');
    const closeButton = document.getElementById('close-chat');
    const typingIndicator = document.getElementById('typing-indicator');

    // --- Backend API Endpoint ---
    // IMPORTANT: Replace this with the actual URL of your backend API
    const API_ENDPOINT = '/api/chat'; // Placeholder URL

    // Function to add a message to the chat window
    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.classList.add(sender === 'user' ? 'user-message' : (sender === 'error' ? 'error-message' : 'bot-message'));
        messageDiv.textContent = text; // Use textContent to prevent HTML injection
        messagesContainer.appendChild(messageDiv);
        // Scroll to the bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // Function to handle sending message and interacting with API
    async function sendMessage() {
        const messageText = chatInput.value.trim();
        if (messageText === '') return; // Do nothing if input is empty

        // 1. Display user message immediately
        addMessage(messageText, 'user');
        chatInput.value = ''; // Clear input field
        chatInput.disabled = true; // Disable input while waiting for response
        sendButton.disabled = true;
        typingIndicator.style.display = 'block'; // Show typing indicator

        try {
            // 2. Send message to backend API
            const response = await fetch(API_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: messageText }), // Send message in JSON body
            });

            typingIndicator.style.display = 'none'; // Hide typing indicator

            if (!response.ok) {
                // Handle HTTP errors (like 404, 500)
                throw new Error(`API Error: ${response.status} ${response.statusText}`);
            }

            // 3. Process successful response
            const data = await response.json();

            if (data && data.answer) {
                // Display bot's answer
                addMessage(data.answer, 'bot');
            } else {
                // Handle cases where response is ok but doesn't contain expected data
                addMessage("Sorry, I received an unexpected response from the server.", 'error');
            }

        } catch (error) {
            // 4. Handle errors (network issues, API errors, JSON parsing errors)
            console.error('Chat API Error:', error);
            typingIndicator.style.display = 'none'; // Hide typing indicator
            addMessage(`Sorry, something went wrong. Could not reach the AI assistant. (${error.message})`, 'error');
        } finally {
            // Re-enable input fields regardless of success or failure
             chatInput.disabled = false;
             sendButton.disabled = false;
             chatInput.focus(); // Set focus back to input
        }
    }

    // --- Event Listeners ---

    // Toggle chat window visibility
    chatBubble.addEventListener('click', () => {
        chatWindow.classList.toggle('open');
        if (chatWindow.classList.contains('open')) {
             chatInput.focus(); // Focus input when opened
        }
    });

    // Close chat window
    closeButton.addEventListener('click', () => {
        chatWindow.classList.remove('open');
    });

    // Send message on button click
    sendButton.addEventListener('click', sendMessage);

    // Send message on Enter key press in input field
    chatInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

</script>
"""

# Inject the HTML into the Streamlit app
# This should generally be placed near the end of your script
st.markdown(chatbox_html, unsafe_allow_html=True)