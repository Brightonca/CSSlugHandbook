# --- WebScraper For RMP ----------------- #
# --- By: Kyle Delmo --------------------- #

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# Gets the information of a professor from the given university.
def get_professor_info(name, university="University of California Santa Cruz"):
    # Setup Chrome options
    options = Options()
    options.add_argument("--headless")  # run in background
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Formatted search url given the name of the professor (has to be exact).
    search_url = f"https://www.ratemyprofessors.com/search/professors?q={name.replace(' ', '%20')}"
    driver.get(search_url)

    try:
        # Wait until the resulting list of professors load.
        # 3 SECOND DELAY; INITIALLY 10 SECONDS; CHANGE AT YOUR OWN RISK.
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/professor/']"))
        )

        cards = driver.find_elements(By.CSS_SELECTOR, "a[href*='/professor/']")
        prof_url = None
        prof_name = None
        school = None
        
        for card in cards:
            try:
                prof_name = card.find_element(By.CSS_SELECTOR, "div.CardName__StyledCardName-sc-1gyrgim-0").text.strip()
                school = card.find_element(By.CSS_SELECTOR, "div.CardSchool__School-sc-19lmz2k-1").text.strip()
                if name.lower() == prof_name.lower() and university.lower() in school.lower():
                    prof_url = card.get_attribute("href")
                    print(prof_url)
                    print(f"Found match: {prof_name} at {school}")
                    break
            except Exception as e:
                print(f"Card parsing error: {e}")
                continue

        if prof_url is None:
            print(f"No matching professor found for {name} at {university}")
            driver.quit()
            return None

        # Go to the professor's page.
        # 3 SECOND DELAY; INITIALLY 10; CHANGE AT YOUR OWN RISK.
        driver.get(prof_url)
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.RatingValue__Numerator-qw8sqy-2"))
        )

        # Getting the professor's rating, tags, whether or not students would take them again, and
        # the perceived difficulty.
        rating = driver.find_element(By.CSS_SELECTOR, "div.RatingValue__Numerator-qw8sqy-2.duhvlP").text
        tags_elements = driver.find_elements(By.CSS_SELECTOR, "span.Tag-bs9vf4-0.bmtbjB")
        tags = [tag.text.strip() for tag in tags_elements]
        feedback_blocks = driver.find_elements(By.CSS_SELECTOR, "div.FeedbackItem__StyledFeedbackItem-uof32n-0")

        take_again = None
        difficulty = None

        for block in feedback_blocks:
            try:
                label = block.find_element(By.CSS_SELECTOR, "div.FeedbackItem__FeedbackDescription-uof32n-2").text.strip()
                value = block.find_element(By.CSS_SELECTOR, "div.FeedbackItem__FeedbackNumber-uof32n-1").text.strip()

                if "Would take again" in label:
                    take_again = value
                elif "Level of Difficulty" in label:
                    difficulty = value
            except Exception as e:
                print(f"Error parsing feedback block: {e}")

        # -- COMMENT OUT LATER; FOR DEBUGGING PURPOSES -- #
        print(f"Rating: {rating}")
        print(f"Difficulty: {difficulty}")
        print(f"Would Take Again: {take_again}")
        print(f"Tags: {tags}")
        # ----------------------------------------------- #

        driver.quit()
        return {
            "name": prof_name,
            "university": school,
            "rating": rating,
            "difficulty": difficulty,
            "take_again": take_again,
            "tags": tags
        }

    except Exception as e:
        print(f"Error: {e}")
        driver.quit()
        return None

# # Testing.
# professor = "Patrick Tantalo"
# prof_info = get_professor_info(professor)
# print(prof_info)