import requests
from bs4 import BeautifulSoup
import re
import httpx
# base_url = "https://en.wikipedia.org/wiki/List_of_vegetables"

def remove_non_english(text):
    # regex pattern to match non-English characters
    non_english_pattern = re.compile(r'[^\x00-\x7F]+')
    
    # rm non-English characters from the text using regex
    clean_text = non_english_pattern.sub('', text)
    
    return clean_text

def get_vegetables():

    base_url = "https://en.wikipedia.org/wiki/List_of_vegetables"

    response = httpx.get(base_url)
    
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all <h2> tags (each one is a section of the page)
    sections = soup.find_all("h2")

    # Set of sections to skip on every wikipedia page
    skip_sections = set(["Contents", "See also", "See also[edit]", "References", "References[edit]", "External links", "External links[edit]"])
    
    sectionsMap = {}

    # Iterate through each <h2> tag
    for section in sections:
        header = section.text.strip()
        print("Heading:", header)

        # Remove the "[edit]" text from the header  
        header_key = header.replace("[edit]", "").strip()

        if header in skip_sections:
            print("--> Skipping section:", header)
            continue
        
        # Find tables within the current <h2> tag
        table = section.find_all_next('table')[0]

        rows = table.find_all("tr")

        row_list = []

        for row in rows:
            cell = row.find_all('td')
            cell_text = [c.get_text(strip=False) for c in cell]

            # remove non-English characters from the food name
            food_name = remove_non_english(cell_text[0])

            # split the food name by "("
            split_names = food_name.split("(")
            split_names = [n.replace(")", "").replace("(", "").strip().split("/") for n in split_names]
            split_names = [item for sublist in split_names for item in sublist]

            # make lower case, remove leading/trailing whitespace, and remove empty strings, and "leaves"
            lower_names = [n.lower().strip() for n in split_names]
            lower_names = [n for n in lower_names if n and n != "leaves"]

            row_list.extend(lower_names)

            # print(f"cell_text: {cell_text}")
            # print(f"-> food_name: {food_name}")
            # print(f"--> split_names: {split_names}")
            # print(f"-----> lower_names: {lower_names}")
            # print(f"\n")

        print(f"Adding {len(row_list)} items to the {header_key} section")
        sectionsMap[header_key] = list(set(row_list))

        print(f"\n")

    return sectionsMap
