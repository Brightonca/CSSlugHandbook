# --- WebScraper For UCSC Class Search --- #
# --- By: Kyle Delmo --------------------- #

import json
import requests
from bs4 import BeautifulSoup

# Returns the total number of courses in the results from the first preliminary search.
def get_total_results(soup):
    summary_div = soup.select_one('div.row.hide-print[style*="background-color"]')
    if summary_div:
        bold_tags = summary_div.find_all('b')
        if len(bold_tags) >= 3:
            try:
                return int(bold_tags[2].text)
            except ValueError:
                pass
    return 25

# Looks for a div that contains the given keyword (e.g. "Instructor:", "Location:")
# Returns the text associated with that keyword.
def get_field_text(panel, keyword):
    for div in panel.select("div.col-xs-6.col-sm-3, div.col-xs-6.col-sm-6"):
        if div and keyword in div.get_text():
            return div.get_text(strip=True).replace(f"{keyword}:", "").strip()
    return "N/A"

# Given a term and a subject, fetches the list of courses from the UCSC Class
# Search and saves them into a .json file.
def fetch_and_scrape_all(term, subject):

    # URL for UCSC Class Search.
    url = "https://pisa.ucsc.edu/class_search/index.php"
    headers = {"User-Agent": "Mozilla/5.0"}

    # Search filters.
    initial_payload = {
        "action": "results",
        "binds[:term]": term,
        "binds[:reg_status]": "all",
        "binds[:subject]": subject,
        "binds[:asynch]": "A",
        "binds[:hybrid]": "H",
        "binds[:synch]": "S",
        "binds[:person]": "P",
        "rec_start": "0",
        "rec_dur": "25"
    }

    # -- COMMENT OUT LATER; FOR DEBUGGING PURPOSES -- #
    print("Fetching total class count...")
    # ----------------------------------------------- #
    
    # Getting how many results there are as a preliminary action
    # so that for the next request, it knows how many classes to
    # display, thus making it easier to scrape.
    resp1 = requests.post(url, data=initial_payload, headers=headers)
    soup1 = BeautifulSoup(resp1.text, "html.parser")
    total_results = get_total_results(soup1)

    # -- COMMENT OUT LATER; FOR DEBUGGING PURPOSES -- #
    print(f"Total classes found: {total_results}")
    # ----------------------------------------------- #

    # Second request, showing all classes.
    full_payload = initial_payload.copy()
    full_payload["rec_dur"] = str(total_results)

    # -- COMMENT OUT LATER; FOR DEBUGGING PURPOSES -- #
    print("Fetching all results...")
    # ----------------------------------------------- #
    
    # Getting classes from second request.
    resp2 = requests.post(url, data=full_payload, headers=headers)
    soup2 = BeautifulSoup(resp2.text, "html.parser")
    panels = soup2.select("div.panel.panel-default.row")

    # For .json purposes.
    all_classes = []
    
    # Iterating through each class.
    for panel in panels:

        # Getting the class name.
        title_tag = panel.select_one("div.panel-heading a")
        title = title_tag.text.strip() if title_tag else "N/A"

        # Getting important information about the class.
        instructor = get_field_text(panel, "Instructor")
        location = get_field_text(panel, "Location")
        time = get_field_text(panel, "Day and Time")
        session = get_field_text(panel, "Session")
        enrollment = get_field_text(panel, "Enrolled")

        # Getting the instruction mode of the class.
        instruction_mode = "N/A"
        for b in panel.select("div.panel-body b"):
            if b.text in ["In Person", "Synchronous Online", "Asynchronous Online", "Hybrid"]:
                instruction_mode = b.text
                break

        # Storing the class info in a dictionary (.json).
        class_info = {
            "title": title,
            "instructor": instructor,
            "location": location,
            "time": time,
            "instruction_mode": instruction_mode,
            "enrollment": enrollment
        }

        # Adding it to the whole data structure.
        all_classes.append(class_info)
    
    # Saving the .json file.
    with open("classes.json", "w", encoding="utf-8") as f:
        json.dump(all_classes, f, indent=2)

    # -- COMMENT OUT LATER; FOR DEBUGGING PURPOSES -- #
    print("Data saved to classes.json")
    # ----------------------------------------------- #

# 2252 = 2025 Spring Quarter (adjacent quarters differ by 2).
fetch_and_scrape_all("2256", "CSE")
