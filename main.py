import os
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import re
import time

def get_edge_driver():
    # Check if the Edge WebDriver is in the system PATH
    driver_path = None
    try:
        driver_path = webdriver.Edge().service.path  # Try to use the system PATH
    except Exception:
        # WebDriver isn't found in PATH, so look in specific folder
        possible_paths = [
            os.path.join(os.getcwd(), "msedgedriver.exe"),  # Current directory
            "C:/path/to/your/msedgedriver.exe"  # You can specify a path here as well
        ]
        for path in possible_paths:
            if os.path.exists(path):
                driver_path = path
                break
    if not driver_path:
        raise FileNotFoundError("Edge WebDriver (msedgedriver.exe) not found!")
    
    return driver_path


def main():
    # Get the path for msedgedriver dynamically
    msedge_driver_path = get_edge_driver()

    # Open Animepahe Website
    options = webdriver.EdgeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    # Create Edge driver with the specified path to msedgedriver
    driver = webdriver.Edge(service=Service(msedge_driver_path), options=options)
    driver.get("https://animepahe.com/")
    actionChains = ActionChains(driver)
    time.sleep(2)

    # Put anime text here
    anime = "Mairimashita! Iruma-kun 3rd Season"

    # Type the quality of video here
    pixels = "720"

    # Search anime
    search = driver.find_element(By.NAME, "q")
    search.send_keys(anime + " ")
    time.sleep(2)

    # Click the first element in the result
    try:
        search_result = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "search-results"))
        )
        first_element = search_result.find_element(By.TAG_NAME, "li").find_element(By.TAG_NAME, "a")
        first_element.click()
        time.sleep(2)
    except Exception as e:
        print(f"Anime Not Found! {e}")

    # Get the total number of Anime Episodes
    try:
        total_episode = driver.find_element(By.CLASS_NAME, "episode-count")
        num_episode = re.findall(r'[0-9]+', total_episode.text)
        print(f"Total Episodes: {num_episode[0]}")
    except Exception as e:
        print(f"Error fetching total episodes: {e}")

    # Click Ascending Button
    try:
        ascending_btn = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "episode_asc"))
        )
        actionChains.double_click(ascending_btn).perform()
    except Exception as e:
        print(f"Error in clicking Ascending Button: {e}")

    time.sleep(5)

    # Click First Episode
    try:
        first_episode = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "episode-list"))
        )
        first_episode_div = first_episode.find_element(By.TAG_NAME, "div").find_element(By.TAG_NAME, "a")
        first_episode_div.click()
        time.sleep(2)
    except Exception as e:
        print(f"First Episode Not Found: {e}")

    # Loop through all episodes
    for i in range(int(num_episode[0])):
        time.sleep(3)

        # Click the download button
        try:
            download_btn = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "downloadMenu"))
            )
            download_btn.click()
        except Exception as e:
            print(f"Error in clicking download button: {e}")

        # Click 720p Link
        try:
            dropdown_download = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "pickDownload"))
            )
            driver.implicitly_wait(5)
            choices = dropdown_download.find_elements(By.CLASS_NAME, "dropdown-item")

            for choice in choices:
                if pixels + "p" in choice.text:
                    choice.click()
                    break
        except Exception as e:
            print(f"Error in clicking 720 link: {e}")

        # Click Pahewin Continue button
        driver.switch_to.window(driver.window_handles[-1])
        driver.implicitly_wait(5)

        try:
            continue_vid = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.LINK_TEXT, "Continue"))
            )
            continue_vid.click()
        except Exception as e:
            print(f"Error in clicking continue button: {e}")

        # Click Download button in Kwik
        try:
            kwik_download_btn = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, "button"))
            )
            kwik_download_btn.click()
            time.sleep(5)
        except Exception as e:
            print(f"Error in clicking Kwik download button: {e}")

        # Close the kwik tab
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        driver.implicitly_wait(2)

        # Click the next episode button
        try:
            next_episode = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[title^='Play Next Episode']"))
            )
            next_episode.click()
        except Exception as e:
            print(f"Error in clicking next episode button: {e}")

    # Close the browser
    driver.quit()

if __name__ == "__main__":
    main()
