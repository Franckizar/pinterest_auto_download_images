from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def scroll_down(driver):
    """Scroll down the page to load more content."""
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # Scroll to the bottom
    time.sleep(2)  # Wait for the new content to load

def collect_all_links(url, output_file="save.txt", max_links=10):
    """Collect Pinterest links from a search URL."""
    options = webdriver.EdgeOptions()
    options.add_argument("--start-maximized")
    options.add_experimental_option("detach", True)  # Keep the browser open after script ends
    
    driver = webdriver.Edge(options=options)

    try:
        driver.get(url)

        # Wait for the page to load by checking for the presence of the body tag
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))  # Wait until the body tag is present
        )
        print("Page has fully loaded.")

        links = []

        # Scroll and collect links until we reach the maximum count
        while len(links) < max_links:
            scroll_down(driver)

            try:
                link_elements = WebDriverWait(driver, 15).until(
                    EC.presence_of_all_elements_located((By.TAG_NAME, "a"))
                )
                print(f"Found {len(link_elements)} links on the page.")

                for link in link_elements:
                    href = link.get_attribute("href")
                    if href and re.search(r'\d', href) and href.startswith("https://www.pinterest.com/pin/"):
                        if href not in links:  # Avoid duplicates
                            links.append(href)
                            print(f"Found valid link: {href}")

                    if len(links) >= max_links:
                        break

                if len(links) >= max_links:
                    break

            except Exception as e:
                print(f"An error occurred while collecting links: {e}")
                continue

        with open(output_file, "w") as file:
            for link in links:
                file.write(link + "\n")

        print(f"Collected {len(links)} valid links and saved to {output_file}.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

def download_image(url, folder, retries=3):
    """Download an image from a URL with retry logic."""
    attempt = 0
    while attempt < retries:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                filename = os.path.join(folder, url.split('/')[-1])
                with open(filename, 'wb') as file:
                    file.write(response.content)
                print(f"Image downloaded: {filename}")
                return
            else:
                print(f"Failed to download image from {url} (Status code: {response.status_code})")
        except Exception as e:
            print(f"Error downloading image from {url}: {e}")

        attempt += 1
        print(f"Retrying... ({attempt}/{retries})")
        time.sleep(2)

    print(f"Failed to download image from {url} after {retries} attempts.")

def collect_main_image_from_links(input_file, output_folder, max_retries=3):
    """Collect main images from links in a specified input file."""
    os.makedirs(output_folder, exist_ok=True)

    with open(input_file, 'r') as file:
        links = file.readlines()

    download_tasks = []

    with ThreadPoolExecutor(max_workers=5) as executor:
        for link in links:
            link = link.strip()
            if link and re.search(r'\d', link) and link.startswith("https://www.pinterest.com/pin/"):
                print(f"Visiting: {link}")
                try:
                    response = requests.get(link)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        img_tag = soup.find('img')
                        if img_tag:
                            img_url = img_tag.get('src')
                            if img_url and re.search(r'\d', img_url):
                                download_tasks.append(executor.submit(download_image, img_url, output_folder, max_retries))
                    else:
                        print(f"Failed to access {link} (Status code: {response.status_code})")
                except Exception as e:
                    print(f"Error accessing {link}: {e}")

        for future in as_completed(download_tasks):
            future.result()

def main():
    # Collect all necessary inputs at once
    parent_folder = input("Enter the name of the parent folder to save all images: ")
    os.makedirs(parent_folder, exist_ok=True)

    choice = input("Choose an option:\n1. Search for terms\n2. Use specific Pinterest links\nEnter your choice (1 or 2): ")

    if choice == '1':
        num_searches = int(input("How many search terms do you want to enter? "))
        
        while True:
            try:
                max_links = int(input("Enter the maximum number of images to download for each search term: "))
                if max_links <= 0:
                    raise ValueError("Maximum links must be greater than zero.")
                break
            except ValueError as ve:
                print(f"Error: {ve}. Please enter a valid number.")

        search_terms = []
        
        for i in range(num_searches):
            search_term = input(f"Enter search term {i + 1}: ")
            search_terms.append(search_term)

        # Now perform searches after collecting all terms
        for search_term in search_terms:
            search_url = f"https://www.pinterest.com/search/pins/?q={search_term.replace(' ', '%20')}&rs=typed"
            output_file = os.path.join(parent_folder, f"{search_term}.txt")  # Save file named after the search term
            
            collect_all_links(search_url, output_file, max_links)

        # After collecting all links for each term, download images from each collected file
        for search_term in search_terms:
            input_file_path = os.path.join(parent_folder, f"{search_term}.txt")
            output_folder_name = os.path.splitext(search_term)[0]
            output_folder_path = os.path.join(parent_folder, output_folder_name)
            
            collect_main_image_from_links(input_file_path, output_folder_path, max_retries=3)

    elif choice == '2':
        num_links = int(input("How many Pinterest links do you want to paste? "))
        
        pinterest_links = []
        
        for i in range(num_links):
            pinterest_link = input(f"Paste Pinterest link {i + 1}: ")
            pinterest_links.append(pinterest_link)
        
        while True:
            try:
                max_links = int(input("Enter the maximum number of images to download from each link: "))
                if max_links <= 0:
                    raise ValueError("Maximum links must be greater than zero.")
                break
            except ValueError as ve:
                print(f"Error: {ve}. Please enter a valid number.")
                
        while True:
            try:
                max_retries = int(input("Enter the maximum number of retries for downloading images: "))
                if max_retries < 0:
                    raise ValueError("Maximum retries must be zero or greater.")
                break
            except ValueError as ve:
                print(f"Error: {ve}. Please enter a valid number.")

        # Collect images from each pasted link and save them into save5.txt
        save5_path = os.path.join(parent_folder, "save5.txt")
        
        with open(save5_path, "w") as save5_file:
            for pinterest_link in pinterest_links:
                collect_all_links(pinterest_link, save5_path, max_links)  # Save to save5.txt

        # After collecting all images from pasted links, download them using save5.txt
        collect_main_image_from_links(save5_path, os.path.join(parent_folder, "Downloaded_Images"), max_retries)

if __name__ == "__main__":
    main()
