import requests
from bs4 import BeautifulSoup
from typing import List, Optional, Dict
from ai_clients.gemini import GeminiClient
import json

# Retrieve all existing content from the website
# 1. Get all text
# 2. Get all urls
# 3. Get all images
# 4. The goal: re-create the product cards with all of the metadata

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


def extract_images(url: str) -> Optional[List[Dict[str, str]]]:
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        image_elements = soup.find_all('img')

        image_list = []
        for image in image_elements:
            img_url = image.get('src')
            style = image.get('style', '')

            # Extract coordinates from the 'style' attribute if present (e.g., top, left)
            coordinates = {}
            if 'top' in style:
                coordinates['top'] = style.split('top:')[1].split(';')[0].strip()
            if 'left' in style:
                coordinates['left'] = style.split('left:')[1].split(';')[0].strip()

            # Append the image URL and coordinates (if any)
            if img_url:
                image_data = {'element': 'img', 'src': img_url}
                if coordinates:
                    image_data['coordinates'] = coordinates
                image_list.append(image_data)

        print(image_list)
        return image_list

    except requests.exceptions.RequestException as e:
        print(f"Error downloading or processing {url}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def reconcile_product(url):

    product_text = extract_text(url)
    product_urls = extract_urls(url)
    # extract_images(url)

    ai_response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            f"Write a structured JSON with all of the product attributes based on this data:"
            f"{product_text} and the URLs: {product_urls}."
        ],
    )
    parsed_response = ai_response.text.replace("```json", "").replace("```", "").strip()

    try:
        json_output = json.loads(parsed_response)
        print("Successfully got JSON Response!")
        return json_output
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print(f"Problematic AI Response! Gemini Broke down.")
        return None


if __name__ == "__main__":
    url = "https://sashakorovkina2003.wixsite.com/my-site/product-page/i-m-a-product-15"
    reconcile_product(url)