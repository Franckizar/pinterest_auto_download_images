import requests
from bs4 import BeautifulSoup
import re
import os

def collect_links_from_search(query, max_links, output_file="save.txt"):
    # Prepare the search URL
    search_url = f"https://www.pinterest.com/search/pins/?q={query.replace(' ', '%20')}&rs=typed"
    
    print(f"Searching for: {query}")
    try:
        response = requests.get(search_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            links = []

            # Find all pin elements (this selector may need adjustment based on Pinterest's HTML structure)
            pin_elements = soup.find_all('a', href=re.compile(r'^/pin/'))

            for pin in pin_elements:
                href = pin.get('href')
                if href:
                    full_link = f"https://www.pinterest.com{href}"
                    links.append(full_link)
                    print(f"Found link: {full_link}")

                # Stop collecting links if we reach the maximum count
                if len(links) >= max_links:
                    break

            # Save the collected links to a file
            with open(output_file, "w") as file:
                for link in links:
                    file.write(link + "\n")

            print(f"Collected {len(links)} links and saved to {output_file}.")
        else:
            print(f"Failed to access search results (Status code: {response.status_code})")
    except Exception as e:
        print(f"An error occurred while searching: {e}")

def main():
    # Prompt user for a search term and maximum number of links
    search_query = input("Enter your search term: ")
    max_links = int(input("Enter the maximum number of links to collect: "))
    output_file = "save4.txt"  # You can change this to any filename you prefer
    collect_links_from_search(search_query, max_links, output_file)

if __name__ == "__main__":
    main()
