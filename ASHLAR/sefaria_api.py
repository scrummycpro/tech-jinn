import requests

def bible_data(reference):
    """
    Fetch data from the Sefaria API for a given reference in the format 'book.chapter.verse'.
    
    Args:
        reference (str): The reference in the format 'book.chapter.verse'.
    
    Returns:
        dict: The JSON response from the Sefaria API.
    """
    base_url = "https://www.sefaria.org/api/links/"
    url = f"{base_url}{reference}"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

def fetch_sefaria_calendars(calendar_type="sephardi", timezone="America/Los_Angeles"):
    """
    Fetch calendar data from the Sefaria API with optional parameters for custom calendar type and timezone.
    
    Args:
        calendar_type (str): The type of calendar to fetch. Defaults to 'sephardi'.
        timezone (str): The timezone to use. Defaults to 'America/Los_Angeles'.
    
    Returns:
        dict: The JSON response from the Sefaria API.
    """
    url = f"https://www.sefaria.org/api/calendars?custom={calendar_type}&timezone={timezone}"
    
    headers = {"accept": "application/json"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

def fetch_topic_data(topic_slug):
    """
    Fetch topic data from the Sefaria API for a given topic slug.
    
    Args:
        topic_slug (str): The slug of the topic to fetch.
    
    Returns:
        dict: The JSON response from the Sefaria API.
    """
    url = f"https://www.sefaria.org/api/v2/topics/{topic_slug}"
    
    headers = {"accept": "application/json"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

def fetch_next_reading(parasha):
    """
    Fetch the next reading data from the Sefaria API for a given parasha.
    
    Args:
        parasha (str): The name of the parasha (e.g., 'Bereshit').
    
    Returns:
        dict: The JSON response from the Sefaria API.
    """
    url = f"https://www.sefaria.org/api/calendars/next-read/{parasha}"
    
    headers = {"accept": "application/json"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

def fetch_random_by_topic():
    """
    Fetch random text data by topic from the Sefaria API.
    
    Returns:
        dict: The JSON response from the Sefaria API.
    """
    url = "https://www.sefaria.org/api/texts/random-by-topic"
    
    headers = {"accept": "application/json"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()
