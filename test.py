from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import time
import os

def scrape_pinterest_images(search_term, scroll_count=5, scroll_pause=2):
    """
    Scrapes image URLs from Pinterest search results.

    Args:
        search_term: The search term to use on Pinterest.
        scroll_count: Number of times to scroll down the page.
        scroll_pause: Time to wait between scrolls (in seconds).

    Returns:
        A list of image URLs.
    """

    options = Options()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    # Assuming ChromeDriver is in the same directory as this script
    options.binary_location = r"chromedriver.exe" 

    driver = webdriver.Chrome(options=options)
    driver.get(f"https://in.pinterest.com/search/pins/?q={search_term}")

    for _ in range(scroll_count):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause)

    # Explicit wait for images to load (optional)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "img"))
        )
    except:
        print("Timeout waiting for images to load.")

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    image_urls = [img.get('src') for img in soup.find_all('img')]

    driver.quit()
    return image_urls

def download_images(image_urls, search_term):
    """
    Downloads images from a list of URLs and saves them in a folder.

    Args:
        image_urls: A list of image URLs.
        search_term: The search term used to create the folder name.
    """

    folder_name = f"pinterest_{search_term}"
    os.makedirs(folder_name, exist_ok=True)  # Create the folder if it doesn't exist

    for i, url in enumerate(image_urls):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()  # Raise an exception for bad status codes

            file_name = f"{folder_name}/image_{i+1}.jpg"  # You can customize the filename format
            with open(file_name, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Downloaded {url} to {file_name}")

        except requests.exceptions.RequestException as e:
            print(f"Error downloading {url}: {e}")

if __name__ == "__main__":
    search_term = "anime"
    image_urls = scrape_pinterest_images(search_term)
    download_images(image_urls, search_term)