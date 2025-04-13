import re
from pypdf import PdfReader

# ------------------------
# PART 1: PDF Text Extraction and Transcript Parsing
# ------------------------

def print_pdf_content_as_text(pdf_path):
    """Open the PDF and return its full text."""
    reader = PdfReader(pdf_path)
    textdata = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            textdata += text
    return textdata

# Define basic User and Course classes.
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
        courses_str = "\n".join([f"- {course}" for course in self.classes_taken])
        return (f"User: {self.name}\n"
                f"Credits Taken: {self.credits_taken}\n"
                f"GPA: {self.gpa}\n"
                f"Courses Taken:\n{courses_str}")

class Course:
    def __init__(self, code, quarter, credits):
        self.code = code      # e.g., "CSE 12", "MATH 19A", etc.
        self.quarter = quarter
        self.credits = credits

    def __str__(self):
        return f"{self.code} - {self.quarter} ({self.credits} credits)"

# ------------------------------------------------------------------------------
# PART 2: Curriculum Requirements and Allowed Courses
# ------------------------------------------------------------------------------

# Requirements based on the official plan.
requirements = {
    "Lower_Division": {
        "Computer_Science_and_Engineering": {
            "mandatory": ["CSE 12", "CSE 16", "CSE 20", "CSE 30", "CSE 40"],
            "additional": ["CSE 13S"]
        },
        "Mathematics": {
            # Must complete one of these two pairs:
            "one_of": [
                ["MATH 19A", "MATH 19B"],
                ["MATH 20A", "MATH 20B"]
            ]
        },
        "Applied_Mathematics": {
            # For Applied Math, only one course is needed.
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

# Define allowed courses for the official plan.
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

# ------------------------------------------------------------------------------
# Updated Prerequisites Dictionary
# ------------------------------------------------------------------------------
# (Do not edit the course names or prerequisites themselves.)
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
    # Updated AM 30: (AM 10 or MATH 21) and MATH 19B.
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
# Remove any prerequisites entries not in allowed courses.
prerequisites = {k: v for k, v in prerequisites.items() if k in allowed_courses}

# ------------------------------------------------------------------------------
# PART 3: CurriculumRequirements Class Definition
# ------------------------------------------------------------------------------
class CurriculumRequirements:
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
        """
        Enhance the set of completed courses by auto-adding prerequisites.
          - If CSE 30 is taken, mark CSE 20 as satisfied.
          - If MATH 19B is taken, mark MATH 19A as satisfied.
          - If MATH 20B is taken, mark MATH 20A as satisfied.
          - If MATH 21 is taken, add AM 10; if AM 10 is taken, add MATH 21.
          - Similarly for MATH 23A and AM 30.
        """
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
        # Enhance the completed set based on equivalencies.
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

# ------------------------------------------------------------------------------
# PART 4: Categorizing Eligible Courses for a Nice Printout
# ------------------------------------------------------------------------------

def group_eligible_courses(curriculum):
    """
    Build a dictionary that groups eligible courses (by their codes)
    into "Lower Division", "Upper Division", and "Electives" based on the
    'requirements' structure.
    
    For requirement groups that are "one_of" or "plus_one_of" (i.e. alternatives),
    if more than one eligible option exists, join them with " or ".
    """
    eligible_set = set(curriculum.eligible_courses)
    grouped = {"Lower Division": {}, "Upper Division": {}, "Electives": []}
    
    # Process Lower Division groups.
    lower_req = requirements.get("Lower_Division", {})
    for subcat, group in lower_req.items():
        subcat_list = []
        # For "mandatory" and "additional" lists.
        for key in ["mandatory", "additional"]:
            if key in group:
                for course in group[key]:
                    if course in eligible_set:
                        subcat_list.append(course)
        # For alternative requirements ("one_of" and "plus_one_of").
        for key in ["one_of", "plus_one_of"]:
            if key in group:
                for alt_group in group[key]:
                    # Get all courses from the alternative that are eligible.
                    alt_eligible = [course for course in alt_group if course in eligible_set]
                    if alt_eligible:
                        # Join alternatives with " or ".
                        alt_str = " or ".join(alt_eligible)
                        subcat_list.append(alt_str)
        if subcat_list:
            grouped["Lower Division"][subcat] = subcat_list

    # Process Upper Division groups.
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

    # Process Electives.
    elec_req = requirements.get("Electives", {})
    if elec_req:
        elective_list = elec_req.get("list", [])
        eligible_electives = [course for course in elective_list if course in eligible_set]
        if eligible_electives:
            grouped["Electives"] = eligible_electives

    return grouped

# ------------------------------------------------------------------------------
# PART 5: Main Transcript Parsing, Curriculum Check, and Grouped Output
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    pdf_file = input("Enter the PDF file path: ")
    text = print_pdf_content_as_text(pdf_file)
    
    # Extract student's name.
    name_match = re.search(r"Name:\s*(.+)", text)
    full_name = name_match.group(1).strip() if name_match else "Unknown"
    if full_name == "Unknown":
        print("Error: Unable to extract student's name.")
    
    user = User(name=full_name)
    
    # Parse course lines.
    current_quarter = None
    lines = text.splitlines()
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
            # Only process if the course is in our allowed list.
            if course_code not in allowed_courses:
                continue
            credits = float(c_match.group(2))
            course = Course(code=course_code, quarter=current_quarter, credits=credits)
            user.add_course(course)
    
    # Extract cumulative GPA and credits.
    cum_matches = re.findall(r'Cum GPA\s+([\d.]+).*?Cum Totals\s+([\d.]+)', text, flags=re.DOTALL)
    if cum_matches:
        last_gpa, last_credits = cum_matches[-1]
        user.gpa = float(last_gpa)
        user.credits_taken = float(last_credits)
    else:
        print("Error: Unable to extract cumulative GPA and credit totals.")
    
    print("----- Transcript Extracted -----")
    print(user)
    
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
    
    # Now print the eligible courses grouped by category.
    grouped = group_eligible_courses(curriculum)
    
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
