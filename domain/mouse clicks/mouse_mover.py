import time
import random
import pyautogui
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from pynput.mouse import Listener, Button

chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=chrome_options)

driver.get("https://www.azazie.com/gb/products/harmony-mauve-floral-maxi-dress-atelier-dress/6586582?sourceTag=atelier_formal_dresses")  # Replace with your target website

def human_like_mouse_move(x_target, y_target, duration=1.5):
    start_x, start_y = pyautogui.position()
    steps = 30
    for i in range(steps):
        x = start_x + (x_target - start_x) * i / steps + random.uniform(-2, 2)
        y = start_y + (y_target - start_y) * i / steps + random.uniform(-2, 2)
        pyautogui.moveTo(x, y, duration / steps)

def hover_around(x, y, radius=10, loops=20):
    for _ in range(loops):
        angle = random.uniform(0, 360)
        dx = radius * random.uniform(0.8, 1.2) * random.choice([1, -1])
        dy = radius * random.uniform(0.8, 1.2) * random.choice([1, -1])
        pyautogui.moveTo(x + dx, y + dy, duration=random.uniform(0.05, 0.1))

# TODO: make this more general
def traverse_elements():
    # --- Element 1 ---
    element1 = driver.find_element(By.XPATH, '//*[@id="goods_thumb_list"]/div[2]/div[1]/div[1]/div[1]/div/img')
    loc1 = element1.location
    size1 = element1.size

    x1 = driver.get_window_position()['x'] + loc1['x'] + size1['width'] / 2
    y1 = driver.get_window_position()['y'] + loc1['y'] + size1['height'] / 2
    print(f"Moving to Element 1 at screen coords: ({x1}, {y1})")

    human_like_mouse_move(x1, y1)
    time.sleep(2)  # Stay for 2s

    # --- Element 2 ---
    element2 = driver.find_element(By.XPATH, '//*[@id="nuxt-main-base"]/div[6]/div[2]/div/section/div[2]/div[1]/div[2]/div[1]/div[2]')
    loc2 = element2.location
    size2 = element2.size

    x2 = driver.get_window_position()['x'] + loc2['x'] + size2['width'] / 2
    y2 = driver.get_window_position()['y'] + loc2['y'] + size2['height'] / 2 + 120
    print(f"Moving to Element 2 at screen coords: ({x2}, {y2})")
    text2 = element2.text.strip()
    print(f"Text content of Element 2: \"{text2}\"")

    human_like_mouse_move(x2, y2)
    time.sleep(2)  # Stay for 2s

    # --- Element 3 (hover around) --- //*[@id="add-to-bag"]
    element2 = driver.find_element(By.XPATH, '//*[@id="add-to-bag"]')
    loc2 = element2.location
    size2 = element2.size

    x2 = driver.get_window_position()['x'] + loc2['x'] + size2['width'] / 2
    y2 = driver.get_window_position()['y'] + loc2['y'] + size2['height'] / 2 + 120
    print(f"Moving to Element 2 at screen coords: ({x2}, {y2})")
    text2 = element2.text.strip()
    print(f"Text content of Element 2: \"{text2}\"")

    human_like_mouse_move(x2, y2)
    time.sleep(2)  # Stay for 2s

    # Wait and close
    time.sleep(5)
    driver.quit()


if __name__ == "__main__":
    traverse_elements()