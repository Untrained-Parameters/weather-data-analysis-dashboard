import requests
import json

def get_chat_response(chat_history):
    """
    Sends a chat input to the model API and returns the model's response.

    Args:
        user_input (str): The user's input message.

    Returns:
        str: The model's response.
    """
    url = "http://backend:8000/chat"  # Ensure the URL is correct and includes the protocol (http://)
    
    payload = json.dumps({
        "messages": chat_history
    })
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"
