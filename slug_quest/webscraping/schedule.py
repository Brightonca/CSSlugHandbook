# -- WebScraper For UCSC Engineering Course Schedule -- $
# --- By: Kyle Delmo ---------------------------------- $

import requests
from bs4 import BeautifulSoup
import re
import json

# Gets all courses from the given year and quarter.
def extract_course_data(YEAR, QUARTER, QUARTER_INDEX):
    url = f"https://courses.engineering.ucsc.edu/courses/cse/{YEAR}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Matching href tags that point to the given quarter.
    quarter_link_pattern = re.compile(rf"^/courses/[^/]+/{QUARTER}/")

    # Storing results.
    results = []
    current_course_name = None

    # Getting all table rows.
    for row in soup.find_all("tr"):
        tds = row.find_all("td", recursive=False)

        # Getting the course name.
        if len(tds) == 1 and tds[0].has_attr('colspan'):
            course_link = tds[0].find("a")
            if course_link:
                current_course_name = course_link.get_text(strip=True)

        # Processing the section data row.
        elif len(tds) == 4:
            quarter_td = tds[QUARTER_INDEX]
            sections = {}

            for li in quarter_td.find_all("li"):
                a_tag = li.find("a", href=True)
                if a_tag and quarter_link_pattern.match(a_tag['href']):
                    section_name = a_tag.get_text(strip=True)
                    # Trying to get the instructor name.
                    instructor_text = li.get_text(separator=' ', strip=True).replace(section_name, '').strip()
                    if section_name and instructor_text:
                        sections[section_name] = instructor_text

            if sections:
                results.append({
                    'course': current_course_name,
                    'sections': sections
                })

    # Save to .json.
    filename = f"courses_{YEAR}_{QUARTER}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    # -- DEBUGGING; COMMENT OUT LATER -- #
    print(f"Saved {len(results)} courses to {filename}")
    # ---------------------------------- #

# # -- TESTING; COMMENT OUT LATER -- #
extract_course_data(2025, "Fall25", 0)
# # -------------------------------- #
