from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import os

def download_specific_pinterest_image(image_url, download_folder="Documents/testing_pin"):
    """
    Downloads a specific image from Pinterest.

    Args:
        image_url: The URL of the image to download.
        download_folder: The path to the folder where the image will be saved.
    """

    options = Options()
    options.add_argument("--remote-debugging-address=localhost:9222") 

    driver = webdriver.Edge(options=options)
    driver.get(image_url)

    # Wait for the image to load completely
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "img"))
    )

    # Extract the high-resolution image URL (if available)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    image = soup.find("img")
    srcset = image.get('srcset') 

    if srcset:
        # Extract the highest resolution image URL from srcset
        srcset_list = srcset.split(',')
        highest_res_url = srcset_list[-1].split(' ')[0]  # Get the URL of the last (usually highest resolution) image
        image_url = highest_res_url
    else:
        image_url = image.get('src')

    driver.quit()  # Close the browser

    # Download the image
    file_name = f"{download_folder}/image.jpg"  # Customize filename
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()  # Raise an exception for bad status codes
        os.makedirs(download_folder, exist_ok=True)  # Create the folder if it doesn't exist
        with open(file_name, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded {image_url} to {file_name}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {image_url}: {e}")

if __name__ == "__main__":
    image_url = "https://www.pinterest.com/pin/334955291048958012/"  # Replace with the desired image URL
    download_specific_pinterest_image(image_url)