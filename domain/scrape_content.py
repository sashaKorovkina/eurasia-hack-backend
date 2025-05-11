import requests
from bs4 import BeautifulSoup
from typing import List, Optional, Dict
from ai_clients.gemini import GeminiClient
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from io import BytesIO
from PIL import Image
from selenium.webdriver.chrome.service import Service
import logging
from flask import Flask

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

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

        return url_list

    except requests.exceptions.RequestException as e:
        print(f"Error downloading or processing {url}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def take_screenshot(url: str) -> Optional[Image.Image]:
    try:
        logging.info(f"Accessing: {url}")

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920,1080")

        # In Cloud Run, we often install chromium & chromedriver in /usr/bin
        chrome_options.binary_location = "/usr/bin/chromium"
        service = Service("/usr/bin/chromedriver")

        driver = webdriver.Chrome(service=service, options=chrome_options)
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
        return image_response

    except Exception as e:
        print(f"An error occurred while taking screenshot of {url}: {e}")
        return None


def reconcile_product(url):
    product_text = extract_text(url)
    if not product_text:
        print("Failed to extract text.")
        return None

    product_urls = extract_urls(url)
    if not product_urls:
        print("Failed to extract URLs.")
        return None

    try:
        ai_response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                f"Write a structured JSON with all of the product attributes based on this data:"
                f"{product_text} and the URLs: {product_urls}."
            ],
        )
        parsed_response = ai_response.text.replace("```json", "").replace("```", "").strip()
        json_output = json.loads(parsed_response)
        return json_output

    except Exception as e:
        print(f"Error during AI processing or JSON decoding: {e}")
        return None


def get_product_image_data(url):
    image_data = take_screenshot(url)
    if not image_data:
        print("Failed to take screenshot.")
        return None

    try:
        ai_response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                f"Write a structured JSON with all of the product attributes based on this data"
                f"images: {image_data}."
            ],
        )
        parsed_response = ai_response.text.replace("```json", "").replace("```", "").strip()
        json_output = json.loads(parsed_response)
        return json_output

    except Exception as e:
        print(f"Error during AI processing or JSON decoding: {e}")
        return None


if __name__ == "__main__":
    url = "https://sashakorovkina2003.wixsite.com/my-site/product-page/i-m-a-product-15"
    reconcile_product(url)