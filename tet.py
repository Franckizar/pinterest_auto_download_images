from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import os
import time
from tqdm import tqdm

def scrape_pinterest_images(search_term, scroll_count=5, scroll_pause=2, max_images=100):
    """
    Scrapes image URLs from Pinterest search results.

    Args:
        search_term: The search term to use on Pinterest.
        scroll_count: Number of times to scroll down the page.
        scroll_pause: Time to wait between scrolls (in seconds).
        max_images: Maximum number of images to download.

    Returns:
        A list of image URLs.
    """

    options = Options()
    options.add_argument("--remote-debugging-address=localhost:9222") 

    driver = webdriver.Edge(options=options)
    driver.get(f"https://in.pinterest.com/search/pins/?q={search_term}")

    total_images = len(driver.find_elements(By.TAG_NAME, "img"))  # Get initial image count
    progress_bar = tqdm(total=total_images, unit="images", desc=f"Downloading {search_term}")

    for _ in range(scroll_count):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause)

        # Update progress bar (optional)
        current_images = len(driver.find_elements(By.TAG_NAME, "img"))
        progress_bar.update(current_images - total_images)
        total_images = current_images

    # Explicit wait for images to load (optional)
    try:
        WebDriverWait(driver, 60).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "img"))
        )
    except:
        print("Timeout waiting for images to load.")

    page_source = driver.page_source

    soup = BeautifulSoup(page_source, 'html.parser')

    # Attempt to find higher resolution images (if available)
    image_urls = []
    for img in soup.find_all('img'):
        srcset = img.get('srcset') 
        if srcset:
            # Extract the highest resolution image URL from srcset
            srcset_list = srcset.split(',')
            highest_res_url = srcset_list[-1].split(' ')[0]  # Get the URL of the last (usually highest resolution) image
            image_urls.append(highest_res_url)
        else:
            image_urls.append(img.get('src'))

    progress_bar.close()  # Close the progress bar 
    driver.quit()  # Close the browser after scraping

    # Limit the number of images to download
    image_urls = image_urls[:max_images] 

    return image_urls

def download_images(image_urls, search_term):
    """
    Downloads images from a list of URLs and saves them in a specific folder.

    Args:
        image_urls: A list of image URLs.
        search_term: The search term used to create the folder name.
    """

    download_folder = os.path.join("Documents", "testing_pin")  # Path to the 'testing_pin' folder
    os.makedirs(download_folder, exist_ok=True)  # Create the folder if it doesn't exist

    progress_bar_download = tqdm(total=len(image_urls), unit="images", desc=f"Downloading Images") 

    for i, url in enumerate(image_urls):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()  # Raise an exception for bad status codes

            file_name = f"{download_folder}/image_{i+1}.jpg"  # Customize filename format
            with open(file_name, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Downloaded {url} to {file_name}")
            progress_bar_download.update(1) 

        except requests.exceptions.RequestException as e:
            print(f"Error downloading {url}: {e}")
            progress_bar_download.update(1)  # Update progress bar even on errors

    progress_bar_download.close()

if __name__ == "__main__":
    search_term = input("Enter search term: ")
    max_images = int(input("Enter maximum number of images to download: ")) 
    image_urls = scrape_pinterest_images(search_term, max_images=max_images)
    download_images(image_urls, search_term)# ... (existing code)

if __name__ == "__main__":
    search_term = input("Enter search term: ")
    print(f"Search term: {search_term}")
    max_images = int(input("Enter maximum number of images to download: "))
    print(f"Max images: {max_images}")
    image_urls = scrape_pinterest_images(search_term, max_images=max_images)
    download_images(image_urls, search_term)
    print("Download complete!")
    time.sleep(2)  # Pause for 2 seconds before closing the browser