import traceback

import requests
from bs4 import BeautifulSoup
import re
from typing import List, Optional, Dict
from ai_clients.gemini import GeminiClient
import json
from io import BytesIO
from PIL import Image
import logging
from flask import Flask
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

genai_client = GeminiClient()
client = genai_client.get_client()


def extract_text(url: str) -> Optional[tuple[list[str], str]]:
    try:
        logging.info(f"Accessing: {url}")
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920,1080")

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        html = driver.page_source

        all_elements = driver.find_elements(By.XPATH, "//*[normalize-space(text())]")

        text_list = list({elem.text.strip() for elem in all_elements if elem.text.strip()})

        return text_list, html

    except Exception as e:
        traceback.print_exc()
        return None
    finally:
        if 'driver' in locals() and driver:
            logging.info("Closing the browser driver.")
            driver.quit()


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

# returns the url of the biggest image
def fetch_biggest_image_url(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        img_tags = soup.find_all('img')

        largest_img = None
        largest_area = 0

        for img in img_tags:
            src = img.get('src')
            if not src:
                continue

            # Handle relative URLs
            if src.startswith('//'):
                src = 'https:' + src
            elif src.startswith('/'):
                src = requests.compat.urljoin(url, src)
            elif not src.startswith('http'):
                continue  # skip unsupported formats

            try:
                img_resp = requests.get(src, timeout=5)
                img_resp.raise_for_status()
                image = Image.open(BytesIO(img_resp.content))

                width, height = image.size
                area = width * height

                if area > largest_area:
                    largest_area = area
                    largest_img = {
                        'url': src,
                        'width': width,
                        'height': height
                    }

            except Exception as e:
                # Skip bad images or broken links
                continue

        return largest_img.get('url')

    except Exception as e:
        print(f"Failed to fetch images from {url}: {e}")
        return None

def take_screenshot(url: str) -> Optional[Image.Image]:
    try:
        logging.info(f"Accessing: {url}")
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920,1080")

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)

        screenshot_png = driver.get_screenshot_as_png()
        driver.quit()

        image = Image.open(BytesIO(screenshot_png))
        prompt = "Describe each clothing item in the image in JSON format, including the colors, type of clothes and print if any."

        print(
            "token count with image: ",
            client.models.count_tokens(
                model="gemini-2.0-flash", contents=[prompt, image]
            )
        )

        image_response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                image,
                prompt
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

    return product_text, product_urls
    #
    # prompt = [
    #     f"Write a structured JSON with all of the product attributes based on this data:"
    #     f"focus they extracted data on the user's request: {user_prompt}"
    #     f"{product_text} and the URLs: {product_urls}."
    # ]
    #
    # try:
    #
    #     print(
    #         "token count for product: ",
    #         client.models.count_tokens(
    #             model="gemini-2.0-flash", contents=[prompt]
    #         )
    #     )
    #
    #     ai_response = client.models.generate_content(
    #         model="gemini-2.0-flash",
    #         contents=[
    #             prompt
    #         ],
    #     )
    #     parsed_response = ai_response.text.replace("```json", "").replace("```", "").strip()
    #     json_output = json.loads(parsed_response)
    #     logging.info('Executed user driven reconciliation')
    #     return json_output
    #
    # except Exception as e:
    #     print(f"Error during AI processing or JSON decoding: {e}")
    #     return None


def get_product_image_data(url):
    image_data = take_screenshot(url)
    if not image_data:
        print("Failed to take screenshot.")
        return None

    prompt = [
        f"Write a structured JSON with all of the product attributes based on the image provided"
        f"this JSON must comply to the best SEO practices. Also focus on the data which is not "
        f"normally described on a product page of the website but which you can infer from the"
        f"image."
        f"images: {image_data}."
    ]

    try:

        print(
            "token count for image data: ",
            client.models.count_tokens(
                model="gemini-2.0-flash", contents=[prompt]
            )
        )

        ai_response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                prompt
            ],
        )
        parsed_response = ai_response.text.replace("```json", "").replace("```", "").strip()
        json_output = json.loads(parsed_response)
        logging.info('Executed SEO JSON')
        return json_output

    except Exception as e:
        print(f"Error during AI processing or JSON decoding: {e}")
        return None


def export_json_ld(url, user_prompt):
    product_text, product_html = extract_text(url)
    product_urls = extract_urls(url)
    image_data = take_screenshot(url)
    biggest_image_url = fetch_biggest_image_url(url)
    try:
        ai_response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                f"Write a structured JSON-LD for a website with all of the product attributes based on this data"
                f"images: {image_data}, urls: {product_urls}, text: {product_text} and imageUrl: {biggest_image_url} . "
                f"Make sure to include 'name', 'image', and 'offers' fields."
            ],
        )
        print(f'The AI response for JSON LD is: {ai_response.text}')
        parsed_response = ai_response.text.replace("```json", "").replace("```", "").strip()
        clean_text = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', parsed_response)
        no_comma_text = re.sub(r',\s*([]})])', r'\1', clean_text)
        json_output = json.loads(no_comma_text)
        return json_output

    except Exception as e:
        print(f"Error during AI processing or JSON decoding: {e}")
        return None

def compute_image_cost(url):
    try:
        logging.info(f"Accessing: {url}")
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920,1080")

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)

        screenshot_png = driver.get_screenshot_as_png()
        driver.quit()

        image = Image.open(BytesIO(screenshot_png))
        prompt = "Describe each clothing item in the image in JSON format, including the colors, type of clothes and print if any."

        image_tokens_count = client.models.count_tokens(
                model="gemini-2.0-flash", contents=[prompt, image]
            ).total_tokens

        print(
            "token count with image: ",
            image_tokens_count
        )
        return image_tokens_count
    except Exception as e:
        print(f"Error during computing costs of processing image: {e}")
        return None

def get_model_cost(url):
    product_text, product_html = extract_text(url)
    product_urls = extract_urls(url)
    image_data = take_screenshot(url)
    biggest_image_url = fetch_biggest_image_url(url)
    price_per_token = 0.0000001

    prompt = [
        f"Write a structured JSON-LD for a website with all of the product attributes based on this data"
        f"images: {image_data}, urls: {product_urls}, text: {product_text} and imageUrl: {biggest_image_url} . "
        f"Make sure to include 'name', 'image', and 'offers' fields."
    ]

    dirty_prompt = [
        f"Write a structured JSON-LD for a website with all of the product attributes based on this data"
        f"images: {image_data}, imageUrl: {biggest_image_url}, and the html of the page: {product_html}. "
        f"Make sure to include 'name', 'image', and 'offers' fields."
    ]
    try:
        image_tokens_count = compute_image_cost(url)
        clean_tokens_count = client.models.count_tokens(model="gemini-2.0-flash", contents=[prompt]).total_tokens
        dirty_tokens_count = client.models.count_tokens(model="gemini-2.0-flash", contents=[dirty_prompt]).total_tokens
        difference = dirty_tokens_count - clean_tokens_count
        saved_money = difference * price_per_token
        total_tokens = image_tokens_count + clean_tokens_count
        total_cost = total_tokens * price_per_token
        percentage_decrease = difference / (difference + total_tokens) * 100
        print(
            f"Compressed prompt token count for json-ld: {clean_tokens_count}\n"
            f"Unprocessed prompt token count for json-ld: {dirty_tokens_count}\n"
            f"Difference: {difference}\n"
            f"Total tokens: {total_tokens}\n"
            f"Saved money: ${saved_money}\n"
            f"Total cost: ${total_cost}\n"
            f"Percentage decrease: {percentage_decrease}%"
        )
        costs_data = {
            "Compressed prompt tokens": clean_tokens_count,
            "Unprocessed prompt tokens": dirty_tokens_count,
            "Difference": difference,
            "Saved money": saved_money,
            "Percentage decrease": percentage_decrease,
            "Total tokens": total_tokens,
            "Total cost": total_cost
        }

        return costs_data

    except Exception as e:
        print(f"Error during computing costs: {e}")
        return None

if __name__ == "__main__":
    url = "https://sashakorovkina2003.wixsite.com/my-site/product-page/i-m-a-product-15"
    reconcile_product(url)