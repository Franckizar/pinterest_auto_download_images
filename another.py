from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re  # Import the regular expression module

def scroll_down(driver, scrolls):
    """Scroll down the page a specified number of times."""
    for _ in range(scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # Scroll to the bottom
        time.sleep(2)  # Wait for the new content to load

def collect_all_links(url, output_file="save2.txt", scrolls=5, max_links=10):
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

        # Scroll down the specified number of times
        scroll_down(driver, scrolls)

        # Now wait for all anchor tags to be present
        link_elements = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "a"))
        )
        print(f"Found {len(link_elements)} links on the page.")

        links = []

        # Collect href attributes from each link element
        for link in link_elements:
            href = link.get_attribute("href")
            if href and re.search(r'\d', href) and href.startswith("https://www.pinterest.com/pin/"):  
                links.append(href)
                print(f"Found valid link: {href}")  # Log the found link
            
            # Stop collecting links if we reach the maximum count
            if len(links) >= max_links:
                break

        # Save the collected links to a file
        with open(output_file, "w") as file:
            for link in links:
                file.write(link + "\n")

        print(f"Collected {len(links)} valid links and saved to {output_file}.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

# Replace with the desired URL to scrape, specify number of scrolls and max links
collect_all_links("https://www.pinterest.com/pin/334955291048958012/", scrolls=20, max_links=50)
