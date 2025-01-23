from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
import time
import requests
import os

def download_images_from_pinterest(pin_url, output_folder="downloads"):
    # Set up the Edge WebDriver options
    options = webdriver.EdgeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-features=SmartScreen")
    
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    driver = webdriver.Edge(options=options)

    try:
        driver.get(pin_url)

        # Scroll to load images dynamically
        for _ in range(5):  # Adjust the range to scroll more if needed
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)  # Give time for the page to load content

        # Wait for all images to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "img"))
        )

        # Collect image URLs
        images = driver.find_elements(By.CSS_SELECTOR, "img")
        image_urls = set()  # Use a set to avoid duplicate URLs

        for img in images:
            try:
                src = img.get_attribute("src")
                if src and src.startswith("http"):  # Only valid URLs
                    image_urls.add(src)
            except StaleElementReferenceException:
                print("Encountered a stale element, skipping...")

        # Download each image
        # for idx, url in enumerate(image_urls):
        #     try:
        #         print(f"Downloading image {idx + 1} from {url}")
        #         response = requests.get(url, stream=True)
        #         if response.status_code == 200:
        #             with open(os.path.join(output_folder, f"image_{idx + 1}.jpg"), "wb") as file:
        #                 for chunk in response.iter_content(1024):
        #                     file.write(chunk)
        #         else:
        #             print(f"Failed to download image from {url}")
        #     except Exception as e:
        #         print(f"Error downloading image {idx + 1}: {e}")

    except TimeoutException:
        print("Page load timed out!")
    finally:
        input("Press Enter to close the browser...")  # Keeps the browser open for inspection
        driver.quit()

# Replace with the Pinterest pin URL
download_images_from_pinterest("https://www.pinterest.com/pin/334955291048958012/")
