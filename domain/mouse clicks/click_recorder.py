import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pynput.mouse import Listener, Button

chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=chrome_options)

def track_clicks(duration=30):
    """Tracks user clicks on the webpage for a specified duration."""
    clicks = []
    start_time = time.time()

    def on_click(x, y, button, pressed):
        if pressed and button == Button.left:
            clicks.append((x, y, time.time() - start_time))

    try:
        with Listener(on_click=on_click) as listener:
            print(f"Tracking clicks for {duration} seconds...")
            time.sleep(duration)
            listener.stop()  # Stop listener after duration
    except Exception as e:
        print(f"An error occurred during click tracking: {e}")
    finally:
        print("Click tracking finished.")
        return clicks


def open_webpage_and_track_clicks(url, driver, tracking_duration=30):
    """
    Opens a specified webpage using Selenium and tracks user clicks on it.

    Args:
        url (str): The URL of the webpage to open.
        tracking_duration (int): The duration in seconds to track clicks.

    Returns:
        list: A list of tuples with x-coordinate, y-coordinate, and timestamp.
    """
    try:
        driver.get(url)
        print(f"Opened webpage: {url}")
        input("Please interact with the webpage. Press Enter to start click tracking...")
        clicks = track_clicks(tracking_duration)
        print("Recorded Clicks:")
        for x, y, t in clicks:
            print(f"Clicked at ({x}, {y}) at {t:.2f} seconds")
    finally:
        driver.quit()
        print("Webdriver closed.")
    return clicks


if __name__ == "__main__":
    target_url = "https://www.azazie.com/gb/products/harmony-mauve-floral-maxi-dress-atelier-dress/6586582?sourceTag=atelier_formal_dresses"
    tracking_time = 15
    driver = webdriver.Chrome()
    recorded_clicks = open_webpage_and_track_clicks(target_url, driver, tracking_time)