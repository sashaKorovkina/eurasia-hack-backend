import requests
from bs4 import BeautifulSoup
from typing import List, Optional, Dict
from ai_clients.gemini import GeminiClient
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from io import BytesIO
from PIL import Image
import base64

"""
Gets all existing product data 
in JSON format.
"""

genai_client = GeminiClient()
client = genai_client.get_client()


def extract_text(url: str) -> Optional[List[Dict[str, str]]]:
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'div'])

        text_list = []
        for element in elements:
            text = element.text.strip()
            if text:
                text_list.append({'element': element.name, 'text': text})

        print(text_list)
        return text_list

    except requests.exceptions.RequestException as e:
        print(f"Error downloading or processing {url}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def extract_urls(url: str) -> Optional[List[Dict[str, List[str]]]]:
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        elements = soup.find_all(['a']) # Find all anchor tags

        url_list = []
        for element in elements:
            href = element.get('href')
            if href:
               url_list.append({'element': element.name, 'urls': [href]})
        print(url_list)
        return url_list

    except requests.exceptions.RequestException as e:
        print(f"Error downloading or processing {url}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def take_screenshot(url: str) -> Optional[Image.Image]:
    try:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)

        screenshot_png = driver.get_screenshot_as_png()
        driver.quit()

        image = Image.open(BytesIO(screenshot_png))

        image_response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                image,
                "Describe each clothing item in the image in JSON format, including the colors, type of clothes and print if any."
            ],
        )

        print(f'The image response is: {image_response.text}')

        return image_response.text

    except Exception as e:
        print(f"An error occurred while taking screenshot of {url}: {e}")
        return None


def reconcile_product(url):

    product_text = extract_text(url)
    product_urls = extract_urls(url)
    image_data = take_screenshot(url)

    ai_response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            f"Write a structured JSON with all of the product attributes based on this data:"
            f"{product_text} and the URLs: {product_urls} and the images: {image_data}."
        ],
    )
    parsed_response = ai_response.text.replace("```json", "").replace("```", "").strip()

    try:
        json_output = json.loads(parsed_response)
        return json_output
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print(f"Problematic AI Response! Gemini Broke down.")
        return None


if __name__ == "__main__":
    url = "https://sashakorovkina2003.wixsite.com/my-site/product-page/i-m-a-product-15"
    reconcile_product(url)