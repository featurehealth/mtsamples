import requests
from bs4 import BeautifulSoup
import itertools
import time
from tqdm import tqdm
from .config import BASE_URL


__all__ = ["get_page_data", "fetch_sample", "get_specialties", "fetch_samples_by_specialty", "fetch_all_samples"]

def get_page_data(url, max_retries=3, wait_time=10):
    """
    Fetches data from the given URL with retry logic in case of failures.
    
    Parameters:
    - url (str): The URL from which to fetch data.
    - max_retries (int): The maximum number of retry attempts. Default is 3.
    - wait_time (int): The time to wait between retries in seconds. Default is 10 seconds.
    
    Returns:
    - response (requests.Response or None): The HTTP response if successful, otherwise None.
    """
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url, timeout=60)
            if response.status_code == 200:
                return response 
            else:
                print(f"Request failed with status code: {response.status_code}. Retrying...")
                retries += 1
                time.sleep(wait_time)  # Retry after 1 second
        except requests.RequestException as e:
            # If an exception occurs, print an error message and retry
            print(f"Exception occurred: {e}. Retrying...")
            retries += 1
            time.sleep(wait_time)
    print(f"Max retries of {max_retries} reached. Failed to fetch data from {url}.")
    return None

def fetch_sample(sample_url):
    """
    Fetches and parses a medical transcription sample from the given URL.
    
    Parameters:
    - sample_url (str): The URL of the medical transcription sample page.
    
    Returns:
    - details (dict): A dictionary containing parsed details from the sample page.
    """
    response = get_page_data(sample_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    data_section = [x.find_all('b') for x in soup.find_all('div', class_='hilightBold')][0]
    # Dynamic section parsing
    details = {}
    for x in data_section:
        if ':' in x.text:
            nextSib = x.nextSibling
            if (nextSib is None):
              continue
            while (len(nextSib.text)==0):
              nextSib = nextSib.nextSibling
            colname = x.text.lower().replace(':', '').replace(' ', '_')
            details[colname] = nextSib.text.strip().replace('\xa0', '')
    details["keywords"] = [x.strip() for x in details["keywords"].split(',') if len(x)>0]
    details["url"] = sample_url
    return details

def get_specialties():
    """
    Fetches and parses the list of medical specialties from the sitemap page.
    
    Returns:
    - specialties (list): A list of medical specialties.
    """
    response = fetch_data(BASE_URL + "/site/pages/sitemap.asp")
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all <p> elements containing specialties
    specialty_elements = soup.find_all('p')
    specialties = []

    for element in specialty_elements:
        # Check if <p> contains an <a> with a JavaScript call for expanding/collapsing sections
        a_tag = element.find('a', onclick=True)
        if a_tag and 'exp_coll' in a_tag['onclick']:
            specialties.append(a_tag.get_text().strip())

    # Remove duplicates and empty strings, if any
    specialties = list(filter(None, specialties))
    return specialties


def fetch_samples_by_specialty(specialty, samples=[]):
    """
    Fetches medical samples for a given specialty.
    
    Parameters:
    - specialty (str): The medical specialty to fetch samples for.
    - samples (list): A list of existing samples to avoid duplicates. Default is an empty list.
    
    Returns:
    - samples (list): A list of dictionaries containing sample details.
    """
    response = fetch_data(BASE_URL + "/site/pages/sitemap.asp")
    soup = BeautifulSoup(response.content, 'html.parser')
    all_links = [x.get("href") for x in soup.find_all('a')]
    specialty_links = [BASE_URL+x for x in all_links if ('-'+specialty in x) and ('sample.asp') in x]
    if (len(samples)>0):
        sample_names = [x["sample_name"] for x in samples]
        specialty_links = [s for s in specialty_links if not any(s.endswith(sample_name) for sample_name in sample_names)]
    if (len(specialty_links)==0):
        return samples
    for i in tqdm (range (len(specialty_links)), desc="Downloading..."):
        samples.append(fetch_sample(specialty_links[i]))
    return samples

def fetch_all_samples(samples_dict={}):
    """
    Fetches all medical transcription samples for all specialties listed on the website.
    
    Parameters:
    - samples_dict (dict): A dictionary of existing samples keyed by specialty. Default is an empty dictionary.
    
    Returns:
    - samples_dict (dict): An updated dictionary with samples for all specialties.
    """
    specialties = get_specialties()
    print("Fetching samples from ")
    for specialty_x in specialties:
        print(specialty_x)
        samples_list = []
        if specialty_x in samples_dict:
            samples_list = samples_dict[specialty_x]
        samples_dict[specialty_x] = fetch_samples_by_specialty(specialty_x, samples=samples_list)
    return samples_dict
