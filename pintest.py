from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import os

def scroll_down(driver):
    """Scroll down the page to load more content."""
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # Scroll to the bottom
    time.sleep(2)  # Wait for the new content to load

def collect_all_links(url, output_file="save.txt", max_links=10):
    # Set up the Edge WebDriver options
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
                # Now wait for all anchor tags to be present
                link_elements = WebDriverWait(driver, 15).until(
                    EC.presence_of_all_elements_located((By.TAG_NAME, "a"))
                )
                print(f"Found {len(link_elements)} links on the page.")

                # Collect href attributes from each link element
                for link in link_elements:
                    href = link.get_attribute("href")
                    if href and re.search(r'\d', href) and href.startswith("https://www.pinterest.com/pin/"):  
                        if href not in links:  # Avoid duplicates
                            links.append(href)
                            print(f"Found valid link: {href}")  # Log the found link

                    # Stop collecting links if we reach the maximum count
                    if len(links) >= max_links:
                        break

                # If we reached max_links, break out of the outer while loop as well
                if len(links) >= max_links:
                    break

            except Exception as e:
                print(f"An error occurred while collecting links: {e}")
                continue  # Continue scrolling if an error occurs

        # Save the collected links to a file
        with open(output_file, "w") as file:
            for link in links:
                file.write(link + "\n")

        print(f"Collected {len(links)} valid links and saved to {output_file}.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

def main():
    print("Choose an option:")
    print("1. Search for terms")
    print("2. Use a specific Pinterest link")
    
    while True:
        choice = input("Enter your choice (1 or 2): ")
        
        if choice == '1':
            while True:
                try:
                    num_searches = int(input("How many search terms do you want to enter? "))
                    if num_searches <= 0:
                        raise ValueError("Number of searches must be greater than zero.")
                    break
                except ValueError as ve:
                    print(f"Error: {ve}. Please enter a valid number.")

            while True:
                try:
                    max_links = int(input("Enter the maximum number of images to download for each search term: "))
                    if max_links <= 0:
                        raise ValueError("Maximum links must be greater than zero.")
                    break
                except ValueError as ve:
                    print(f"Error: {ve}. Please enter a valid number.")

            folder_name = input("Enter the name of the folder to save search term files: ")
            os.makedirs(folder_name, exist_ok=True)  # Create folder if it doesn't exist
            
            search_terms = []
            
            for i in range(num_searches):
                search_term = input(f"Enter search term {i + 1}: ")
                search_terms.append(search_term)

            # Now perform searches after collecting all terms
            for search_term in search_terms:
                search_url = f"https://www.pinterest.com/search/pins/?q={search_term.replace(' ', '%20')}&rs=typed"
                output_file = os.path.join(folder_name, f"{search_term}.txt")  # Save file named after the search term
                
                collect_all_links(search_url, output_file, max_links)

            break  # Exit after processing all searches

        elif choice == '2':
            pinterest_link = input("Paste your Pinterest link: ")
            while True:
                try:
                    max_links = int(input(f"Enter the maximum number of images to download from '{pinterest_link}': "))
                    if max_links <= 0:
                        raise ValueError("Maximum links must be greater than zero.")
                    break
                except ValueError as ve:
                    print(f"Error: {ve}. Please enter a valid number.")
            
            collect_all_links(pinterest_link, "save5.txt", max_links)  # Save to save5.txt
            
            break  # Exit after processing specific link

        else:
            print("Invalid choice! Please enter 1 or 2.")

if __name__ == "__main__":
    main()
