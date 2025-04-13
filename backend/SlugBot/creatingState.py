import re
import json
from pypdf import PdfReader
from webscraping.schedule import extract_course_data
from webscraping.rmp import get_professor_info
from state import state as shared_state

# =============================================================================
# Data Classes: User and Course
# =============================================================================
class User:
    def __init__(self, name, credits_taken=0, classes_taken=None, gpa=0.0):
        self.name = name
        self.credits_taken = credits_taken
        self.classes_taken = classes_taken if classes_taken is not None else []
        self.gpa = gpa

    def add_course(self, course):
        self.classes_taken.append(course)

    def get_courses_by_quarter(self, quarter):
        return [course for course in self.classes_taken if course.quarter == quarter]

    def __str__(self):
        courses_str = "\n".join(f"- {course}" for course in self.classes_taken)
        return (f"User: {self.name}\n"
                f"Credits Taken: {self.credits_taken}\n"
                f"GPA: {self.gpa}\n"
                f"Courses Taken:\n{courses_str}")

class Course:
    def __init__(self, code, quarter, credits):
        self.code = code   # e.g., "CSE 12", "MATH 19A", etc.
        self.quarter = quarter
        self.credits = credits

    def __str__(self):
        return f"{self.code} - {self.quarter} ({self.credits} credits)"


# =============================================================================
# Constants: Requirements, Allowed Courses, and Prerequisites
# =============================================================================
requirements = {
    "Lower_Division": {
        "Computer_Science_and_Engineering": {
            "mandatory": ["CSE 12", "CSE 16", "CSE 20", "CSE 30", "CSE 40"],
            "additional": ["CSE 13S"]
        },
        "Mathematics": {
            "one_of": [
                ["MATH 19A", "MATH 19B"],
                ["MATH 20A", "MATH 20B"]
            ]
        },
        "Applied_Mathematics": {
            "one_of": [["AM 10"], ["MATH 21"]],
            "plus_one_of": [["AM 30", "MATH 23A"]]
        },
        "Engineering_Science": {
            "mandatory": ["ECE 30"]
        }
    },
    "Upper_Division": {
        "Core_Computer_Science": {
            "mandatory": ["CSE 101", "CSE 101M", "CSE 120", "CSE 130"],
            "one_of": [
                ["CSE 102", "CSE 103"],
                ["CSE 112", "CSE 114A"]
            ]
        },
        "Statistics": {"one_of": [["STAT 131", "CSE 107"]]},
        "DC": {"one_of": [["CSE 115A", "CSE 185E", "CSE 195"]]},
        "Capstone": {
            "one_of": [[
                "CSE 110B", "CSE 115C", "CSE 115D", "CSE 121", "CSE 134", "CSE 138",
                "CSE 140", "CSE 143", "CSE 144", "CSE 145", "CSE 156+L", "CSE 156L",
                "CSE 157", "CSE 160", "CSE 161+L", "CSE 161L", "CSE 162+L", "CSE 162L",
                "CSE 163", "CSE 168", "CSE 181", "CSE 183", "CSE 184", "CSE 187",
                "CMPM 172"
            ]]
        }
    },
    "Electives": {
        "number_required": 4,
        "list": [
            "AM 114", "AM 147", "CMPM 120", "CMPM 131", "CMPM 146",
            "CMPM 163", "CMPM 164+L", "CMPM 164L", "CMPM 171", "CMPM 172",
            "MATH 110", "MATH 115", "MATH 116", "MATH 117", "MATH 118",
            "MATH 134", "MATH 145+L", "MATH 145L", "MATH 148", "MATH 160",
            "MATH 161", "STAT 132"
        ]
    }
}

allowed_lower = [
    "CSE 12", "CSE 16", "CSE 20", "CSE 30", "CSE 40", "CSE 13S",
    "MATH 19A", "MATH 19B", "MATH 20A", "MATH 20B",
    "AM 10", "MATH 21", "AM 30", "MATH 23A", "ECE 30"
]
allowed_upper_core = [
    "CSE 101", "CSE 101M", "CSE 120", "CSE 130",
    "CSE 102", "CSE 103", "CSE 112", "CSE 114A", "STAT 131", "CSE 107"
]
allowed_dc = ["CSE 115A", "CSE 185E", "CSE 195"]
allowed_capstone = [
    "CSE 110B", "CSE 115C", "CSE 115D", "CSE 121", "CSE 134", "CSE 138",
    "CSE 140", "CSE 143", "CSE 144", "CSE 145", "CSE 156+L", "CSE 156L",
    "CSE 157", "CSE 160", "CSE 161+L", "CSE 161L", "CSE 162+L", "CSE 162L",
    "CSE 163", "CSE 168", "CSE 181", "CSE 183", "CSE 184", "CSE 187",
    "CMPM 172"
]
allowed_electives = [
    "AM 114", "AM 147", "CMPM 120", "CMPM 131", "CMPM 146",
    "CMPM 163", "CMPM 164+L", "CMPM 164L", "CMPM 171", "CMPM 172",
    "MATH 110", "MATH 115", "MATH 116", "MATH 117", "MATH 118",
    "MATH 134", "MATH 145+L", "MATH 145L", "MATH 148", "MATH 160",
    "MATH 161", "STAT 132"
]
allowed_courses = set(allowed_lower + allowed_upper_core + allowed_dc + allowed_capstone + allowed_electives)
all_courses = list(allowed_courses)

prerequisites = {
    # Lower Division
    "CSE 12": [["CSE 30"]],
    "CSE 16": [["MATH 19A"]],
    "CSE 20": [],
    "CSE 30": [["CSE 20"]],
    "CSE 40": [["CSE 30"], ["MATH 19B", "MATH 20B"]],
    "CSE 13S": [["CSE 12"]],
    "MATH 19A": [],
    "MATH 19B": [["MATH 19A"]],
    "MATH 20A": [],
    "MATH 20B": [["MATH 20A"]],
    "AM 10": [],
    "MATH 21": [["MATH 11A", "MATH 19A", "MATH 20A"]],
    "AM 30": [["AM 10", "MATH 21"], ["MATH 19B"]],
    "MATH 23A": [["MATH 19B", "MATH 20A"]],
    "ECE 30": [],
    # Upper Division Core
    "CSE 101": [["CSE 13S"], ["CSE 16"], ["CSE 30"]],
    "CSE 101M": [["CSE 101"]],
    "CSE 120": [["CSE 13S"], ["CSE 16"]],
    "CSE 130": [["CSE 101"]],
    "CSE 102": [["CSE 101"]],
    "CSE 103": [["CSE 101"]],
    "CSE 112": [["CSE 101"]],
    "CSE 114A": [["CSE 101"]],
    "STAT 131": [["MATH 11A", "MATH 19A", "MATH 20A"]],
    "CSE 107": [["CSE 16"], ["AM 30", "MATH 23A", "MATH 22"]],
    # DC Options
    "CSE 115A": [["CSE 101"], ["CSE 130"]],
    "CSE 185E": [["CSE 12", "CSE 30"]],
    "CSE 195": [["CSE 123A", "CSE 129"]],
    # Capstone Courses
    "CSE 110B": [["CSE 110A"]],
    "CSE 115C": [["CSE 115B"]],
    "CSE 115D": [["CSE 115A"]],
    "CSE 121": [["CSE 100"], ["CSE 13S"], ["ECE 101"], ["PHYS 5C"], ["PHYS 5N"]],
    "CSE 134": [["CSE 120"], ["CSE 130"]],
    "CSE 138": [["CSE 130", "CSE 131"]],
    "CSE 140": [["CSE 101"], ["CSE 40", "STAT 132"]],
    "CSE 143": [["CSE 101"], ["CSE 107", "STAT 131"], ["CSE 40"]],
    "CSE 144": [["CSE 40", "STAT 132"], ["CSE 101"]],
    "CSE 145": [["CSE 30", "CSE 13S"], ["AM 30", "MATH 23A", "MATH 22"], ["STAT 5", "CSE 107", "STAT 131"], ["AM 10", "MATH 21"], ["CSE 16", "ECON 113"]],
    "CSE 156+L": [["CSE 150"], ["CSE 101"]],
    "CSE 156L": [["CSE 156+L"]],
    "CSE 157": [["CSE 121"], ["CSE 150"]],
    "CSE 160": [["CSE 101"], ["AM 10", "MATH 21"]],
    "CSE 161+L": [["CSE 160"]],
    "CSE 161L": [["CSE 161+L"]],
    "CSE 162+L": [["CSE 101"], ["AM 10", "MATH 21"]],
    "CSE 162L": [["CSE 162+L"]],
    "CSE 163": [["CSE 101"]],
    "CSE 168": [["CSE 160"]],
    "CSE 181": [["CSE 180"]],
    "CSE 183": [["CSE 101", "CMPM 35"]],
    "CSE 184": [["CSE 101"]],
    "CSE 187": [["CSE 186"]],
    # Electives (Mathematics/AM)
    "AM 114": [["AM 10", "MATH 21"], ["MATH 24", "AM 20"], ["AM 30", "MATH 23A", "MATH 22"]],
    "AM 147": [["AM 10", "MATH 21"]],
    "MATH 110": [["MATH 100", "CSE 101"]],
    "MATH 115": [["MATH 21", "AM 10"], ["MATH 100", "CSE 101"]],
    "MATH 116": [["MATH 100", "CSE 101"]],
    "MATH 117": [["MATH 21", "AM 10"], ["MATH 100", "CSE 101"]],
    "MATH 118": [["MATH 110", "MATH 11A"]],
    "MATH 134": [["MATH 100", "CSE 101"]],
    "MATH 145+L": [["MATH 22", "MATH 23A"], ["MATH 21", "AM 10"], ["MATH 100", "CSE 101"]],
    "MATH 145L": [["MATH 145+L"]],
    "MATH 148": [["MATH 22", "MATH 23A"], ["MATH 21", "AM 10"], ["MATH 103A", "MATH 105A", "MATH 152", "AM 147", "CSE 101"]],
    "MATH 160": [["MATH 100", "CSE 101"]],
    "MATH 161": [["MATH 100"]],
    "STAT 132": [["STAT 131", "CSE 107"]],
    # Electives (CMPM)
    "CMPM 120": [["CMPM 80K"], ["FILM 80V"], ["CSE 30", "CMPM 35"]],
    "CMPM 131": [["cred 90>"]],
    "CMPM 146": [["CSE 101"]],
    "CMPM 163": [["CSE 120"]],
    "CMPM 164+L": [["CMPM 163", "CSE 160"], ["CSE 160"]],
    "CMPM 164L": [["CMPM 164+L"]],
    "CMPM 171": [["CMPM 121"], ["CMPM 130"], ["CMPM 170"], ["CMPM 176"]],
    "CMPM 172": [["CMPM 171"]]
}
prerequisites = {k: v for k, v in prerequisites.items() if k in allowed_courses}


# =============================================================================
# Class: TranscriptParser
# =============================================================================
class TranscriptParser:
    """
    Extracts text from a PDF transcript and parses the student information.
    """
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.text = self._read_pdf()

    def _read_pdf(self):
        reader = PdfReader(self.pdf_path)
        textdata = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                textdata += text
        return textdata

    def parse_user(self):
        # Extract student's name.
        name_match = re.search(r"Name:\s*(.+)", self.text)
        full_name = name_match.group(1).strip() if name_match else "Unknown"
        if full_name == "Unknown":
            print("Error: Unable to extract student's name.")
        user = User(name=full_name)

        # Parse course lines.
        current_quarter = None
        lines = self.text.splitlines()
        quarter_pattern = re.compile(r'^(\d{4}\s+(Summer|Fall|Winter|Spring)\s+Quarter)')
        course_pattern = re.compile(
            r'^([A-Z]+\s*\d+[A-Z]*)\s+[\w:,&\-/]+(?:\s+[\w:,&\-/]+)*\s+([\d]+\.[\d]+)\s+([\d]+\.[\d]+)\s+[A-F][+-]?\s+[\d]+\.[\d]+'
        )
        for line in lines:
            line = line.strip()
            q_match = quarter_pattern.match(line)
            if q_match:
                current_quarter = q_match.group(0)
                continue
            c_match = course_pattern.match(line)
            if c_match and current_quarter:
                course_code = c_match.group(1)
                if course_code not in allowed_courses:
                    continue
                credits = float(c_match.group(2))
                course = Course(code=course_code, quarter=current_quarter, credits=credits)
                user.add_course(course)

        # Extract cumulative GPA and credits.
        cum_matches = re.findall(r'Cum GPA\s+([\d.]+).*?Cum Totals\s+([\d.]+)', self.text, flags=re.DOTALL)
        if cum_matches:
            last_gpa, last_credits = cum_matches[-1]
            user.gpa = float(last_gpa)
            user.credits_taken = float(last_credits)
        else:
            print("Error: Unable to extract cumulative GPA and credit totals.")
        return user


# =============================================================================
# Class: CurriculumRequirements
# =============================================================================
class CurriculumRequirements:
    """
    Manages curriculum requirements and computes remaining requirements
    as well as eligible courses based on the transcript.
    """
    def __init__(self, user, requirements, prerequisites, all_courses):
        self.user = user
        self.requirements = requirements
        self.prerequisites = prerequisites
        self.all_courses = all_courses

    def _check_requirement_group(self, group, completed):
        return [course for course in group if course not in completed]

    def _check_one_of_group(self, groups, completed):
        missing_options = []
        for alternatives in groups:
            missing = [course for course in alternatives if course not in completed]
            missing_options.append(missing)
        if any(len(missing) == 0 for missing in missing_options):
            return []
        return min(missing_options, key=len)

    def _enhance_completed(self, completed):
        """Auto-add prerequisites based on equivalencies."""
        enhanced = set(completed)
        if "CSE 30" in enhanced:
            enhanced.add("CSE 20")
        if "MATH 19B" in enhanced:
            enhanced.add("MATH 19A")
            enhanced.add("MATH 20A")
            enhanced.add("MATH 20B")
        if "MATH 20B" in enhanced:
            enhanced.add("MATH 20A")
        if "MATH 21" in enhanced:
            enhanced.add("AM 10")
        if "AM 10" in enhanced:
            enhanced.add("MATH 21")
        if "MATH 23A" in enhanced:
            enhanced.add("AM 30")
        if "AM 30" in enhanced:
            enhanced.add("MATH 23A")
        return enhanced

    @property
    def remaining_requirements(self):
        completed = {course.code for course in self.user.classes_taken}
        completed = self._enhance_completed(completed)
        remaining = {}
        for cat, subreqs in self.requirements.items():
            remaining[cat] = {}
            if cat == "Electives":
                required = subreqs.get("number_required", 0)
                elective_list = subreqs.get("list", [])
                electives_done = sum(1 for c in elective_list if c in completed)
                if electives_done < required:
                    remaining[cat]["Electives"] = f"{required - electives_done} elective(s) remaining"
            else:
                for subcat, req in subreqs.items():
                    if not isinstance(req, dict):
                        continue
                    if "mandatory" in req:
                        missing = self._check_requirement_group(req["mandatory"], completed)
                        if missing:
                            remaining[cat][f"{subcat} (mandatory)"] = missing
                    if "additional" in req:
                        missing = self._check_requirement_group(req["additional"], completed)
                        if missing:
                            remaining[cat][f"{subcat} (additional)"] = missing
                    if "one_of" in req:
                        missing = self._check_one_of_group(req["one_of"], completed)
                        if missing:
                            remaining[cat][f"{subcat} (one_of)"] = missing
                    if "plus_one_of" in req:
                        missing = self._check_one_of_group(req["plus_one_of"], completed)
                        if missing:
                            remaining[cat][f"{subcat} (plus_one_of)"] = missing
        return remaining

    @property
    def eligible_courses(self):
        completed = {course.code for course in self.user.classes_taken}
        completed = self._enhance_completed(completed)
        eligible = []
        for course in self.all_courses:
            if course in completed:
                continue
            prereq_groups = self.prerequisites.get(course, [])
            satisfied = True
            for group in prereq_groups:
                if not any(req in completed for req in group):
                    satisfied = False
                    break
            if satisfied:
                eligible.append(course)
        return eligible


# =============================================================================
# Utility Class: CourseGrouper
# =============================================================================
class CourseGrouper:
    """
    Provides a method to group eligible courses into
    Lower Division, Upper Division, and Electives.
    """
    @staticmethod
    def group_eligible_courses(curriculum):
        eligible_set = set(curriculum.eligible_courses)
        grouped = {"Lower Division": {}, "Upper Division": {}, "Electives": []}

        # Group Lower Division courses.
        lower_req = requirements.get("Lower_Division", {})
        for subcat, group in lower_req.items():
            subcat_list = []
            for key in ["mandatory", "additional"]:
                if key in group:
                    for course in group[key]:
                        if course in eligible_set:
                            subcat_list.append(course)
            for key in ["one_of", "plus_one_of"]:
                if key in group:
                    for alt_group in group[key]:
                        alt_eligible = [course for course in alt_group if course in eligible_set]
                        if alt_eligible:
                            alt_str = " or ".join(alt_eligible)
                            subcat_list.append(alt_str)
            if subcat_list:
                grouped["Lower Division"][subcat] = subcat_list

        # Group Upper Division courses.
        upper_req = requirements.get("Upper_Division", {})
        for subcat, group in upper_req.items():
            subcat_list = []
            for key in ["mandatory"]:
                if key in group:
                    for course in group[key]:
                        if course in eligible_set:
                            subcat_list.append(course)
            for key in ["one_of", "plus_one_of"]:
                if key in group:
                    for alt_group in group[key]:
                        alt_eligible = [course for course in alt_group if course in eligible_set]
                        if alt_eligible:
                            alt_str = " or ".join(alt_eligible)
                            subcat_list.append(alt_str)
            if subcat_list:
                grouped["Upper Division"][subcat] = subcat_list

        # Group Electives.
        elec_req = requirements.get("Electives", {})
        if elec_req:
            elective_list = elec_req.get("list", [])
            eligible_electives = [course for course in elective_list if course in eligible_set]
            if eligible_electives:
                grouped["Electives"] = eligible_electives

        return grouped


# =============================================================================
# Class: ScheduleLoader
# =============================================================================
class ScheduleLoader:
    """
    Loads a JSON file containing schedule data and extracts
    information only for eligible courses.
    """
    def __init__(self, schedule_filepath):
        self.schedule_filepath = schedule_filepath

    def get_schedule_for_eligible_courses(self, eligible_courses):
        with open(self.schedule_filepath, 'r') as f:
            schedule_data = json.load(f)
        eligible_schedule = {}
        for eligible in eligible_courses:
            # Remove spaces to create a matching pattern.
            pattern = eligible.replace(" ", "")
            for entry in schedule_data:
                # JSON field expected to start with something like "CSE12:"
                if re.match(r"{}:".format(re.escape(pattern)), entry["course"]):
                    eligible_schedule[eligible] = entry["sections"]
                    break
        return eligible_schedule


# =============================================================================
# Class: ProfessorScraper
# =============================================================================
class ProfessorScraper:
    """
    Retrieves professor information from RateMyProfessors for courses in the schedule.
    If the professor name (after cleaning) is 'staff', the scrape is skipped.
    If a professor's full name returns no data and it includes a middle name,
    the scraper retries with a shorter version (first and last name only).
    Only data for a maximum of 10 courses is scraped.
    Additionally, the 'tags' list is converted to a minimal dictionary with tag frequencies.
    """
    @staticmethod
    def scrape_professors(eligible_schedule):
        prof_data = {}
        scraped_courses = 0
        max_courses = 10  # Limit for courses to scrape

        for course, sections in eligible_schedule.items():
            prof_data[course] = {}
            # Enforce max course scraping limit.
            if scraped_courses >= max_courses:
                print(f"\nMax course scrape limit reached. Skipping scraping for course {course}.")
                for section in sections:
                    prof_data[course][section] = None
                continue

            scraped_courses += 1
            for section, professor_name in sections.items():
                # Clean professor name: remove any text within parentheses.
                clean_name = re.sub(r'\s*\(.*?\)', '', professor_name).strip()
                if clean_name.lower() == "staff":
                    print(f"\nSkipping web scrape for professor '{clean_name}' (Course {course}, Section {section})...")
                    prof_data[course][section] = None
                    continue

                print(f"\nScraping info for Professor '{clean_name}' (Course {course}, Section {section})...")
                prof_info = get_professor_info(clean_name)

                # If nothing is found and name contains a middle name, retry with first and last name only.
                if not prof_info:
                    name_parts = clean_name.split()
                    if len(name_parts) >= 3:
                        short_name = f"{name_parts[0]} {name_parts[-1]}"
                        print(f"No data with full name '{clean_name}'. Retrying with '{short_name}'...")
                        prof_info = get_professor_info(short_name)

                # Convert tags list into a dictionary of tag frequencies.
                if prof_info and "tags" in prof_info:
                    tag_counts = {}
                    for tag in prof_info["tags"]:
                        tag_counts[tag] = tag_counts.get(tag, 0) + 1
                    prof_info["tags"] = tag_counts

                prof_data[course][section] = prof_info

        return prof_data

# =============================================================================
# Class: Application
# =============================================================================
class Application:
    """
    Orchestrates the flow: parsing the transcript PDF, checking curriculum
    requirements, loading schedule data, and scraping professor information.
    """
    def __init__(self):
        self.schedule_filepath = "courses_2025_Fall25.json"
        self.state = {}

    def run(self):

        # -------------------------
        # Parse the Transcript.
        # -------------------------
        pdf_file = input("Enter the PDF file path: ")
        transcript_parser = TranscriptParser(pdf_file)
        user = transcript_parser.parse_user()
    
        # Add user information to the state
        self.state["user"] = {
            "name": user.name,
            "gpa": user.gpa,
            "credits_taken": user.credits_taken,
            "courses_taken": [str(course) for course in user.classes_taken]
        }

        # -------------------------
        # Analyze Curriculum Requirements.
        # -------------------------
        curriculum = CurriculumRequirements(user, requirements, prerequisites, all_courses)
        print("\n----- Remaining Curriculum Requirements -----")
        rem = curriculum.remaining_requirements
        if rem:
            for cat, reqs in rem.items():
                print(f"{cat}:")
                for subcat, missing in reqs.items():
                    print(f"  {subcat}: {missing}")
        else:
            print("All requirements satisfied!")

        print("\n----- Eligible Courses to Take Next (Flat List) -----")
        eligibles = curriculum.eligible_courses
        if eligibles:
            for c in eligibles:
                print(f"- {c}")
        else:
            print("No courses available (or prerequisites not met).")

        grouped = CourseGrouper.group_eligible_courses(curriculum)
        print("\n----- Eligible Courses Grouped by Category -----\n")
        if grouped["Lower Division"]:
            print("LOWER DIVS:")
            for subcat, courses in grouped["Lower Division"].items():
                for course_line in courses:
                    print(f"- {course_line}")
                print()  # Blank line between subcategories
        if grouped["Upper Division"]:
            print("UPPER DIVS:")
            for subcat, courses in grouped["Upper Division"].items():
                for course_line in courses:
                    print(f"- {course_line}")
                print()
        if grouped["Electives"]:
            print("ELECTIVES:")
            for course in grouped["Electives"]:
                print(f"- {course}")

        # -------------------------
        # Load Schedule Data.
        # -------------------------
        schedule_loader = ScheduleLoader(self.schedule_filepath)
        eligible_schedule_info = schedule_loader.get_schedule_for_eligible_courses(curriculum.eligible_courses)
        self.state["eligible_schedule"] = eligible_schedule_info

        print("\n----- Eligible Courses Schedule Info -----\n")
        if eligible_schedule_info:
            for course, sections in eligible_schedule_info.items():
                print(f"{course}:")
                for section, professor in sections.items():
                    print(f"  {section}: {professor}")
        else:
            print("No matching schedule info found for eligible courses.")

        # -------------------------
        # Scrape Professor Information.
        # -------------------------
        self.state["professors"] = ProfessorScraper.scrape_professors(eligible_schedule_info)
        print("\n----- Professor Information -----\n")
        for course, sections in self.state["professors"].items():
            print(f"{course}:")
            for section, info in sections.items():
                if info is not None:
                    print(f"  {section}: {info}")
                else:
                    print(f"  {section}: No data found or web scraping skipped (staff or limit reached).")
        
        shared_state.update(self.state)
        print("\nState updated:", shared_state.get())  # Debug print
        
        # -------------------------
        # Optionally, call any additional schedule extraction if needed.
        # -------------------------
        extract_course_data(2025, "Fall25", 0)


# =============================================================================
# Main Entry Point
# =============================================================================
if __name__ == '__main__':
    app = Application()
    app.run()
