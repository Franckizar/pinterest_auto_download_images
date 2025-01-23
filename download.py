import requests
from bs4 import BeautifulSoup
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def download_image(url, folder, retries=3):
    """Download an image from a URL with retry logic."""
    attempt = 0
    while attempt < retries:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                # Extract the image filename from the URL
                filename = os.path.join(folder, url.split('/')[-1])
                with open(filename, 'wb') as file:
                    file.write(response.content)
                print(f"Image downloaded: {filename}")
                return  # Exit the function on successful download
            else:
                print(f"Failed to download image from {url} (Status code: {response.status_code})")
        except Exception as e:
            print(f"Error downloading image from {url}: {e}")

        attempt += 1
        print(f"Retrying... ({attempt}/{retries})")
        time.sleep(2)  # Wait before retrying

    print(f"Failed to download image from {url} after {retries} attempts.")

def collect_main_image_from_links(input_file, output_folder, max_retries=3):
    """Collect main images from links in a specified input file."""
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Read links from the input file
    with open(input_file, 'r') as file:
        links = file.readlines()

    download_tasks = []

    # Prepare to download images concurrently
    with ThreadPoolExecutor(max_workers=5) as executor:  # Adjust max_workers for more or fewer concurrent downloads
        for link in links:
            link = link.strip()  # Remove any whitespace characters
            if link and re.search(r'\d', link) and link.startswith("https://www.pinterest.com/pin/"):
                print(f"Visiting: {link}")
                try:
                    response = requests.get(link)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        # Find the main image tag (usually the first <img> tag or a specific class)
                        img_tag = soup.find('img')  # Adjust this selector if needed to target the main image
                        if img_tag:
                            img_url = img_tag.get('src')
                            if img_url and re.search(r'\d', img_url):  # Check if the image URL contains numbers
                                # Submit the download task to the executor with retry count
                                download_tasks.append(executor.submit(download_image, img_url, output_folder, max_retries))
                    else:
                        print(f"Failed to access {link} (Status code: {response.status_code})")
                except Exception as e:
                    print(f"Error accessing {link}: {e}")

        # Wait for all download tasks to complete
        for future in as_completed(download_tasks):
            future.result()  # This will also raise exceptions if any occurred during download

def main():
    # Prompt for parent folder name where all image folders will be saved
    parent_folder = input("Enter the name of the parent folder to save all images: ")
    os.makedirs(parent_folder, exist_ok=True)  # Create parent folder if it doesn't exist

    # Prompt for the folder containing text files with links
    links_folder = input("Enter the path of the folder containing text files with links: ")

    # Get all text files in the specified folder
    text_files = [f for f in os.listdir(links_folder) if f.endswith('.txt')]

    max_retries = int(input("Enter the maximum number of retries for downloading images: "))

    for text_file in text_files:
        input_file_path = os.path.join(links_folder, text_file)
        output_folder_name = os.path.splitext(text_file)[0]  # Remove .txt extension for folder name
        output_folder_path = os.path.join(parent_folder, output_folder_name)  # Create output folder path
        
        collect_main_image_from_links(input_file_path, output_folder_path, max_retries)

if __name__ == "__main__":
    main()
